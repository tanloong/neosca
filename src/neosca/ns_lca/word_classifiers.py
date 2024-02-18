#!/usr/bin/env python3

import string


class Abstract_Word_Classifier:
    def __init__(self, word_data: dict, easy_word_threshold: int) -> None:
        self.word_dict = word_data["word_dict"]
        self.adj_dict = word_data["adj_dict"]
        self.verb_dict = word_data["verb_dict"]
        self.noun_dict = word_data["noun_dict"]
        self.word_ranks = sorted(self.word_dict.keys(), key=lambda w: self.word_dict[w], reverse=True)
        self.easy_words = self.word_ranks[:easy_word_threshold]

    def is_(self, class_: str, lemma: str, pos: str) -> bool:
        if hasattr(self, f"is_{class_}"):
            return getattr(self, f"is_{class_}")(lemma, pos)
        else:
            raise ValueError(f"Invalid class: {class_}")


class UD_Word_Classifier(Abstract_Word_Classifier):
    def is_misc(self, lemma: str, pos: str) -> bool:
        if pos in ("PUNCT", "SYM", "SPACE"):
            return True
        # https://universaldependencies.org/u/pos/X.html
        if pos == "X" and not lemma.isalpha():
            return True
        return False

    def is_sword(self, lemma: str, pos: str) -> bool:
        # sophisticated word
        return lemma not in self.easy_words and pos != "NUM"

    def is_noun(self, lemma: str, pos: str) -> bool:
        # UD    |PTB
        # ------|--------
        # NOUN  |NN, NNS
        # PROPN |NNP,NNPS
        return pos in ("NOUN", "PROPN")

    def is_adj(self, lemma: str, pos: str) -> bool:
        return pos == "ADJ"

    def is_adv(self, lemma: str, pos: str) -> bool:
        if pos != "ADV":
            return False
        if lemma in self.adj_dict:
            return True
        if lemma.endswith("ly") and lemma[:-2] in self.adj_dict:
            return True
        return False

    def is_verb(self, lemma: str, pos: str) -> bool:
        # Don't have to filter auxiliary verbs, because the VERB tag covers
        # main verbs (content verbs) but it does not cover auxiliary verbs and
        # verbal copulas (in the narrow sense), for which there is the AUX tag.
        #  https://universaldependencies.org/u/pos/VERB.html
        return pos == "VERB"


class PTB_Word_Classifier(Abstract_Word_Classifier):
    def is_verb(self, lemma: str, pos: str) -> bool:
        if not pos.startswith("V"):
            return False
        if lemma in ("be", "have"):
            return False
        return True

    def is_misc(self, lemma: str, pos: str) -> bool:
        if lemma.isspace():
            return True
        if pos[0] in string.punctuation:
            return True
        if pos in ("SENT", "SYM", "HYPH"):
            return True
        return False

    def is_sword(self, lemma: str, pos: str) -> bool:
        return lemma not in self.easy_words and pos != "CD"

    def is_noun(self, lemma: str, pos: str) -> bool:
        return pos.startswith("N")

    def is_adj(self, lemma: str, pos: str) -> bool:
        return pos.startswith("J")

    def is_adv(self, lemma: str, pos: str) -> bool:
        if not pos.startswith("R"):
            return False
        if lemma in self.adj_dict:
            return True
        if lemma.endswith("ly") and lemma[:-2] in self.adj_dict:
            return True
        return False
