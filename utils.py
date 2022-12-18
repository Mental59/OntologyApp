import string
from nltk.stem.snowball import SnowballStemmer
from nltk.util import ngrams
import nltk
import re
import random

STEMMER = SnowballStemmer('english', ignore_stopwords=True)


def remove_punctuation(text: str):
    return text.translate(str.maketrans('', '', string.punctuation))


def stem_word(word: str):
    return STEMMER.stem(word)


def extract_ngrams(text: str, num: int):
    n_grams = ngrams(nltk.word_tokenize(text), num)
    return [' '.join(grams) for grams in n_grams]


def safe_index(lst: list, value):
    try:
        return lst.index(value)
    except ValueError:
        return -1


def in_text(s: str, sentence: str):
    match = re.search(rf"\b{re.escape(s)}\b", sentence, flags=re.IGNORECASE)
    if match:
        return True
    return False


def count_in_text(s: str, sentence: str):
    return len(re.findall(rf"\b{re.escape(s)}\b", sentence, flags=re.IGNORECASE))


def random_hex_color():
    return ("#%06x" % random.randint(0, 0xFFFFFF)).upper()
