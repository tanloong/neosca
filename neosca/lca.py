import json
from math import log, sqrt
import os.path as os_path
import random
import string
import sys

# adjust minimum sample size here
standard = 50


# Returns the keys of dictionary d sorted by their values
def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort()
    return [backitems[i][1] for i in range(0, len(backitems))]


# NDW for first z words in a sample
def get_ndw_first_z(z, lemma_lst):
    ndw_first_z_types = {}
    for lemma in lemma_lst[:z]:
        ndw_first_z_types[lemma] = 1
    return len(ndw_first_z_types)


# NDW expected random z words, 10 trials
def get_ndw_erz(z, lemma_lst):
    ndw_erz = 0
    for _ in range(10):
        erz_lemma_lst = random.sample(lemma_lst, z)

        ndw_erz_types = set(erz_lemma_lst)
        ndw_erz += len(ndw_erz_types)
    return ndw_erz / 10.0


# NDW expected random sequences of z words, 10 trials
def get_ndw_esz(z, lemma_lst):
    ndw_esz = 0
    for _ in range(10):
        start_word = random.randint(0, len(lemma_lst) - z)
        esz_lemma_lst = lemma_lst[start_word : start_word + z]

        ndw_esz_types = set(esz_lemma_lst)
        ndw_esz += len(ndw_esz_types)
    return ndw_esz / 10.0


# MSTTR
def get_msttr(z, lemma_lst):
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


def is_letter_number(character) -> bool:
    if character in string.printable and character not in string.punctuation:
        return True
    return False


def is_sentence(line) -> bool:
    for character in line:
        if is_letter_number(character):
            return True
    return False


with open("data/bnc_all_filtered.json", "r", encoding="utf-8") as f:
    data = json.load(f)
word_dict = data["word_dict"]
adj_dict = data["adj_dict"]
verb_dict = data["verb_dict"]
noun_dict = data["noun_dict"]

word_ranks = sort_by_value(word_dict)
easy_words = word_ranks[-2000:]

# input file is output of morph
filename = sys.argv[1]

with open(filename, "r", encoding="utf-8") as f:
    lemlines = f.readlines()

filename = os_path.basename(filename)

# process input file
word_count_map = {}
sword_count_map = {}
lex_count_map = {}
slex_count_map = {}
verb_count_map = {}
sverb_count_map = {}
adj_count_map = {}
adv_count_map = {}
noun_count_map = {}

lemma_lst = []

for lemline in lemlines:
    lemline = lemline.lower().strip()

    if not is_sentence(lemline):
        continue

    lemmas = lemline.split()
    for lemma in lemmas:
        word, *_, pos = lemma.split("_")
        if pos in ("sent", "sym") or pos in string.punctuation:
            continue

        lemma_lst.append(word)
        word_count_map[word] = word_count_map.get(word, 0) + 1

        if (word not in easy_words) and pos != "cd":
            sword_count_map[word] = sword_count_map.get(word, 0) + 1

        if pos[0] == "n":
            lex_count_map[word] = lex_count_map.get(word, 0) + 1
            noun_count_map[word] = noun_count_map.get(word, 0) + 1

            if word not in easy_words:
                slex_count_map[word] = slex_count_map.get(word, 0) + 1
        elif pos[0] == "j":
            lex_count_map[word] = lex_count_map.get(word, 0) + 1
            adj_count_map[word] = adj_count_map.get(word, 0) + 1
            if word not in easy_words:
                slex_count_map[word] = slex_count_map.get(word, 0) + 1
        elif pos[0] == "r" and (
            (word in adj_dict) or (word[-2:] == "ly" and (word[:-2] in adj_dict))
        ):
            lex_count_map[word] = lex_count_map.get(word, 0) + 1
            adv_count_map[word] = adv_count_map.get(word, 0) + 1
            if word not in easy_words:
                slex_count_map[word] = slex_count_map.get(word, 0) + 1
        elif pos[0] == "v" and word not in ("be", "have"):
            verb_count_map[word] = verb_count_map.get(word, 0) + 1
            lex_count_map[word] = lex_count_map.get(word, 0) + 1
            if word not in easy_words:
                sverb_count_map[word] = sverb_count_map.get(word, 0) + 1
                slex_count_map[word] = slex_count_map.get(word, 0) + 1

word_type_nr = len(word_count_map)
word_token_nr = sum(count for count in word_count_map.values())

sword_type_nr = len(sword_count_map)
sword_token_nr = sum(count for count in sword_count_map.values())

lex_type_nr = len(lex_count_map)
lex_token_nr = sum(count for count in lex_count_map.values())

slex_type_nr = len(slex_count_map)
slex_token_nr = sum(count for count in slex_count_map.values())

verb_type_nr = len(verb_count_map)
verb_token_nr = sum(count for count in verb_count_map.values())

sverb_type_nr = len(sverb_count_map)
sverb_token_nr = sum(count for count in sverb_count_map.values())

adj_type_nr = len(adj_count_map)
adj_token_nr = sum(count for count in adj_count_map.values())

adv_type_nr = len(adv_count_map)
adv_token_nr = sum(count for count in adv_count_map.values())

noun_type_nr = len(noun_count_map)
noun_token_nr = sum(count for count in noun_count_map.values())

lemma_nr = len(lemma_lst)

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

# 3.1 NDW, may adjust the values of "standard"
ndw = ndwz = ndwerz = ndwesz = word_type_nr
if lemma_nr >= standard:
    ndwz = get_ndw_first_z(standard, lemma_lst)
    ndwerz = get_ndw_erz(standard, lemma_lst)
    ndwesz = get_ndw_esz(standard, lemma_lst)

# 3.2 TTR
msttr = ttr = word_type_nr / word_token_nr
if lemma_nr >= standard:
    msttr = get_msttr(standard, lemma_lst)
cttr = word_type_nr / sqrt(2 * word_token_nr)
rttr = word_type_nr / sqrt(word_token_nr)
logttr = log(word_type_nr) / log(word_token_nr)
uber = (log(word_token_nr, 10) * log(word_token_nr, 10)) / log(word_token_nr / word_type_nr, 10)

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

sys.stdout.write(
    "filename, wordtypes, swordtypes, lextypes, slextypes, wordtokens, swordtokens, lextokens,"
    " slextokens, ld, ls1, ls2, vs1, vs2, cvs1, ndw, ndwz, ndwerz, ndwesz, ttr, msttr, cttr,"
    " rttr, logttr, uber, lv, vv1, svv1, cvv1, vv2, nv, adjv, advv, modv\n"
)

output = filename
for measure in (
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
):
    output += ", " + str(round(measure, 2))
sys.stdout.write(output)
