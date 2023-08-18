import argparse
import logging
from math import log, sqrt
import os.path as os_path
import random
import string
import sys
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

from .scaio import SCAIO
from .scaprint import color_print, get_yes_or_no
from .util import SCAProcedureResult


class LCAUI:
    def __init__(self) -> None:
        self.args_parser: argparse.ArgumentParser = self.create_args_parser()
        self.options: argparse.Namespace = argparse.Namespace()

        self.is_spacy_initialized: bool = False
        self.nlp_spacy: Optional[Callable] = None

    def create_args_parser(self) -> argparse.ArgumentParser:
        args_parser = argparse.ArgumentParser(
            prog="nsca-lca", formatter_class=argparse.RawDescriptionHelpFormatter
        )
        args_parser.add_argument(
            "--wordlist",
            dest="wordlist",
            choices=("bnc", "anc"),
            default="bnc",
            help=(
                "Choose BNC or ANC (American National Corpus) wordlist for lexical"
                ' sophistication analysis. The default is "bnc".'
            ),
        )
        return args_parser

    def parse_args(self, argv: List[str]) -> SCAProcedureResult:
        options, ifile_list = self.args_parser.parse_known_args(argv[1:])
        logging.basicConfig(format="%(message)s", level=logging.INFO)

        self.verified_ifiles = SCAIO.get_verified_ifile_list(ifile_list)
        self.init_kwargs = {"wordlist": options.wordlist}
        self.options = options
        return True, None

    def install_spacy_model(self) -> SCAProcedureResult:
        import subprocess
        from subprocess import CalledProcessError

        command = [sys.executable, "-m", "pip", "install", "en_core_web_sm"]
        try:
            subprocess.run(command, check=True, capture_output=False)
        except CalledProcessError as e:
            return False, f"Failed to install spaCy: {e}"
        return True, None

    def check_spacy_model(self):
        try:
            import en_core_web_sm  # type: ignore # noqa: F401 'en_core_web_sm' imported but unused
        except ModuleNotFoundError:
            is_install = get_yes_or_no(
                "Running LCA requires spaCy. Do you want me to install it?"
            )
            if not is_install:
                return (
                    False,
                    (
                        "spaCy installation refused. You need to manually install it using:"
                        "\npip install spacy"
                        "\npython -m spacy download en_core_web_sm"
                    ),
                )
            return self.install_spacy_model()
        else:
            color_print("OKGREEN", "ok", prefix="spaCy has already been installed. ")

    def run_tmpl(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            sucess, err_msg = self.check_spacy_model()
            if not sucess:
                return sucess, err_msg
            if not self.options.is_stdout:
                sucess, err_msg = SCAIO.is_writable(self.options.ofile_freq)
                if not sucess:
                    return sucess, err_msg
            func(self, *args, **kwargs)
            return True, None

        return wrapper

    @run_tmpl
    def run_on_ifiles(self) -> SCAProcedureResult:
        analyzer = LCA(**self.init_kwargs)
        analyzer.run_on_ifiles(self.verified_ifiles)
        return True, None

    def run(self) -> SCAProcedureResult:
        return self.run_on_ifiles()


class LCA:
    def __init__(self, wordlist: str) -> None:
        # adjust minimum sample size here
        self.standard = 50
        self.scaio = SCAIO()

        assert wordlist in ("bnc", "anc")
        wordlist_datafile_map = {
            "bnc": "bnc_all_filtered.pickle.lzma",
            "anc": "anc_all_count.pickle.lzma",
        }
        data_dir = os_path.join(os_path.dirname(__file__), "data")
        datafile = os_path.join(data_dir, wordlist_datafile_map[wordlist])
        data = self.scaio.load_pickle_lzma_file(datafile)

        word_dict = data["word_dict"]
        adj_dict = data["adj_dict"]
        verb_dict = data["verb_dict"]
        noun_dict = data["noun_dict"]
        word_ranks = self._sort_by_value(word_dict)
        easy_words = word_ranks[-2000:]

        self.word_dict = word_dict
        self.adj_dict = adj_dict
        self.verb_dict = verb_dict
        self.noun_dict = noun_dict
        self.word_ranks = word_ranks
        self.easy_words = easy_words

    def _sort_by_value(self, d):
        """Returns the keys of dictionary d sorted by their values"""
        items = d.items()
        backitems = [[v[1], v[0]] for v in items]
        backitems.sort()
        return [backitems[i][1] for i in range(0, len(backitems))]

    def get_ndw_first_z(self, z, lemma_lst):
        """NDW for first z words in a sample"""
        ndw_first_z_types = {}
        for lemma in lemma_lst[:z]:
            ndw_first_z_types[lemma] = 1
        return len(ndw_first_z_types)

    def get_ndw_erz(self, z, lemma_lst):
        """NDW expected random z words, 10 trials"""
        ndw_erz = 0
        for _ in range(10):
            erz_lemma_lst = random.sample(lemma_lst, z)

            ndw_erz_types = set(erz_lemma_lst)
            ndw_erz += len(ndw_erz_types)
        return ndw_erz / 10.0

    def get_ndw_esz(self, z, lemma_lst):
        """NDW expected random sequences of z words, 10 trials"""
        ndw_esz = 0
        for _ in range(10):
            start_word = random.randint(0, len(lemma_lst) - z)
            esz_lemma_lst = lemma_lst[start_word : start_word + z]

            ndw_esz_types = set(esz_lemma_lst)
            ndw_esz += len(ndw_esz_types)
        return ndw_esz / 10.0

    def get_msttr(self, z, lemma_lst):
        samples = 0
        msttr = 0.0
        while len(lemma_lst) >= z:
            samples += 1
            msttr_types = {}
            for lemma in lemma_lst[:z]:
                msttr_types[lemma] = 1
            msttr += len(msttr_types) / z
            lemma_lst = lemma_lst[z:]
        return msttr / samples

    def run_on_ifile(
        self,
        filepath: str,
    ):
        easy_words = self.easy_words
        adj_dict = self.adj_dict
        # verb_dict = self.verb_dict
        # noun_dict = self.noun_dict

        text = self.scaio.read_txt(filepath)
        if text is None:
            return None
        g = self.get_lemma_pos_tuple(text)
        # Universal POS tags: https://universaldependencies.org/u/pos/

        lemma_count_map: Dict[str, int] = {}
        slemma_count_map: Dict[str, int] = {}
        lex_count_map: Dict[str, int] = {}
        slex_count_map: Dict[str, int] = {}
        verb_count_map: Dict[str, int] = {}
        sverb_count_map: Dict[str, int] = {}
        adj_count_map: Dict[str, int] = {}
        adv_count_map: Dict[str, int] = {}
        noun_count_map: Dict[str, int] = {}
        for lemma, pos in g:
            if pos in ("SENT", "SYM", "X") or pos in string.punctuation:
                continue

            lemma_count_map[lemma] = lemma_count_map.get(lemma, 0) + 1

            if (lemma not in easy_words) and pos != "NUM":
                slemma_count_map[lemma] = slemma_count_map.get(lemma, 0) + 1

            if pos == "NOUN":
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                noun_count_map[lemma] = noun_count_map.get(lemma, 0) + 1

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
            elif pos[0] == "ADJ":
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                adj_count_map[lemma] = adj_count_map.get(lemma, 0) + 1

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
            elif pos[0] == "ADV" and (
                (lemma in adj_dict) or (lemma.endswith("ly") and lemma[:-2] in adj_dict)
            ):
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1
                adv_count_map[lemma] = adv_count_map.get(lemma, 0) + 1

                if lemma not in easy_words:
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
            elif pos[0] == "VERB" and lemma not in ("be", "have"):
                verb_count_map[lemma] = verb_count_map.get(lemma, 0) + 1
                lex_count_map[lemma] = lex_count_map.get(lemma, 0) + 1

                if lemma not in easy_words:
                    sverb_count_map[lemma] = sverb_count_map.get(lemma, 0) + 1
                    slex_count_map[lemma] = slex_count_map.get(lemma, 0) + 1
        res = self.compute(
            lemma_count_map,
            slemma_count_map,
            lex_count_map,
            slex_count_map,
            verb_count_map,
            sverb_count_map,
            adj_count_map,
            adv_count_map,
            noun_count_map,
        )
        sys.stdout.write(
            "filename, wordtypes, swordtypes, lextypes, slextypes, wordtokens, swordtokens,"
            " lextokens, slextokens, ld, ls1, ls2, vs1, vs2, cvs1, ndw, ndwz, ndwerz, ndwesz,"
            " ttr, msttr, cttr, rttr, logttr, uber, lv, vv1, svv1, cvv1, vv2, nv, adjv, advv,"
            " modv\n"
        )
        sys.stdout.write(f"{filepath},")
        sys.stdout.write(",".join(str(round(value, 4)) for value in res))
        sys.stdout.write("\n")

    def compute(
        self,
        lemma_count_map,
        slemma_count_map,
        lex_count_map,
        slex_count_map,
        verb_count_map,
        sverb_count_map,
        adj_count_map,
        adv_count_map,
        noun_count_map,
    ):
        word_type_nr = len(lemma_count_map)
        word_token_nr = sum(count for count in lemma_count_map.values())
        lemma_lst = []
        for lemma, count in lemma_count_map.item():
            lemma_lst.extend([lemma] * count)
        lemma_nr = word_token_nr

        sword_type_nr = len(slemma_count_map)
        sword_token_nr = sum(count for count in slemma_count_map.values())

        lex_type_nr = len(lex_count_map)
        lex_token_nr = sum(count for count in lex_count_map.values())

        slex_type_nr = len(slex_count_map)
        slex_token_nr = sum(count for count in slex_count_map.values())

        verb_type_nr = len(verb_count_map)
        verb_token_nr = sum(count for count in verb_count_map.values())

        sverb_type_nr = len(sverb_count_map)
        # sverb_token_nr = sum(count for count in sverb_count_map.values())

        adj_type_nr = len(adj_count_map)
        # adj_token_nr = sum(count for count in adj_count_map.values())

        adv_type_nr = len(adv_count_map)
        # adv_token_nr = sum(count for count in adv_count_map.values())

        noun_type_nr = len(noun_count_map)
        noun_token_nr = sum(count for count in noun_count_map.values())

        # 1. lexical density
        ld = lex_token_nr / word_token_nr

        # 2. lexical sophistication
        # 2.1 lexical sophistication
        ls1 = slex_token_nr / lex_token_nr
        ls2 = sword_type_nr / word_type_nr

        # 2.2 verb sophistication
        vs1 = sverb_type_nr / verb_token_nr
        vs2 = (sverb_type_nr**2) / verb_token_nr
        cvs1 = sverb_type_nr / sqrt(2 * verb_token_nr)

        # 3 lexical diversity or variation

        # 3.1 NDW, may adjust the values of "self.standard"
        ndw = ndwz = ndwerz = ndwesz = word_type_nr
        if lemma_nr >= self.standard:
            ndwz = self.get_ndw_first_z(self.standard, lemma_lst)
            ndwerz = self.get_ndw_erz(self.standard, lemma_lst)
            ndwesz = self.get_ndw_esz(self.standard, lemma_lst)

        # 3.2 TTR
        msttr = ttr = word_type_nr / word_token_nr
        if lemma_nr >= self.standard:
            msttr = self.get_msttr(self.standard, lemma_lst)
        cttr = word_type_nr / sqrt(2 * word_token_nr)
        rttr = word_type_nr / sqrt(word_token_nr)
        logttr = log(word_type_nr) / log(word_token_nr)
        uber = (log(word_token_nr, 10) * log(word_token_nr, 10)) / log(
            word_token_nr / word_type_nr, 10
        )

        # 3.3 verb diversity
        vv1 = verb_type_nr / verb_token_nr
        svv1 = verb_type_nr * verb_type_nr / verb_token_nr
        cvv1 = verb_type_nr / sqrt(2 * verb_token_nr)

        # 3.4 lexical diversity
        lv = lex_type_nr / lex_token_nr
        vv2 = verb_type_nr / lex_token_nr
        nv = noun_type_nr / noun_token_nr
        adjv = adj_type_nr / lex_token_nr
        advv = adv_type_nr / lex_token_nr
        modv = (adv_type_nr + adj_type_nr) / lex_token_nr

        return (
            word_type_nr,
            sword_type_nr,
            lex_type_nr,
            slex_type_nr,
            word_token_nr,
            sword_token_nr,
            lex_token_nr,
            slex_token_nr,
            ld,
            ls1,
            ls2,
            vs1,
            vs2,
            cvs1,
            ndw,
            ndwz,
            ndwerz,
            ndwesz,
            ttr,
            msttr,
            cttr,
            rttr,
            logttr,
            uber,
            lv,
            vv1,
            svv1,
            cvv1,
            vv2,
            nv,
            adjv,
            advv,
            modv,
        )

    def run_on_ifiles(self, ifiles: List[str]):
        for ifile in ifiles:
            self.run_on_ifile(ifile)

    def ensure_spacy_initialized(func: Callable):  # type:ignore
        def wrapper(self, *args, **kwargs):
            if self.nlp_spacy is None:
                logging.info("Initializing spaCy...")
                import spacy  # type: ignore

                self.nlp_spacy = spacy.load("en_core_web_sm", enable=["tagger", "lemmatizer"])

            return func(self, *args, **kwargs)

        return wrapper

    @ensure_spacy_initialized
    def get_lemma_pos_tuple(self, text: str) -> Generator[Tuple[str, str], Any, None]:
        doc = self.nlp_spacy(text)  # type:ignore
        for token in doc:
            yield (token.lemma_, token.pos_)


def lca_main() -> None:
    ui = LCAUI()
    success, err_msg = ui.parse_args(sys.argv)
    if not success:
        logging.critical(err_msg)
        sys.exit(1)
    success, err_msg = ui.run()
    if not success:
        logging.critical(err_msg)
        sys.exit(1)


if __name__ == "__main__":
    lca_main()
