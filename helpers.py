# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
import string
from string import ascii_lowercase
from subprocess import Popen, PIPE
import sys
import os
import random
import re
import string
import sys
import tkinter as tk
import tkinter.ttk as ttk
from itertools import groupby
# from logging import exception
# from string import ascii_lowercase
from subprocess import Popen, PIPE
from tkinter import messagebox

import customtkinter as ctk

import outcomedrilling
from fmwm import debug_mode
from logging import exception
from itertools import groupby



gc_z = [0] * 28

def get_word_list_path_name(local_path_file_name: str, critical: bool = True) -> str:
    """Return the full path to a Wordle word-list file.

    :param local_path_file_name: Path to the word-list file, relative to this module.
    :param critical:             If True, show an error dialog and exit when the file
                                 is not found. If False, show a warning and return ''.
    :return:                     Absolute path to the file, or '' if not found and
                                 critical is False.
    """
    full_path = os.path.join(os.path.dirname(__file__), local_path_file_name)
    if os.path.exists(full_path):
        return full_path

    if critical:
        msg = (f'The wordle word list file {local_path_file_name} was not found.'
               f'\n\nExpected here: {full_path}')
        print(msg)
        messagebox.showerror(title='Stopping Here', message=msg)
        sys.exit()

    msg = (f'The wordle word list file {local_path_file_name} was not found.'
           f'\n\nExpected here: {full_path}'
           f'\n\nThe option using this file will not use it.')
    messagebox.showwarning(title='Will Continue', message=msg)
    return ''

"""
Letter ranking functions for rank that includes by letter position method
"""


_CLASSIC_LTR_RANK: dict = {
    'e': [44.9, 2.30, 8.12, 5.27, 16.59, 12.57],
    'a': [35.3, 5.27, 12.56, 9.38, 5.40, 2.70],
    'r': [31.4, 4.04, 8.30, 6.41, 5.08, 7.56],
    'o': [27.3, 1.58, 11.46, 7.55, 4.42, 2.29],
    'i': [25.4, 1.27, 8.84, 9.04, 5.68, 0.61],
    't': [24.7, 5.29, 2.33, 4.79, 4.61, 7.72],
    'l': [23.4, 3.41, 6.06, 4.29, 4.99, 4.68],
    's': [22.5, 11.76, 0.66, 3.02, 5.48, 1.59],
    'n': [20.5, 1.53, 3.19, 5.43, 5.95, 4.39],
    'd': [19.9, 4.14, 0.82, 3.16, 2.19, 9.57],
    'u': [17.9, 1.39, 7.66, 5.66, 3.09, 0.14],
    'y': [17.0, 0.39, 0.78, 1.04, 0.17, 14.65],
    'c': [16.8, 7.36, 1.51, 2.33, 4.54, 1.03],
    'p': [14.4, 5.55, 1.86, 2.68, 2.02, 2.31],
    'h': [13.8, 3.10, 4.80, 0.50, 1.03, 4.36],
    'm': [13.8, 4.69, 1.58, 2.90, 2.99, 1.61],
    'g': [11.4, 4.23, 0.46, 2.65, 2.65, 1.45],
    'b': [10.9, 6.53, 0.56, 2.34, 0.91, 0.54],
    'k': [8.7,  1.08, 0.39, 1.28, 2.39, 3.52],
    'f': [7.8,  4.56, 0.26, 0.98, 1.18, 0.85],
    'w': [7.4,  3.06, 1.59, 1.30, 0.85, 0.57],
    'v': [5.6,  1.56, 0.56, 2.01, 1.50, 0.00],
    'z': [1.9,  0.15, 0.05, 0.64, 0.81, 0.24],
    'x': [1.9,  0.03, 0.54, 0.80, 0.09, 0.40],
    'j': [1.3,  0.97, 0.06, 0.14, 0.11, 0.00],
    'q': [1.0,  0.77, 0.20, 0.03, 0.00, 0.00],
}


def make_ltr_rank_dictionary(local_path_rank_file: str) -> dict:
    """Build and return the letter ranking dictionary.

    Reads rankings from a file; falls back to the built-in classic ranking
    if the file is not found.

    File format — one entry per line::

        e:44.9:2.30:8.12:5.27:16.59:12.57

    where the first field is the letter, index 0 is the anywhere-rank,
    and indices 1-5 are the positional ranks.

    :param local_path_rank_file: Path to the ranking file, relative to this module.
    :return:                     Letter ranking dictionary keyed by letter;
                                 values are lists of six floats.
    """
    full_path = os.path.join(os.path.dirname(__file__), local_path_rank_file)

    if os.path.exists(full_path):
        ltr_rank_dict = {}
        with open(full_path) as f:
            for line in f:
                key, *values = line.strip().split(':')
                ltr_rank_dict[key] = [float(v) for v in values]
        return ltr_rank_dict

    msg = (f'Letter ranking file "{local_path_rank_file}" not found. '
           f'Switching to built-in classic letter ranking.')
    print(msg)
    messagebox.showwarning('Warning', message=msg)
    return _CLASSIC_LTR_RANK

def wrd_rank(wrd: str, ltr_rank_dict: dict, method: int) -> float:
    """Return a word's letter-frequency ranking.

    Words longer than 5 letters return 0 (undefined rank), allowing
    word-list flexibility.

    :param wrd:           Subject word (lowercase, max 5 letters).
    :param ltr_rank_dict: Ranking dictionary keyed by letter; each value is
                          a list where index 0 is the anywhere-rank and
                          indices 1-5 are the positional ranks.
    :param method:        0 = rank by letter occurrence (anywhere in word);
                          1 = rank by letter position;
                          2 = combined occurrence and position rank.
    :return:              Cumulative letter-frequency rank, or 0 for an
                          unrecognised method or a word longer than 5 letters.
    """
    if len(wrd) > 5:
        return 0

    letters = [(p, x) for p, x in enumerate(wrd, 1) if 'a' <= x <= 'z']

    if method == 0:
        return sum(ltr_rank_dict[x][0] for _, x in letters)
    if method == 1:
        return sum(ltr_rank_dict[x][p] for p, x in letters)
    if method == 2:
        return sum(ltr_rank_dict[x][0] + ltr_rank_dict[x][p] for p, x in letters)
    return 0


# def word_has_duplicates(wrd) -> bool:
#     """
#     Checks is a word has duplicate letters.
#     This function is also used for the special pattern
#     where '.' is allowed. These would not be duplicates.
#     @param wrd: word in question
#     @return: true=has duplicate letters, false=no duplicate letters
#     """
#     ltr_d = {}
#     wrd = wrd.replace('.', '')
#     wrd = wrd.replace(' ', '')
#     for ltr in wrd:
#         ltr_d[ltr] = ltr
#     return len(ltr_d) < len(wrd)

def word_has_duplicates(word: str) -> bool:
    """
    Checks if a word has duplicate letters.
    This function is also used for the special pattern
    where '.' is allowed. These would not be duplicates.
    '.' and ' ' characters are ignored and not treated as duplicates.

    :param word: The word to check.
    :return: True if the word has duplicate letters, False otherwise.
    """
    filtered = word.replace('.', '').replace(' ', '')
    return len(set(filtered)) < len(filtered)

def print_word_list_col_format(word_list: dict, n_col: int) -> None:
    """
    List out the ranked word list into n_col columns.

    :param word_list: Dictionary mapping words to their ranks.
    :param n_col: Number of columns to display.
    """
    col_header = "Word : Rank"
    col_sep = "   "

    print(col_sep.join([col_header] * n_col))

    items = list(word_list.items())
    for row_start in range(0, len(items), n_col):
        row_items = items[row_start:row_start + n_col]
        print(col_sep.join(f"{word} : {rank}" for word, rank in row_items))


def make_ranked_filtered_result_dictionary(
    words: list,
    ltr_rank_dict: dict,
    allow_dups: bool,
    rank_mode: int,
    no_ordr: bool,
    no_rank: bool = False,
) -> dict:
    """
    Build a ranked and filtered word dictionary.

    :param words: The filtered word list.
    :param ltr_rank_dict: Letter ranking dictionary.
    :param allow_dups: If True, include words with duplicate letters.
    :param rank_mode: Letter ranking mode to use.
    :param no_ordr: If True, sort alphabetically instead of by rank.
    :param no_rank: If True, skip ranking (e.g. for random selection).
    :return: Dictionary of words mapped to their formatted rank strings.
    """
    words_dict = {}

    for word in words:
        if not word:
            continue
        if not allow_dups and word_has_duplicates(word):
            continue
        words_dict[word] = "000" if no_rank else f"{wrd_rank(word, ltr_rank_dict, rank_mode):05.1f}"

    if no_rank:
        return words_dict

    sort_key = (lambda x: x[0]) if no_ordr else (lambda x: x[1])
    return dict(sorted(words_dict.items(), key=sort_key))



def get_results_word_list(shell_cmd) -> list:
    """
    Run the grep command pipeline and return the matched words.

    :param shell_cmd: Command object exposing a .full_cmd() shell string.
    :return: List of words that pass the grep command pipeline.
    """
    with Popen(shell_cmd.full_cmd(), shell=True, stdout=PIPE, text=True) as proc:
        return [line.rstrip('\n') for line in proc.stdout]




# def print_word_list_col_format(the_word_list, n_col):
#     """
#     List out the ranked word list into n_col columns.
#     @param the_word_list:
#     @param n_col: number of columns to fill.
#     """
#     n_items = len(the_word_list)
#     h_txt = " Word : Rank"
#     left_pad = ""
#     mid_pad = "   "
#     h_line = left_pad + h_txt
#     for i in range(1, n_col):
#         mid = ' ' * 2
#         h_line = h_line + mid + h_txt
#     print(h_line)
#     c = 0
#     i = 0
#     l_msg = ""
#     for key, value in the_word_list.items():
#         msg = key + " : " + str(value)
#         i = i + 1
#         if c == 0:
#             l_msg = left_pad + msg
#         else:
#             l_msg = l_msg + mid_pad + msg
#         c = c + 1
#         if c == n_col:
#             print(l_msg)
#             c = 0
#             l_msg = ""
#         if i == n_items:
#             print(l_msg)

def print_word_list_col_format(word_list: dict, n_col: int) -> None:
    """
    List out the ranked word list into n_col columns.

    :param word_list: Dictionary mapping words to their ranks.
    :param n_col: Number of columns to display.
    """
    col_header = "Word : Rank"
    col_sep = "   "

    print(col_sep.join([col_header] * n_col))

    items = list(word_list.items())
    for row_start in range(0, len(items), n_col):
        row_items = items[row_start:row_start + n_col]
        print(col_sep.join(f"{word} : {rank}" for word, rank in row_items))


# def make_ranked_filtered_result_dictionary(wrds: list, ltr_rank_dict: dict, allow_dups: bool,
#                                            rank_mode: int, no_ordr: bool, no_rank=False) -> dict:
#     """
#     Ranking and filtering the words into a dictionary.
#     @param wrds: The filtered words list
#     @param ltr_rank_dict: Letter ranking dictionary
#     @param allow_dups:  Allows duplicate letters bool
#     @param rank_mode: Letter ranking mode to use
#     @param no_ordr: Omit ordering bool
#     @param no_rank: Omit ranking bool
#     @return: dictionary sorted by the word rank
#     """
#     wrds_dict = {}
#     for w in wrds:
#         # currently, the wrd_rank function can handle only 5-letter words
#         # if len(w) == 5:
#         if len(w) == 0:
#             print("len 0")
#         if allow_dups:
#             # every word goes into the dictionary
#             if not no_rank:
#                 wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))
#             else:
#                 # no ranking for speed since pick will be random
#                 wrds_dict[w] = '000'
#         else:
#             # only words having no duplicates goes into the dictionary
#             if not word_has_duplicates(w):
#                 if not no_rank:
#                     wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))
#                 else:
#                     # no ranking for speed since pick will be random
#                     wrds_dict[w] = '000'
#
#     # sorting the ranked word list into a dictionary
#     if not no_rank:
#         if no_ordr:
#             return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[0]))
#         else:
#             return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))
#     else:
#         return wrds_dict

def make_ranked_filtered_result_dictionary(
    words: list,
    ltr_rank_dict: dict,
    allow_dups: bool,
    rank_mode: int,
    no_ordr: bool,
    no_rank: bool = False,
) -> dict:
    """
    Build a ranked and filtered word dictionary.

    :param words: The filtered word list.
    :param ltr_rank_dict: Letter ranking dictionary.
    :param allow_dups: If True, include words with duplicate letters.
    :param rank_mode: Letter ranking mode to use.
    :param no_ordr: If True, sort alphabetically instead of by rank.
    :param no_rank: If True, skip ranking (e.g. for random selection).
    :return: Dictionary of words mapped to their formatted rank strings.
    """
    words_dict = {}

    for word in words:
        if not word:
            continue
        if not allow_dups and word_has_duplicates(word):
            continue
        words_dict[word] = "000" if no_rank else f"{wrd_rank(word, ltr_rank_dict, rank_mode):05.1f}"

    if no_rank:
        return words_dict

    sort_key = (lambda x: x[0]) if no_ordr else (lambda x: x[1])
    return dict(sorted(words_dict.items(), key=sort_key))


# def get_results_word_list(this_sh_cmd_lst) -> list:
#     """
#     Returns the result for the grep command list.
#     @param this_sh_cmd_lst: the grep stack of command list
#     @return: Returns the list of words that pass the grep command list
#     """
#     with Popen(this_sh_cmd_lst.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
#         return list(map(lambda i: i[: -1], proc.stdout.readlines()))

def get_results_word_list(shell_cmd) -> list:
    """
    Run the grep command pipeline and return the matched words.

    :param shell_cmd: Command object exposing a .full_cmd() shell string.
    :return: List of words that pass the grep command pipeline.
    """
    with Popen(shell_cmd.full_cmd(), shell=True, stdout=PIPE, text=True) as proc:
        return [line.rstrip('\n') for line in proc.stdout]

# def get_pu_wordlist(full_path_name) -> list:
#     pu_wrds = []
#     if os.path.exists(full_path_name):
#         with open(full_path_name, 'r') as file:
#             for line in file:
#                 pu_wrds.append(line.split(',', 1)[0].lower())
#     return pu_wrds
# def get_pu_wordlist(full_path_name: str) -> list:
#     """
#     Read a word list from a CSV-style file, returning the first field of each line.
#
#     :param full_path_name: Path to the word list file.
#     :return: List of lowercase words, or an empty list if the file does not exist.
#     """
#     if not os.path.exists(full_path_name):
#         return []
#     with open(full_path_name, 'r') as file:
#         return [
#             line.split(',', 1)[0].strip().lower()
#             for line in file
#             if line.strip()
#         ]

# def get_classic_wordlist(full_path_name) -> list:
#     classic_wrds = []
#     if os.path.exists(full_path_name):
#         with open(full_path_name, 'r') as file:
#             for line in file:
#                 classic_wrds.append(line.split(',', 1)[0].lower().rstrip())
#     return classic_wrds
# def get_classic_wordlist(full_path_name: str) -> list:
#     """
#     Read a classic word list from a CSV-style file, returning the first field of each line.
#
#     :param full_path_name: Path to the word list file.
#     :return: List of lowercase words, or an empty list if the file does not exist.
#     """
#     if not os.path.exists(full_path_name):
#         return []
#     with open(full_path_name, 'r') as file:
#         return [
#             line.split(',', 1)[0].strip().lower()
#             for line in file
#             if line.strip()
#         ]

def get_wordlist(full_path_name: str) -> list:
    """
    Read a word list from a CSV-style file, returning the first field of each line.

    :param full_path_name: Path to the word list file.
    :return: List of lowercase words, or an empty list if the file does not exist.
    """
    if not os.path.exists(full_path_name):
        return []
    with open(full_path_name, 'r') as file:
        return [
            line.split(',', 1)[0].strip().lower()
            for line in file
            if line.strip()
        ]

# def cull_sol_list(s_wrds: list, p_wrds: list) -> None:
#     """
#     Culls the p_wrds list from the s_wrds list. Intended
#     for removing the previously used words from the
#     possible solutions word list.
#     :param s_wrds: total solutions wordlist
#     :param p_wrds:  previously used wordlist
#     """
#     for w in p_wrds:
#         try:
#             s_wrds.remove(w)
#         except ValueError:
#             pass
def cull_sol_list(s_wrds: list, p_wrds: list) -> None:
    """
    Culls the p_wrds list from the s_wrds list. Intended
    for removing the previously used words from the
    possible solutions word list.

    :param s_wrds: Total solutions word list (modified in place).
    :param p_wrds: Previously used word list to remove.
    """
    exclude = set(p_wrds)
    s_wrds[:] = [w for w in s_wrds if w not in exclude]

def clear_scrn() -> None:
    """
    Clears the console window
    """
    os.system("cls" if os.name == "nt" else "clear")


def get_gencode(word: str) -> list:
    """
    Return the genetic code for a word as a 28-element integer list.

    Indices 0–25: 1 if the letter is present, 0 otherwise.
    Index 26: excess occurrence count — sum of (appearances − 1) for each
              repeated letter. e.g. "woody" → 1 (o×2), "toott" → 3 (o×2, t×3).
    Index 27: genetic rank, calculated externally and defaulting to 0.

    Example — "woody":
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0]

    :param word: The word to encode.
    :return: 28-element list encoding letter presence, duplicate count, and rank.
    """
# def get_gencode(word) -> list:
#     """
#     Return a word's genetic code
#     example:woody
#     returns:[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0]
#     translated: idx 0-25 'abc...xyz' letter count, idx 26 duplicates count, idx 27 genetic rank.
#     Rank applies in the title_context for a list of words, so it is calculated later
#     @param word: a word in question
#     @return: a special list of ints that encode the genetic code
#     """
#     # gencode is the list of integers that will be returned
#     gencode = gc_z.copy()
#     # dups counts the number of times letters occur more than once.
#     # In woody the letter o occurs 1 time more than once. dups = 1
#     # In toott the letter o occurs 1 time more than once. The letter t
#     # occurs 2 times more han once. dups = 1 + 2 = 3
#     dups = 0
#     # loop through each letter in the word
#     for ltr in word:
#         idx = ord(ltr) - 97
#         # Increment dups if that letter has already been seen.
#         if gencode[idx] > 0:
#             dups += 1
#         # Mark that letter as having been seen.
#         gencode[idx] = 1
#     gencode[26] = dups
#     return gencode

def get_gencode(word: str) -> list:
    """
    Return the genetic code for a word as a 28-element integer list.

    Indices 0–25: 1 if the letter is present, 0 otherwise.
    Index 26: excess occurrence count — sum of (appearances − 1) for each
              repeated letter. e.g. "woody" → 1 (o×2), "toott" → 3 (o×2, t×3).
    Index 27: genetic rank, calculated externally and defaulting to 0.

    Example — "woody":
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0]

    :param word: The word to encode.
    :return: 28-element list encoding letter presence, duplicate count, and rank.
    """
    gencode = gc_z.copy()
    dups = 0
    for ltr in word:
        idx = ord(ltr) - ord('a')
        if gencode[idx] > 0:
            dups += 1
        gencode[idx] = 1
    gencode[26] = dups
    return gencode


# def get_gendict_tally(gendict: dict[str, list]) -> list:
#     """
#     returns genetic letter tally list for a gendictionary, (dict[str, list])
#     this list is 26 members where each member corresponds to the count for
#     that letter position idx 0-25 where idx 0=a and idx 25=z
#     @param gendict:
#     @return:
#     """
#     gen_tally = []
#     for x in range(26):
#         gen_tally.append(0)
#     # loop through each gencode values list
#     for gencode in gendict.values():
#         # looking at just the list's a...z letter presence value,
#         # add them up
#         for idx in range(26):
#             if gencode[idx] > 0:
#                 gen_tally[idx] = gen_tally[idx] + gencode[idx]
#     return gen_tally

def get_gendict_tally(gendict: dict[str, list]) -> list:
    """
    Return the letter presence tally across all words in a gen-dictionary.

    Each position 0–25 in the returned list corresponds to a letter ('a'–'z')
    and holds the total count of words in which that letter is present.

    :param gendict: Dictionary mapping words to their gencode lists.
    :return: 26-element list of per-letter presence counts.
    """
    gen_tally = [0] * 26
    for gencode in gendict.values():
        for idx in range(26):
            gen_tally[idx] += gencode[idx]
    return gen_tally

def dict_gen_tally(gt: list, cnt: int) -> dict[str, float]:
    """
    Convert a letter tally list into a sorted letter-frequency dictionary.

# def dict_gen_tally(gt: list, cnt: int) -> dict:
#     lf_dict: dict[str, float] = {}
#     s = 97
#     for lcnt in gt:
#         if lcnt:
#             lc_ltr = chr(s)
#             if not lc_ltr in lf_dict:
#                 lf_dict.update({lc_ltr: lcnt / cnt})
#         s = s + 1
#     s_lf_dict = dict(sorted(lf_dict.items(), key=lambda item: item[1], reverse=True))
#     return s_lf_dict

def dict_gen_tally(gt: list, cnt: int) -> dict[str, float]:
    """
    Convert a letter tally list into a sorted letter-frequency dictionary.

    :param gt: 26-element letter tally list (index 0='a' … 25='z').
    :param cnt: Total word count used to compute relative frequencies.
    :return: Dictionary mapping letters to their frequency (tally / cnt),
             sorted by frequency descending.
    """
    lf_dict: dict[str, float] = {}
    for i, tally in enumerate(gt):
        if tally:
            lf_dict[chr(ord('a') + i)] = tally / cnt
    return dict(sorted(lf_dict.items(), key=lambda item: item[1], reverse=True))

# def assign_genrank(gendict: dict[str, list], gen_tally: list) -> int:
#     """
#     Places the product sums of gendict values and the gen_tally vector. This value is
#     the genetic rank for the gendict words (the keys). The genetic rank is injected into
#     the gendict value vector as the 27th item of the 1 x 27 value vector. The maximum
#     genetic rank calculated is the integer being returned.
#     @param gendict: dictionary of words (keys) with values being 1 x 27 letter count vectors
#     @param gen_tally: 1 x 26 vector of letter tallies
#     @return: maximum genetic rank seen as integer
#     """
#     maxrank = 0
#     for w, g in gendict.items():
#         gr = 0
#         for idx in range(26):
#             gr = gr + g[idx] * gen_tally[idx]
#         gr = gr + g[26]
#         new_g = g
#         new_g[27] = gr
#         if gr > maxrank:
#             maxrank = gr
#         gendict.update({w: new_g})
#     return maxrank

def assign_genrank(gendict: dict[str, list], gen_tally: list) -> int:
    """
    Compute and assign the genetic rank for each word in gendict in place.

    The rank is the dot product of the word's letter-presence vector (indices 0–25)
    with gen_tally, plus the word's duplicate-letter count (index 26).
    The rank is written to index 27 of each word's gencode vector.

    :param gendict: Dictionary mapping words to their 28-element gencode vectors.
    :param gen_tally: 26-element letter tally vector.
    :return: Maximum genetic rank across all words.
    """
    maxrank = 0
    for g in gendict.values():
        g[27] = sum(g[i] * gen_tally[i] for i in range(26)) + g[26]
        maxrank = max(maxrank, g[27])
    return maxrank

def get_maxgenrankers(gendict: dict[str, list], maxrank: int) -> list[str]:
    """
    Return all words in gendict whose genetic rank equals maxrank.

    :param gendict: Dictionary mapping words to their 28-element gencode vectors.
    :param maxrank: The maximum genetic rank to filter by.
    :return: List of words whose gencode rank (index 27) equals maxrank.
    """
    return [w for w, g in gendict.items() if g[27] == maxrank]

def regex_maxgenrankers(max_rankers: list[str], wordsdict: dict) -> str:
    """
    Build a regex alternation pattern string for highlighting max-ranked words.

    Each alternative is formatted as "word : rank".

    :param max_rankers: List of top-ranked words.
    :param wordsdict: Dictionary mapping words to their rank strings.
    :return: Pipe-delimited regex alternation string of "word : rank" entries.
    """
    return '|'.join(f"{w} : {wordsdict[w]}" for w in max_rankers)

def analyze_pick_to_solution(sol_wrd: str, pick: str, excl_lst: list, x_pos_dict: dict,
                             r_pos_dict: dict):
    """
    This function is used by fmwm.py only. This function determines what and how a guess
    matches against a target solution. The parameters returned are used to grep filter the
    current remaining word list to be the next remaining word list according to how the guess
    compares to the solution.
    
    Updates the exclude, exclude position, include position and multi filtering according to
    what a pick looks like against the solution word.
    @param sol_wrd: The target solution
    @param pick: The guess word.
    @param excl_lst: The letters to be excluded. (ie gray clues)
    @param x_pos_dict: The letters excluded from a position (ie yellow clues)
    @param r_pos_dict: The letters required at a position (ie green clues)
    multi_code:str The multiple same letters and how many code (like 2A,3E)
    @return: [excl_lst: list, x_pos_dict: dict, r_pos_dict:dict, multi_code:str]
    """
    p_ltr_pos: int = 0  # Current letter position in the pick
    # Multiple same letter accounting is required to filter for multiple same letter
    # instances when they are called for. The user is expected to make that determination
    # in the GUI pywt.py. That determination needs to be coded for fmwm.py.
    for p_ltr in pick:
        # First check for a p_ltr instance.
        if sol_wrd.find(p_ltr) < 0:
            # p_ltr has no matches
            # This must be a GRAY letter.
            if not excl_lst.__contains__(p_ltr):
                excl_lst.append(p_ltr)
            # done with this letter
            # keep track of the index position
            p_ltr_pos += 1
            continue
        # If here, then p_ltr has at least one instance.
        # value = key in the position dictionaries, so just make the key.
        key = p_ltr + ',' + str(p_ltr_pos + 1)
        # Decide into which dictionary: x-clude or r-equire to place this key/value pair,
        # also make the multiple same letter accounting
        if p_ltr_pos == sol_wrd.find(p_ltr, p_ltr_pos):
            # This must be a GREEN clue
            # Add p_ltr and p_ltr's position to the required position dictionary.
            r_pos_dict[key] = key
        else:
            # This must be a YELLOW clue
            # Add p_ltr and p_ltr's position to the exclude position dictionary.
            x_pos_dict[key] = key
        # keep track of index position
        p_ltr_pos += 1
    # end for
    # Handling multiple same letter will be done as this afterward process that returns a dictionary of letter count
    # and include/exclude mode.

    mult_dict = mult_ltr_dict(pick, sol_wrd, r_pos_dict)

    return [excl_lst, x_pos_dict, r_pos_dict, mult_dict]


def letter_counts(word: str) -> dict:
    """
    Used by only fmwm.py
    Returns a dictionary holding the instance counts for the letters
    withing the word argument.
    :param word: str
    :return:
    """
    lc_dict: dict[str, int] = {}
    for w_ltr in word:
        if w_ltr in lc_dict:
            lc_dict[w_ltr] = lc_dict[w_ltr] + 1
        else:
            lc_dict[w_ltr] = 1
    return lc_dict


def is_include_necessary(r_pos_dict: dict, gl: str, tc: int) -> bool:
    """
    Used by only fmwm.py
    Used for the multiple letter include grep line where the current required letter at position
    dictionary does not inherently require the gc number of gl letters.
    :param tc: guess letter count in question
    :param gl: guess letter in question
    :type r_pos_dict: dict Required letter at position dictionary
    :rtype: bool
    """
    gl_cnt = 0
    for key in r_pos_dict:
        if key[0] == gl:
            gl_cnt = gl_cnt + 1
    r = not (gl_cnt == tc)
    return r


def mult_ltr_dict(guess: str, target: str, r_pos_dict: dict) -> dict:
    """
    Returns the requirements for handling multiple same letters
    Used by only fmwm.py
    :param guess: guess candidate word
    :param target: solution word
    :param r_pos_dict: required letter at position dictionary
    :return: dict; multiple letter with count needing exclusion or inclusion
    key is the letter and its count, value is the mode 1=include, 2=exclude
    """
    lc_guess = letter_counts(guess)
    lc_target = letter_counts(target)
    mult_dict: dict[str, int] = {}
    for gl, gc in lc_guess.items():
        if gc == 1:
            # Multiple exclude or include cannot be determined
            continue
        if gc > 1:
            # Quess has multiple same letter. This letter would be excluded or required by earlier code
            # but if required then an xgL require or exclude might be necessary.
            tc = None
            if gl in lc_target:
                tc = lc_target[gl]
            match tc:
                case None:
                    # gl would have been excluded by prior code
                    continue
                case 1:
                    # target has 1
                    if gc == 2:
                        # target has 1, guess has 2
                        # Exclude 2gl
                        key = f"{str(gc)}{gl}"
                        mode_value = 2  # exclude
                        mult_dict[key] = mode_value
                case 2:
                    # target has 2, guess has 2 or 3
                    if gc == 2:
                        # target has 2, guess has 2
                        # Include 2gl, but only if both guess gl are NOT green since
                        # the prior require dict would cover the grep requirement.
                        if is_include_necessary(r_pos_dict, gl, tc):
                            key = f"2{gl}"
                            mode_value = 1  # include
                            mult_dict[key] = mode_value
                    if gc == 3:
                        # target has 2, guess has 3
                        # Exclude 3gl
                        key = f"3{gl}"
                        mode_value = 2  # exclude
                        mult_dict[key] = mode_value
                        # Include 2gl, but only if both guess gl are NOT green since
                        # the prior require dict would cover the grep requirement.
                        if is_include_necessary(r_pos_dict, gl, tc):
                            key = f"2{gl}"
                            mode_value = 1  # include
                            mult_dict[key] = mode_value
                case 3:
                    # target has 3, guess has 2 or 3
                    if gc == 2:
                        # target has 3, guess has 2
                        # Include 2gl, but only if both guess gl are NOT green since
                        # the prior require dict would cover the grep requirement.
                        if is_include_necessary(r_pos_dict, gl, tc):
                            key = f"2{gl}"
                            mode_value = 1  # include
                            mult_dict[key] = mode_value
                    if gc == 3:
                        # target has 3, guess has 3
                        # Include 3gl, but only if all 3 guess gl are NOT green since
                        # the prior require dict would cover the grep requirement.
                        if is_include_necessary(r_pos_dict, gl, gc):
                            key = f"3{gl}"
                            mode_value = 1  # include
                            mult_dict[key] = mode_value
    return mult_dict

def build_x_pos_grep(self, this_pos_dict: dict, rq_lts: str) -> None:
    """
    Build grep exclusion commands for each letter-position pair in this_pos_dict.

    Example: entry "b,3" produces grep -vE '..b..'

    :param this_pos_dict: Dict of exclusion entries; each value is "letter,position" (e.g. "b,3").
    :param rq_lts: String of letters already marked as required.
    """
    for _, entry in sorted(this_pos_dict.items()):
        ltr, pos = entry.split(',')
        ltr = ltr.lower()
        already_required = ltr in rq_lts
        self.tool_command_list.add_excl_pos_cmd(ltr, int(pos), not already_required)
        if not already_required:
            rq_lts += ltr

def build_r_pos_grep(self, this_pos_dict: dict) -> str:
    """
    Build a grep inclusion pattern for required letter positions.

    Example: entries (b, 3) and (a, 5) produce pattern '..b.a'.

    :param this_pos_dict: Dict of inclusion entries; each value is "letter,position" (e.g. "b,3").
    :return: The grep pattern string, or '' if this_pos_dict is empty.
    """
    if not this_pos_dict:
        return ''

    pat = ['.'] * 5
    for entry in this_pos_dict.values():
        ltr, p_str = entry.split(',')
        pat[int(p_str) - 1] = ltr.lower()

    result = ''.join(pat)
    self.tool_command_list.add_type_cmd(result, True)
    return result

def build_multi_code_grep(lself, multi_code: dict) -> None:
    """
    used only by fmwm.py
    It is here that add_type_mult_ltr_cmd must be sent for each
    multi_code entry with the correct require/excluse argument. Otherwise, Only a letter require
    is sent regardless of what it should be.
    """
    for mltr, mode in multi_code.items():
        lself.tool_command_list.add_type_mult_ltr_cmd(mltr.lower(), mode)


def load_grep_arguments(wordle_tool_cmd_lst, excl_l: list, requ_l: list, x_pos_dict: dict,
                        r_pos_dict: dict, multi_code: dict) -> None:
    """
    Build and load filter grep commands into the shell command list.

    :param wordle_tool_cmd_lst: The shell command list object.
    :param excl_l: Letters to exclude.
    :param requ_l: Letters to require.
    :param x_pos_dict: Excluded letter-position dictionary.
    :param r_pos_dict: Required letter-position dictionary.
    :param multi_code: Coded multiple same-letter dictionary.
    """
    tcl = wordle_tool_cmd_lst.tool_command_list

    if excl_l:
        tcl.add_cmd(f"grep -vE '{'|'.join(excl_l)}'")

    if requ_l:
        tcl.add_cmd("| ".join(f"grep -E '{ltr}'" for ltr in requ_l))

    build_x_pos_grep(wordle_tool_cmd_lst, x_pos_dict, "".join(requ_l))
    build_r_pos_grep(wordle_tool_cmd_lst, r_pos_dict)

    if multi_code:
        build_multi_code_grep(wordle_tool_cmd_lst, multi_code)

# def get_genpattern(subject_word: str, target_word: str) -> str:
#     """
#     Return a subject word's genetic pattern against a target guess word
#     example:heavy against leash is the string 12200 pattern
#     @param subject_word: The word to check against the guess word.
#     @param target_word: The guess word
#     @return: String pattern representing each digit in the subject word where
#     0 = letter not present, 1 = letter present but not this position and
#     2 = letter present at correct position
#     """
#     ltr_pos = [0, 1, 2, 3, 4]
#     genpat = '00000'
#
#     # dictionary of subject sltr instances in target. sltr is key, value is sltr positions
#     subj_in_target_dict = {}
#     for sltr in subject_word:
#         subj_in_target = ([pos for pos, char in enumerate(target_word) if char == sltr])
#         if subj_in_target:
#             subj_in_target_dict[sltr] = subj_in_target
#
#     rec_pos = ltr_pos.copy()
#     # first find all ltr matches, mark as 2s and remove their positions
#     # from rec_pos and the subject_in_target dictionary
#     for slp in ltr_pos:
#         sl = subject_word[slp]
#         if subject_word[slp] == target_word[slp]:
#             genpat = genpat[:slp] + '2' + genpat[slp + 1:]
#             rec_pos.remove(slp)
#             subj_in_target_dict[sl].remove(slp)
#             if not subj_in_target_dict[sl]:
#                 subj_in_target_dict.pop(sl)
#
#     # rec_pos now holds only the positions needing further examination
#     for slp in rec_pos:
#         sl = subject_word[slp]
#         if sl in subj_in_target_dict:
#             genpat = genpat[:slp] + '1' + genpat[slp + 1:]
#             subj_in_target_dict[sl].pop(0)
#             if not subj_in_target_dict[sl]:
#                 subj_in_target_dict.pop(sl)
#
#     return genpat

def get_genpattern(subject_word: str, target_word: str) -> str:
    """
    Return the genetic pattern of subject_word compared against target_word.

    Each character in the returned string represents one position:
      '2' = correct letter at correct position
      '1' = letter present but at wrong position
      '0' = letter not present

    Example: 'heavy' against 'leash' → '12200'

    :param subject_word: The word to evaluate.
    :param target_word: The guess word to compare against.
    :return: 5-character pattern string of '0', '1', and '2'.
    """
    pattern = ['0'] * 5

    # Track positions in target where each subject letter appears
    subj_in_target = {
        ltr: [i for i, ch in enumerate(target_word) if ch == ltr]
        for ltr in set(subject_word)
        if ltr in target_word
    }

    # First pass: exact matches (2s), build list of remaining positions
    unmatched = []
    for i, (sl, tl) in enumerate(zip(subject_word, target_word)):
        if sl == tl:
            pattern[i] = '2'
            subj_in_target[sl].remove(i)
            if not subj_in_target[sl]:
                del subj_in_target[sl]
        else:
            unmatched.append(i)

    # Second pass: present but wrong position (1s)
    for i in unmatched:
        sl = subject_word[i]
        if sl in subj_in_target:
            pattern[i] = '1'
            subj_in_target[sl].pop(0)
            if not subj_in_target[sl]:
                del subj_in_target[sl]

    return ''.join(pattern)


def outcomes_for_this_guess(guess_word: str, word_list: list) -> dict[str, list]:
    """
    Group words from word_list by the genpattern they produce against guess_word.

    Returns a dictionary of the word outcomes the guess_word would result
    from applying the guess_word on the word_list. The key values will be
    five-digit codes where 0 means letter is not present, 1 letter is present
    but at wrong position and 2 means letter is present and in correct position.

    :param guess_word: The guess word to evaluate against.
    :param word_list: List of subject words to categorise.
    :return: Dict mapping 5-digit pattern strings to lists of matching words.
             Pattern digits: '0' = absent, '1' = present but wrong position,
             '2' = present at correct position.
    """
    outcomes: dict[str, list] = {}
    for subject_word in word_list:
        genpat = get_genpattern(guess_word, subject_word)
        outcomes.setdefault(genpat, []).append(subject_word)
    return outcomes


def get_outcomes_stats(the_outcomes_dict: dict, meta_l: bool = False) -> tuple[
        int, int, int, float, float, float, float, int, int, int]:
    """
    Compute statistics for a single guess's outcome dictionary.
    Given a single guess's outcome dictionary, returns stats:
    outcome pattern quantity,
    smallest outcome pattern size,
    largest outcome pattern size,
    average outcome pattern size,
    outcome population variance,
    outcome entropy,
    outcome expected size

    :param the_outcomes_dict: Outcome dictionary mapping pattern strings to word lists.
    :param meta_l: If True, tally clue-digit counts (0/1/2) weighted by group size.
    :return: Tuple of (qty, smallest, largest, mean, variance, entropy, expected_size,
             cnt_0, cnt_1, cnt_2).
    """
    items = [(k, len(v)) for k, v in the_outcomes_dict.items()]
    sizes = [size for _, size in items]

    g_qty = len(sizes)
    total = sum(sizes)
    mean = total / g_qty

    p2 = g_ent = g_xa = 0.0
    cnt_0 = cnt_1 = cnt_2 = 0
    for k, size in items:
        p2 += (size - mean) ** 2
        i_p = size / total
        g_ent -= i_p * math.log(i_p, 2)
        g_xa += size * i_p
        # tally the clue types if meta_lr is True
        # (Presumably pressing the meta key to the spacebar left.)
        if meta_l:
            cnt_0 += k.count('0') * size
            cnt_1 += k.count('1') * size
            cnt_2 += k.count('2') * size
    p2 /= g_qty

    return g_qty, min(sizes), max(sizes), mean, p2, g_ent, g_xa, cnt_0, cnt_1, cnt_2

    return g_qty, min(sizes), max(sizes), mean, p2, g_ent, g_xa, cnt_0, cnt_1, cnt_2


# def outcomes_stat_summary(best_rank_dict: dict) -> tuple[int, int, int, float, float, float, float]:
#     """
#     Summarizes the outcomes best_rank_dictionary, mainly to extract the
#     minimum and maximum outcome sizes
#     @param best_rank_dict:
#     @return: outcomes_stat_summary tuple:
#     [0]:qty,[1]:smallest,[2]:largest,[3]:average,
#     [4]:population variance,[5]:entropy bits,all as a tuple
#     """
#     # The outcome_stats for each best_rank_dict member are:
#     # [0]:qty, [1]:smallest, [2]:largest, [3]:average, [4]:population variance and [5]:entropy bits as tuple parts
#     # Each member is 'best' because they have the maximum found grps_qty as the [0]:qty.
#     # The 'best' are equal in grps_qty and average but could have varying
#     # [2]:largest values and thus varying [4]:population variance values and [5] entropy bits
#     # BTW, optimal_rank ([3]:average) in this function is an old name. It is not always optimal.
#     #
#     # This function's purpose, outcomes_stat_summary, it to summarize the outcome stats in all the found
#     # best words that have their outcome stats contained by the best_rank_dictionary for reporting outcome
#     # optimal words. The summary report is for noticing when better word selections exist. Because an outcome stat
#     # largest outcome count ([2]:largest) identifies a better selection within the best_rank_dictionary the
#     # max_grp_size this function reports will actually be the minimum of the [3]:largest present in the
#     # best_rank_dictionary. This is where we get the minimum of the maximums (min_max) idea. This is a subtlety
#     # noticed occasionally where some word selections among words all having the same grps_qty could be better
#     # because they have more balanced word outcome sizes, ie smaller population variance. Perhaps they also happen
#     # to be from the list showing. These selections would be harder to spot when the summary reports the max outcome
#     # size instead of the min_max outcome size.
#     g_stats = best_rank_dict[list(best_rank_dict.keys())[0]]
#     optimal_rank = g_stats[3]
#     grps_qty = g_stats[0]
#     min_grp_size = g_stats[2]  # Seed with a member's largest
#     max_grp_size = g_stats[2]  # The min_max is desired. Seed with a member's largest
#     min_grp_p2 = g_stats[4]  # Seed with member's variance
#     max_grp_ent = 0.0
#     min_grp_xa = g_stats[6]  # Seed with member's expected average
#     for g_stats in best_rank_dict.values():
#         (_, min_stat, max_stat, _, p2_stat, e_stat, xa_stat, cnt_0, cnt_1, cnt_2) = g_stats
#         min_grp_size = min(min_stat, min_grp_size)
#         max_grp_size = min(max_stat, max_grp_size)  # The min_max is desired.
#         min_grp_p2 = min(p2_stat, min_grp_p2)
#         max_grp_ent = max(max_grp_ent, e_stat)
#         min_grp_xa = min(min_grp_xa, xa_stat)
#         # outcomes_stat_summary are:[0]:qty,[1]:smallest,[2]:largest,[3]:average,
#         # [4]:min p2,[5]:max entropy bit, [6] expected outcome size,
#         # [7] cnt_0, [8] cnt_1, [9] cnt_2 as a tuple
#     return grps_qty, min_grp_size, max_grp_size, optimal_rank, min_grp_p2, max_grp_ent, min_grp_xa

def outcomes_stat_summary(best_rank_dict: dict) -> tuple[int, int, int, float, float, float, float]:
    """
    Summarise outcome stats across all entries in best_rank_dict, mainly to extract the
    minimum and maximum outcome sizes

    All entries share the same group count and mean, but may differ in their largest
    group size, variance, and entropy. Group size is reported as the min-of-maximums
    (min_max) — the minimum of each entry's largest group size — to surface more
    balanced word selections within the best set.

    :param best_rank_dict: Dict mapping words to their outcome stat tuples.
    :return: Tuple of (qty, min_smallest, min_max_largest, mean,
             min_variance, max_entropy, min_expected_size).
    """
    # The outcome_stats for each best_rank_dict member are:
    # [0]:qty, [1]:smallest, [2]:largest, [3]:average, [4]:population variance and [5]:entropy bits as tuple parts
    # Each member is 'best' because they have the maximum found grps_qty as the [0]:qty.
    # The 'best' are equal in grps_qty and average but could have varying
    # [2]:largest values and thus varying [4]:population variance values and [5] entropy bits
    # BTW, optimal_rank ([3]:average) in this function is an old name. It is not always optimal.
    #
    # This function's purpose, outcomes_stat_summary, it to summarize the outcome stats in all the found
    # best words that have their outcome stats contained by the best_rank_dictionary for reporting outcome
    # optimal words. The summary report is for noticing when better word selections exist. Because an outcome stat
    # largest outcome count ([2]:largest) identifies a better selection within the best_rank_dictionary the
    # max_grp_size this function reports will actually be the minimum of the [3]:largest present in the
    # best_rank_dictionary. This is where we get the minimum of the maximums (min_max) idea. This is a subtlety
    # noticed occasionally where some word selections among words all having the same grps_qty could be better
    # because they have more balanced word outcome sizes, ie smaller population variance. Perhaps they also happen
    # to be from the list showing. These selections would be harder to spot when the summary reports the max outcome
    # size instead of the min_max outcome size.
    first = next(iter(best_rank_dict.values()))
    grps_qty     = first[0]
    mean         = first[3] # formerly was optimal rank
    min_grp_size = first[1] # Seed with a member's largest
    max_grp_size = first[2] # The min_max is desired. Seed with a member's largest
    min_grp_p2   = first[4] # Seed with member's variance
    max_grp_ent  = first[5]
    min_grp_xa   = first[6] # Seed with member's expected average

    for g_stats in best_rank_dict.values():
        _, min_stat, max_stat, _, p2_stat, e_stat, xa_stat, *_ = g_stats
        min_grp_size = min(min_grp_size, min_stat)
        max_grp_size = min(max_grp_size, max_stat)  # min_max: prefer smaller largest group
        min_grp_p2   = min(min_grp_p2, p2_stat)
        max_grp_ent  = max(max_grp_ent, e_stat)
        min_grp_xa   = min(min_grp_xa, xa_stat)

    return grps_qty, min_grp_size, max_grp_size, mean, min_grp_p2, max_grp_ent, min_grp_xa

    for g_stats in best_rank_dict.values():
        _, min_stat, max_stat, _, p2_stat, e_stat, xa_stat, *_ = g_stats
        min_grp_size = min(min_grp_size, min_stat)
        max_grp_size = min(max_grp_size, max_stat)  # min_max: prefer smaller largest group
        min_grp_p2   = min(min_grp_p2, p2_stat)
        max_grp_ent  = max(max_grp_ent, e_stat)
        min_grp_xa   = min(min_grp_xa, xa_stat)

    return grps_qty, min_grp_size, max_grp_size, mean, min_grp_p2, max_grp_ent, min_grp_xa


# def extended_best_outcomes_guess_dict(remaining_word_lst: list, reporting: bool, byentonly: bool,
#                                       cond_rpt: bool, keyed_rpt: bool,
#                                       guess_targets: dict,
#                                       report_header_msg1: str, title_context: str, meta_l=False) -> dict:
#     """
#     Wraps guess word outcome ranking to return the best
#     outcome rank guesses. Guesses resulting in more outcomes
#     and smaller outcomes are better guesses.
#     @param remaining_word_lst: the remaining solutions word list
#     @param reporting: flag for verbose printing to rptwnd
#     @param byentonly: flag to return only the highest entropy guesses
#     @param cond_rpt: flag for condensed verbose printing to rptwnd
#     @param keyed_rpt: flag for keyed by word verbose printing to rptwnd
#     @param guess_targets: guess vocabulary dictionary
#     @param report_header_msg1: msg string put in verbose report header
#     @param title_context: String used in title so indicate owner
#     @return: dictionary of the best outcome ranked guesses
#     """
#     guess_rank_dict = {}
#     best_rank_dict = {}
#     cond_dict = {}
#     min_score = len(remaining_word_lst)
#     max_ent = 0.0
#     rptwnd = RptWnd(title_context)
#     rptwnd.withdraw()
#
#     if reporting:
#         rptwnd.deiconify()
#         reporting_header_to_window(report_header_msg1, guess_targets, rptwnd)
#
#     for guess in guess_targets:
#         guess_outcomes_dict = outcomes_for_this_guess(guess, remaining_word_lst)
#         # outcome_stats are: [0]:qty, [1]:smallest, [2]:largest,
#         # [3]:average , [4]:population variance , [5]:entropy as a tuple
#         outcome_stats = get_outcomes_stats(guess_outcomes_dict, meta_l)
#
#         if reporting:
#             clue_pattern_outcomes_to_window(guess, outcome_stats, guess_outcomes_dict, rptwnd, cond_rpt, keyed_rpt)
#             # saving the condensed stats for later sorting
#             if cond_rpt:
#                 cond_dict[guess] = outcome_stats
#                 # omit the 'For:' in the search control
#                 rptwnd.search_text.set('')
#
#         # This function has changed over time. Its purpose is to return a best_stat_dict of guess
#         # words and their stats sorted by the best rank. Guesses having the most outcomes tend to
#         # result in smaller outcomes. However, within guesses having the same number of outcomes,
#         # the guesses with smaller maximum outcomes or guesses with more evenly distributed
#         # outcomes tend to be better than their brethren. Outcome entropy measures that quality.
#         #
#         # Here the guesses' average outcome size (essentially outcome qty) is used as the rank
#         # criteria while also keeping track of the guess having the maximum entropy. Then the
#         # ranked guess dictionary is sorted by entropy. This pulls the best equal outcome qty
#         # words to the top and, if there are actually lesser outcome qty guesses with the higher
#         # entropy, puts the single best word at the dictionary top.
#         #
#         # It is understood this function does not list all the best guesses in order, but does
#         # but the best at the top. It is also understood entropy only approximates the
#         # expected number of steps to solve.
#         #
#         guess_rank_dict[guess] = outcome_stats
#         # Record the smallest outcome pattern average size. (essentially max outcome qty)
#         min_score = min(outcome_stats[3], min_score)
#         # Record the maximum entropy seen
#         max_ent = max(outcome_stats[5], max_ent)
#
#     # Populate the best_rank_dict with the best guesses.
#     # This dictionary's values are outcome_stats tuples.
#     for g, s in guess_rank_dict.items():
#         # if not only by entropy, then include all with
#         # minimum average outcome size (max outcome size)
#         if not byentonly:
#             if math.isclose(s[3], min_score):
#                 if g not in best_rank_dict:
#                     best_rank_dict[g] = s
#         # Also collect the max_ent instances, these are not
#         # always with max outcome size.
#         if math.isclose(s[5], max_ent):
#             if g not in best_rank_dict:
#                 best_rank_dict[g] = s
#
#     # make a new dict that is best_rank_dict sorted by ent size
#     inorder_best_rank_dict = dict(sorted(best_rank_dict.items(), key=lambda item: item[1][5], reverse=True))
#     # Reporting only the best ranking guesses.
#     if reporting:
#         report_footer_wrapper(report_header_msg1, remaining_word_lst, inorder_best_rank_dict, rptwnd, cond_rpt)
#         if cond_rpt:
#             report_sorted_cond_guess_stats_to_window(cond_dict, rptwnd, keyed_rpt, meta_l)
#
#     return inorder_best_rank_dict

def extended_best_outcomes_guess_dict(remaining_word_lst: list, reporting: bool, byentonly: bool,
                                      cond_rpt: bool, keyed_rpt: bool,
                                      guess_targets: dict,
                                      report_header_msg1: str, title_context: str,
                                      meta_l: bool = False) -> dict:
    """
    Find and return the best outcome-ranked guess words from guess_targets.

    Guesses producing more outcomes (and therefore smaller outcomes) rank higher.
    Within equal outcome counts, guesses with higher entropy — more evenly distributed
    outcome sizes — are preferred. The returned dict is sorted by entropy descending,
    putting the best candidate at the top.

    :param remaining_word_lst: The remaining solutions word list.
    :param reporting: If True, print verbose output to rptwnd.
    :param byentonly: If True, return only the highest-entropy guesses.
    :param cond_rpt: If True, use condensed verbose output format.
    :param keyed_rpt: If True, use keyed-by-word verbose output format.
    :param guess_targets: Guess vocabulary dictionary.
    :param report_header_msg1: Message string placed in the verbose report header.
    :param title_context: String used in the window title to indicate owner.
    :param meta_l: If True, include clue-digit tallies in outcome stats.
    :return: Dictionary of best outcome-ranked guesses, sorted by entropy descending.
    """
    guess_rank_dict = {}
    best_rank_dict = {}
    cond_dict = {}
    min_score = len(remaining_word_lst)
    max_ent = 0.0

    rptwnd = RptWnd(title_context)
    rptwnd.withdraw()
    if reporting:
        rptwnd.deiconify()
        reporting_header_to_window(report_header_msg1, guess_targets, rptwnd)

    for guess in guess_targets:
        # outcome_stats are: [0]:qty, [1]:smallest, [2]:largest,
        # [3]:average , [4]:population variance , [5]:entropy as a tuple
        guess_outcomes_dict = outcomes_for_this_guess(guess, remaining_word_lst)
        outcome_stats = get_outcomes_stats(guess_outcomes_dict, meta_l)

        if reporting:
            clue_pattern_outcomes_to_window(guess, outcome_stats, guess_outcomes_dict, rptwnd, cond_rpt, keyed_rpt)
            # saving the condensed stats for later sorting
            if cond_rpt:
                cond_dict[guess] = outcome_stats
                rptwnd.search_text.set('')

        # This function has changed over time. Its purpose is to return a best_stat_dict of guess
        # words and their stats sorted by the best rank. Guesses having the most outcomes tend to
        # result in smaller outcomes. However, within guesses having the same number of outcomes,
        # the guesses with smaller maximum outcomes or guesses with more evenly distributed
        # outcomes tend to be better than their brethren. Outcome entropy measures that quality.
        #
        # Here the guesses' average outcome size (essentially outcome qty) is used as the rank
        # criteria while also keeping track of the guess having the maximum entropy. Then the
        # ranked guess dictionary is sorted by entropy. This pulls the best equal outcome qty
        # words to the top and, if there are actually lesser outcome qty guesses with the higher
        # entropy, puts the single best word at the dictionary top.
        #
        # It is understood this function does not list all the best guesses in order, but does
        # but the best at the top. It is also understood entropy only approximates the
        # expected number of steps to solve.
        #

        guess_rank_dict[guess] = outcome_stats
        # Record the smallest outcome pattern average size. (essentially max outcome qty)
        min_score = min(outcome_stats[3], min_score)
        # Record the maximum entropy seen
        max_ent = max(outcome_stats[5], max_ent)

    # Populate the best_rank_dict with the best guesses.
    # This dictionary's values are outcome_stats tuples.
    for g, s in guess_rank_dict.items():
        qualifies = (not byentonly and math.isclose(s[3], min_score)) or math.isclose(s[5], max_ent)
        if qualifies:
            best_rank_dict.setdefault(g, s)

    # make a new dict that is best_rank_dict sorted by ent size
    inorder_best_rank_dict = dict(sorted(best_rank_dict.items(), key=lambda item: item[1][5], reverse=True))

    # Reporting only the best ranking guesses.
    if reporting:
        report_footer_wrapper(report_header_msg1, remaining_word_lst, inorder_best_rank_dict, rptwnd, cond_rpt)
        if cond_rpt:
            report_sorted_cond_guess_stats_to_window(cond_dict, rptwnd, keyed_rpt, meta_l)

    return inorder_best_rank_dict

def best_outcomes_from_showing_as_guess_dict(remaining_word_lst: list, reporting: bool, byentonly: bool,
                                             cond_rpt: bool, keyed_rpt: bool,
                                             title_context: str, meta_l=False) -> dict:
    """
    Wraps guess word outcomes ranking to return the best
    outcomes rank guesses. Guesses resulting in more outcomes
    and smaller outcomes are better guesses.
    @param remaining_word_lst: the remaining solutions word list
    @param reporting: flag for verbose printing to rptwnd
    @param byentonly: flag to return only the highest entropy guesses
    @param cond_rpt: flag for condensed verbose printing to rptwnd
    @param keyed_rpt: flag for keyed by word verbose printing to rptwnd
    @param title_context: String used in title to indicate owner
    @return: dictionary of the best outcomes ranked guesses where
    guess words are the keys, outcome_stats tuples are the values
    outcome_stats tuples are:
    [0]:qty,[1]:smallest,[2]:largest,[3]:average,[4]:population variance,[5]:entropy
    """
    guess_stat_dict = {}
    best_stat_dict = {}
    cond_dict = {}
    min_outcome_ave = len(remaining_word_lst)
    max_ent = 0.0
    rptwnd = RptWnd(title_context)
    rptwnd.withdraw()
    if reporting:
        rptwnd.deiconify()
        reporting_header_to_window("Words Showing", remaining_word_lst, rptwnd)

    for guess in remaining_word_lst:
        guess_outcomes_dict = outcomes_for_this_guess(guess, remaining_word_lst)
        # outcome_stats are: [0]:qty, [1]:smallest, [2]:largest, [3]:average,
        # [4]:population variance, [5]:entropy, [6] expected outcome size all as a tuple
        outcomes_stats = get_outcomes_stats(guess_outcomes_dict)

        if reporting:
            clue_pattern_outcomes_to_window(guess, outcomes_stats, guess_outcomes_dict, rptwnd, cond_rpt, keyed_rpt)
            # saving the stats for later sorting
            if cond_rpt:
                cond_dict[guess] = outcomes_stats
                # omit the 'For:' in the search control
                rptwnd.search_text.set('')

        # This function has changed over time. Its purpose is to return a best_stat_dict of guess
        # words and their stats sorted by the best rank. Guesses having the most outcomes tend to
        # result in smaller outcomes. However, within guesses having the same number of outcomes,
        # the guesses with smaller maximum outcomes or guesses with more evenly distributed
        # outcomes tend to be better than their brethren. Outcome entropy measures that quality.
        #
        # Here the guesses' average outcome size (essentially outcome qty) is used as the rank
        # criteria while also keeping track of the guess having the maximum entropy. Then the
        # ranked guess dictionary is sorted by entropy. This pulls the best equal outcome qty
        # words to the top and, if there are actually lesser outcome qty guesses with the higher
        # entropy, puts the single best word at the dictionary top.
        #
        # It is understood this function does not list all the best guesses in order, but does
        # but the best at the top. It is also understood entropy only approximates the
        # expected number of steps to solve.
        #
        guess_stat_dict[guess] = outcomes_stats
        # Record the smallest outcome pattern average size. (essentially max outcome qty)
        min_outcome_ave = min(outcomes_stats[3], min_outcome_ave)
        # Record the maximum entropy seen
        max_ent = max(outcomes_stats[5], max_ent)

    # Populate the best_stat_dict with the best guesses.
    # This dictionary's values are outcome_stats tuples.
    for g, s in guess_stat_dict.items():
        # if not only by entropy, then include all with
        # minimum average outcome size (max outcome size)
        if not byentonly:
            if math.isclose(s[3], min_outcome_ave):
                if g not in best_stat_dict:
                    best_stat_dict[g] = s
        # Also collect the max_ent instances, these are not
        # always with max outcome size.
        if math.isclose(s[5], max_ent):
            if g not in best_stat_dict:
                best_stat_dict[g] = s

    # make a new dict that is best_stat_dict sorted by ent size
    inorder_best_rank_dict = dict(sorted(best_stat_dict.items(), key=lambda item: item[1][5], reverse=True))
    # Reporting only the best ranking guesses.
    if reporting:
        report_footer_wrapper("Words Showing", remaining_word_lst, inorder_best_rank_dict, rptwnd, cond_rpt)
        if cond_rpt:
            report_sorted_cond_guess_stats_to_window(cond_dict, rptwnd, keyed_rpt, meta_l)

    return inorder_best_rank_dict


def best_entropy_outcomes_guess_dict(targets_word_lst: list, guess_word_lst: list, debug_mode: bool) -> dict:
    """
    Intended for finite moinkey use. Not used by pywt.
    Wraps guess word outcomes ranking to return the best
    outcomes entropy ranked guesses.
    @param byentonly: flag to return only the highest entropy guesses
    @param targets_word_lst: possible solution words
    @param guess_word_lst: guess words to pull guesses from
    @return: dictionary of the best outcomes ranked guesses where
    guess words are the keys, outcome_stats tuples are the values
    outcome_stats tuples are:
    [0]:qty,[1]:smallest,[2]:largest,[3]:average,[4]:population variance,[5]:entropy
    """
    guess_stat_dict = {}
    best_stats_found_dict = {}
    best_desired_dict = {}
    max_ent = 0.0
    gl_len = len(guess_word_lst)
    g_n = 0

    if debug_mode:
        print(f'Working with {len(targets_word_lst)} remaining possibles. '
              f'Pulling guesses from a {gl_len} guess list.')

    for guess in guess_word_lst:
        guess_outcomes_dict = outcomes_for_this_guess(guess, targets_word_lst)
        outcomes_stats = get_outcomes_stats(guess_outcomes_dict)
        # outcome_stats tuple is: [0]:qty, [1]:smallest, [2]:largest, [3]:average,
        # [4]:population variance, [5]:entropy, [6] expected outcome size
        # [7] cnt_0, [8] cnt_1, [9] cnt_2
        guess_stat_dict[guess] = outcomes_stats
        # animated in progress showing
        msg = '\033[K' + '> ' + guess + ' : ' + str(g_n) + ' of ' + str(gl_len) + '\r'
        sys.stdout.write(msg)
        g_n = g_n + 1

        # Record the maximum entropy seen
        max_ent = max(outcomes_stats[5], max_ent)

    # At this point, all guesses were examined and the maximum entropy
    # value recorded.

    # Populate the best_stats_found_dict with the best guesses.
    # Initially, only those guesses with the same max_ent go into
    # the dictionary.
    # This dictionary's values are outcome_stats tuples.
    # Iterate back through the guess_stat_dict to find the guesses
    # with the max_ent. There could be more than 1.
    for g, s in guess_stat_dict.items():
        if math.isclose(s[5], max_ent):
            if g not in best_stats_found_dict:
                best_stats_found_dict[g] = s
                if debug_mode:
                    print(f'Added {g} having {s} to best_stats_found_dict')

    for w in targets_word_lst:
        for g, s in best_stats_found_dict.items():
            if w == g:
                best_desired_dict[g] = s
                if debug_mode:
                    print(f'Added {g} having {s} to best_desired_dict')

    if len(best_desired_dict) > 0:
        del best_stats_found_dict
        best_stats_found_dict = best_desired_dict
        if debug_mode:
            print(f'Using only target best entropy words')

    return best_stats_found_dict


def report_footer_wrapper(msg1: str, word_lst: list, best_rank_dict: dict, rptwnd: ctk, cond_rpt: bool):
    """
    Write the full report footer sequence to rptwnd.

    :param msg1: Header message string.
    :param word_lst: Remaining solutions word list.
    :param best_rank_dict: Dictionary of best outcome-ranked guesses.
    :param rptwnd: The report window instance.
    :param cond_rpt: If True, use condensed format (skips per-word stats footer).
    """
    report_footer_summary_header_to_window(msg1, word_lst, rptwnd)
    report_footer_stats_summary_to_window(best_rank_dict, rptwnd)
    report_footer_opt_wrds_to_window(best_rank_dict, rptwnd, cond_rpt)
    if not cond_rpt:
        report_footer_optimal_wrds_stats_to_window(best_rank_dict, rptwnd)
    rptwnd.back_to_summary()

def report_footer_summary_header_to_window(msg: str, source_list: list, rptwnd: ctk) -> None:
    """
    Append the outcome summary header line to the report window.

    :param msg: Label identifying the guess word source.
    :param source_list: The word list being summarised.
    :param rptwnd: The report window instance.
    """
    rptl = f"\n\n> >  Outcome summary using the {msg} words for guesses on the {len(source_list)} words.  < <"
    rptwnd.verbose_data.insert(tk.END, rptl)

def prnt_guesses_header(rptwnd: ctk, keyed: bool = False, meta_l: bool = False) -> None:
    """
    Append the guess stats column header line to the report window.

    :param rptwnd: The report window instance.
    :param keyed: If True, prepend a 'slot' column for keyed-by-word format.
    :param meta_l: If True, append clue-digit count columns (#0, #1, #2).
    """
    cols = ['slot', 'guess'] if keyed else ['guess']
    cols += ['qty', 'ent', 'min', 'max', 'ave', 'exp', 'p2']
    if meta_l:
        cols += ['#0', '#1', '#2']
    rptwnd.verbose_data.insert(tk.END, '\n\n' + '\t'.join(cols))

def reporting_header_to_window(msg: str, source_list: list, rptwnd: ctk) -> None:
    """
    Set the report window title and append the decorated header line.

    :param msg: Label identifying the guess word source.
    :param source_list: The guess target word list.
    :param rptwnd: The report window instance.
    """
    title = f"{rptwnd.context} - Outcome Patterns For Guesses From The {msg} Words List ({len(source_list)})"
    rptwnd.title(title)
    rptwnd.verbose_data.insert(tk.END, f"> >  {title}  < <")

def report_sorted_cond_guess_stats_to_window(l_cond_dict: dict, rptwnd: ctk, keyed: bool, meta_l: bool = False) -> None:
    """
    Append condensed line-by-line guess outcome stats to the report window.

    :param l_cond_dict: Dictionary of guesses and their outcome stats.
    :param rptwnd: The report window instance.
    :param keyed: If True, group guesses into entropy slots with a slot index prefix.
    :param meta_l: If True, append clue-digit count columns to each line.
    """
    inorder_cond_dict = dict(sorted(l_cond_dict.items(), key=lambda item: item[1][5], reverse=True))
    prnt_guesses_header(rptwnd, keyed, meta_l)

    indx = 1
    c_indx_ent = None
    for g, s in inorder_cond_dict.items():
        qty, smallest, largest, average, p2, ent, g_xa, cnt_0, cnt_1, cnt_2 = s

        if keyed:
            if c_indx_ent is None:
                c_indx_ent = ent
            elif not math.isclose(ent, c_indx_ent):
                indx += 1
                c_indx_ent = ent
            prefix = f"\n{indx}\t{g}\t"
        else:
            prefix = f"\n{g}\t"

        rptl = (f"{prefix}{qty}"
                f"\t{ent:.3f}"
                f"\t{smallest}"
                f"\t{largest}"
                f"\t{average:.3f}"
                f"\t{g_xa:.2f}"
                f"\t{p2:.1f}")
        if meta_l:
            rptl += f"\t{cnt_0}\t{cnt_1}\t{cnt_2}"

        rptwnd.verbose_data.insert(tk.END, rptl)

def clue_pattern_outcomes_to_window(guess: any, outcome_stats: tuple, guess_outcomes_dict: dict,
                                    rptwnd: ctk, cond_rpt: bool, keyed_rpt: bool) -> None:
    (qty, smallest, largest, average, p2, ent, g_xa, cnt_0, cnt_1, cnt_2) = outcome_stats
    # report in full or condensed format according to cond_prt flag
    keyed_if = ''
    if keyed_rpt:
        keyed_if = guess + '  '
    if not cond_rpt:
        rptl = '\n\n' + keyed_if + '> > > > Clue pattern outcomes for: ' + guess + ' < < < < '
        rptwnd.verbose_data.insert(tk.END, rptl)
        rptl = '\n' + keyed_if + '> qty ' + str(qty) + \
               ', ent ' + '{0:.3f}'.format(ent) + \
               ", sizes: min " + str(smallest) + \
               ", max " + str(largest) + \
               ', ave ' + '{0:.2f}'.format(average) + \
               ', exp ' + '{0:.2f}'.format(g_xa) + \
               ', p2 ' + '{0:.1f}'.format(p2)

        rptwnd.verbose_data.insert(tk.END, rptl)
        rptwnd.verbose_data.insert(tk.END, '\n')
        for key in sorted(guess_outcomes_dict):
            g = guess_outcomes_dict[key]
            rptl = '\n' + keyed_if + key + ' ' + '{:3d}'.format(len(g)) + ': ' + ', '.join(sorted(g))
            rptwnd.verbose_data.insert(tk.END, rptl)



def report_footer_stats_summary_to_window(best_rank_dict: dict, rptwnd: ctk):
    rptwnd.verbose_data.insert(tk.END, outcomes_stats_summary_line(best_rank_dict))
    rptwnd.verbose_data.see('end')

def outcomes_stats_summary_line(best_rank_dict: dict) -> str:
    """
    Return a formatted summary line of outcome stats across all best-ranked guesses.
    stats_summary [0]:qty,[1]:smallest,[2]:largest, [3]:average,
    [4]:population variance, [5]:entropy bits as a tuple
    :param best_rank_dict: Dictionary of best outcome-ranked guesses and their stat tuples.
    :return: Formatted summary string for insertion into the report window.
    """
    g_qty, g_min, g_max, g_ave, g_p2, g_ent, g_xa = outcomes_stat_summary(best_rank_dict)
    return (f"\n> >  Max ent {g_ent:.3f}"
            f", grp qty {g_qty:.0f}"
            f", sizes: min {g_min:.0f}"
            f", min-max {g_max:.0f}"
            f", ave {g_ave:.3f}"
            f", exp {g_xa:.2f}"
            f", p2 {g_p2:.1f}")

def report_footer_opt_wrds_to_window(best_rank_dict: dict, rptwnd: ctk, cond_mode=False):
    rptwnd.verbose_data.insert(tk.END, opt_wrds_for_reporting(best_rank_dict, cond_mode))

def opt_wrds_for_reporting(best_rank_dict: dict, cond_mode: bool = False) -> str:
    """
    Build a formatted string listing the optimal words for report output.

    The dictionary is already sorted by entropy; the first word has the highest
    entropy, and any subsequent words have the highest outcome quantity.

    :param best_rank_dict: Dictionary of optimal words, sorted by entropy descending.
    :param cond_mode: If True, append a condensed-mode sort header.
    :return: Formatted string listing the optimal words.
    """
    words = list(best_rank_dict)
    rptl = (f"\n> >  {len(words)} optimal. "
            f"1st word is highest ent. Any next have the highest outcome qty:\n"
            f"{', '.join(words)}")
    if cond_mode:
        rptl += '\n\nSorted by highest ent:'
    return rptl

def report_footer_optimal_wrds_stats_to_window(best_rank_dict: dict, rptwnd: ctk) -> None:
    """
    Append per-word outcome stats for each optimal guess to the report window.

    stats_summary [0]:qty,[1]:smallest,[2]:largest,[3]:average,
    [4]:population variance,[5]:entropy bits as a tuple

    :param best_rank_dict: Dictionary of best outcome-ranked guesses and their stat tuples.
    :param rptwnd: The report window instance.
    """
    stats_summary = outcomes_stat_summary(best_rank_dict)
    rptwnd.verbose_data.insert(tk.END,
        f"\n> >  Optimal guess stats, each has outcome qty {stats_summary[0]:.0f} or is max entropy:")

    for w, s in best_rank_dict.items():
        g_qty, g_min, g_max, g_ave, g_p2, g_ent, g_xa, *_ = s
        rptwnd.verbose_data.insert(tk.END,
            f"\n{w} - "
            f"qty {g_qty:.0f}, "
            f"ent {g_ent:.3f}, "
            f"min {g_min:.0f}, "
            f"max {g_max:.0f}, "
            f"ave {g_ave:.3f}, "
            f"exp {g_xa:.2f}, "
            f"p2 {g_p2:.1f}")
        rptwnd.verbose_data.see('end')

    rptwnd.verbose_data.configure(state='disabled')

# def valid_mult_ltr(s: str) -> bool:
#     """
#     The format requires the letter placed after the number. The mltr_entry_str
#     argument will have already been converted to uppercase.
#     @param s: The string being checked.
#     @return: Returns True if the second character is an uppercase letter A - Z.
#     """
#     if len(s) != 2:
#         return False
#     else:
#         valid = 'QWERTYUIOPASDFGHJKLZXCVBNM ,'
#         return valid.find(s[1]) > -1

def valid_mult_ltr(s: str) -> bool:
    """
    Return True if s is exactly 2 characters and the second is an uppercase letter.
    The format requires the letter placed after the number. The mltr_entry_str
    argument will have already been converted to uppercase.
    :param s: The string to check (expected to already be uppercase).
    :return: True if len(s) == 2 and s[1] is A–Z, False otherwise.
    """
    return len(s) == 2 and s[1] in string.ascii_uppercase

def valid_first_mult_number(s: str) -> bool:
    """
    Return True if the first character of s is a valid multiplicity number (2 or 3).
    The multiple letter requirement would apply to only
    2 or 3 multiple instances for that letter. The format
    requires the number placed before the letter.
    :param s: The string to check.
    :return: True if s starts with '2' or '3', False otherwise.
    """
    return bool(s) and s[0] in ('2', '3')

def validate_mult_ltr_sets(mltr_entry_str: str) -> str:
    """
    Validate and clean a multiple-letter specification string.

    Conforms user input to the format <number><letter>,<number><letter> (e.g. "2e,3a").
    Intentionally lenient — designed as a live entry conformer, not strict validation.

    :param mltr_entry_str: The multiple-letter specification entry.
    :return: Cleaned, comma-separated string of valid entries.
    """
    if not mltr_entry_str:
        return mltr_entry_str
    if mltr_entry_str[-1] == ',':
        return mltr_entry_str
    if mltr_entry_str[-1] == ' ':
        return mltr_entry_str.rstrip() + ','

    valid = []
    for s in mltr_entry_str.upper().split(','):
        if not s:
            continue
        if valid_first_mult_number(s):
            valid.append(s[:2] if valid_mult_ltr(s) else s[0])

    return ','.join(valid)

def size_and_position_this_window(self, this_wnd_width: int, this_wnd_height: int,
                                  offset_h: int, offset_w: int) -> None:
    """
    Centre the window on screen at the desired size, with optional offsets.

    :param this_wnd_width: Desired window width in pixels.
    :param this_wnd_height: Desired window height in pixels.
    :param offset_h: Vertical offset from centre (positive moves down).
    :param offset_w: Horizontal offset from centre (positive moves right).
    """
    pos_x = (self.winfo_screenwidth()  - this_wnd_width)  // 2 + offset_w
    pos_y = (self.winfo_screenheight() - this_wnd_height) // 2 + offset_h
    self.geometry(f"{this_wnd_width}x{this_wnd_height}+{pos_x}+{pos_y}")

def hard_mode_guesses(default_guesses: dict, req_pat: str, req_ltrs: list) -> dict:
    """
    Filter guess words to those complying with hard mode green and yellow clue constraints.
    Returns hard mode guess words from a dictionary of guess words that comply with
    hard mode for green clues as a regex string and yellow clue letters in a list.
    :param default_guesses: Dictionary of candidate guess words.
    :param req_pat: Green clues as a regex pattern string.
    :param req_ltrs: Yellow clue letters that must be present.
    :return: Filtered dictionary of hard mode compliant guess words.
    """
    return {w: v for w, v in default_guesses.items()
            if hard_mode_func_grn((w, v), req_pat) and hard_mode_func_yel((w, v), req_ltrs)}

def hard_mode_func_grn(pair: tuple, req_pat: str) -> bool:
    """
    Return True if the word (key) in pair matches the required green letter pattern.

    :param pair: A (word, value) dictionary item tuple.
    :param req_pat: Regex green clue pattern to match against.
    :return: True if the word matches, False otherwise.
    """
    key, _ = pair
    return bool(re.match(req_pat, key))

def hard_mode_func_yel(pair: tuple, req_ltrs: list) -> bool:
    """
    Return True if the word (key) in pair contains all required yellow letters.

    :param pair: A (word, value) dictionary item tuple.
    :param req_ltrs: Yellow letters that must all be present in the word.
    :return: True if the word contains every required letter, False otherwise.
    """
    key, _ = pair
    return all(ltr in key for ltr in req_ltrs)

def make_lpc_list_dict(wrds: list) -> dict[str, list]:
    """
    Build a letter position count dictionary from a word list.

    Each key is a letter; its value is a 5-element list where each element
    counts how many times that letter appears at that position across all words.

    :param wrds: List of 5-letter words.
    :return: Dictionary mapping each letter to its per-position occurrence counts.
    """
    lpc_dict: dict[str, list] = {}
    for wrd in wrds:
        for i, lt in enumerate(wrd):
            lpc_dict.setdefault(lt, [0, 0, 0, 0, 0])
            lpc_dict[lt][i] += 1
    return lpc_dict

def dict_ltr_frq_data_for_words_list(wrds: list) -> dict[str, list]:
    """
    Build a letter frequency data dictionary for a word list.

    Each entry maps a letter to its 5-element position count list, extended with
    a position hierarchy — groups of 1-based positions ordered from most to least
    frequent. Positions with equal counts are placed in the same group.

    Example: counts [3, 1, 5, 2, 0] → hierarchy [[3], [1], [4], [2]]

    :param wrds: List of 5-letter words.
    :return: Dictionary mapping each letter to its extended position count list.
    """
    lpc_list_dict = make_lpc_list_dict(wrds)

    for ltr, lpc_list in lpc_list_dict.items():
        if not sum(lpc_list):
            continue

        # Pair each non-zero count with its position, sorted highest count first
        pos_counts = sorted(
            [(count, pos) for pos, count in enumerate(lpc_list) if count],
            key=lambda x: -x[0]
        )

        # Group positions sharing the same count into one hierarchy level
        hierarchy = [
            [pos + 1 for _, pos in group]
            for _, group in groupby(pos_counts, key=lambda x: x[0])
        ]

        lpc_list.append(hierarchy)

    return lpc_list_dict


def rpt_ltr_use(gen_tally: list, the_word_list: list) -> None:
    """
    Open a data window and report letter usage details for the word list.

    :param gen_tally: 26-element letter tally list.
    :param the_word_list: The word list to analyse.
    """
    datawnd = RptWnd("Data")
    datawnd.title("Wordle Helper - Letter Use Details")

    gen_tally_dict = dict_gen_tally(gen_tally, len(the_word_list))
    use_details_dict = dict_ltr_frq_data_for_words_list(the_word_list)

    datawnd.verbose_data.insert(tk.END,
        f"----- Letter use details for the {len(the_word_list)} words -----\n"
        f"- Letter, % having, position counts, [position hierarchy] -\n")

    for ltr, lper in gen_tally_dict.items():
        entry = use_details_dict[ltr]
        counts    = ', '.join(str(c) for c in entry[:5])
        hierarchy = ', '.join(str(group) for group in entry[5])
        datawnd.verbose_data.insert(tk.END,
            f"{ltr.upper()}, {lper:.2f}, {counts}, {hierarchy}\n")



class ShellCmdList:
    """
    The class is a list holding the shell commands that operate a series of grep regex
    functions on the word list text targeted as the solutions list file.
    It has functions that build the grep regex arguments related to filtering wordle
    letter conditions.
    Some functions are not used in the gui pywordletool.
    The command list is by instance.
    @param list_file_name: The word list filename.
    """

    def __init__(self, list_file_name: str) -> None:
        """
        The shCMDList is the list of ready to pipe together grep arguments, including the
        base cat filename wordlist command.
        @param list_file_name:
        """
        self.shCMDlist = list()
        self.shCMDlist.append("cat " + list_file_name)

    def add_cmd(self, s: str) -> None:
        """
        Adds string s to the command stack.
        @param s: the string to add to the command stack
        """
        if len(s) > 0:
            self.shCMDlist.append(s)

    def add_rand_incl_frm_cmd(self, lst: str) -> str:
        """
        Given a string of letters lst, adds to the command
        stack a grep filter requiring a letter picked at random
        from string lst.
        @param lst: string of letters to randomly pick one.
        @return: Returns that randomly picked letter for
        feedback purposes.
        """
        rand_frm_l = random.choice(lst)
        self.shCMDlist.append("grep -E '" + rand_frm_l + "'")
        return rand_frm_l

    def add_type_cmd(self, ltr: str, require: bool) -> None:
        """
        Adds command to command stack to require or exclude letter ltr.
        Appends mltr_entry_str to CMDList as either:
        required (true) or
        excluded (false)
        @param ltr: the grep string
        @param require: true=required, false=exclude
        """
        if len(ltr) > 0:
            if require:  # require
                self.shCMDlist.append("grep -E '" + ltr + "'")
            else:
                self.shCMDlist.append("grep -vE '" + ltr + "'")

    def add_excl_pos_cmd(self, ltr: str, p: int, add_e: bool) -> None:
        """
        Adds command to the command stack that excludes letters from a position number.
        Context is that letter is known, therefore is required but not at the designated position.
        These are the Wordle Yellow clues.
        @param ltr: The letter.
        @param p:  The letter's position, indexed 1 = first.
        @param add_e: Add as requirement.
        """
        if len(ltr) > 0:
            # add_E a requirement argument, being managed
            # outside the shCMDList so that the shCMDList
            # does not duplicate the grep -E for any one letter.
            if add_e:  # Require the letter if not already done
                self.shCMDlist.append("grep -E '" + ltr + "'")
            # Build the dots around the letter to specify the excluded letter position.
            c = 5
            dp = ''.rjust(p - 1, '.')
            dpn = ''.rjust(c - p, '.')
            self.shCMDlist.append("grep -vE '" + dp + ltr + dpn + "'")

    def add_incl_pos_cmd(self, ltr: str, p: int) -> None:
        """
        Adds command to command stack to require the letter at a position number.
        @param ltr: The letter.
        @param p: The letter's position, indexed 1 = first.
        """
        if len(ltr) > 0:
            # Build the dots around the letter to specify the required letter position.
            c = 5
            dp = ''.rjust(p - 1, '.')
            dpn = ''.rjust(c - p, '.')
            self.shCMDlist.append("grep -E '" + dp + ltr + dpn + "'")

    def add_type_mult_ltr_cmd(self, mult_ltr_definition: str, typ: int) -> None:
        """
        Converts the multiple letter code, like 2a,3a, to the required grep regex
        to affect that multiple letter requirement. The appends the command line to the
        self.shCMDlist
        @param mult_ltr_definition: something like 2a,3s
        @param typ: 1=require, 2=exclude
        """
        codes = mult_ltr_definition.split(',')
        g_code = ''
        for code in codes:
            if len(code) == 2:
                c = code[0]
                x = code[1]
                if c == '2':
                    g_c = f"{x}{x}|{x}.{x}|{x}..{x}|{x}...{x}"
                    if len(g_code) < 1:
                        g_code = g_c
                    else:
                        g_code = g_code + '|' + g_c
                if c == '3':
                    g_c = f"{x}{x}{x}|{x}.{x}{x}|.{x}{x}.{x}|{x}.{x}{x}.|{x}..{x}{x}|{x}{x}..{x}|{x}.{x}.{x}"
                    if len(g_code) < 1:
                        g_code = g_c
                    else:
                        g_code = g_code + '|' + g_c
        if typ == 1:
            self.shCMDlist.append("grep -E '" + g_code + "'")
        if typ == 2:
            self.shCMDlist.append("grep -vE '" + g_code + "'")

    def full_cmd(self) -> str:
        """
        Returns the command stack assembled into one single shell command line to
        list only those words that satisfy the grep regex filters.
        @return: string being the single shell command line.
        """
        pipe = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pipe
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd


class ToolResults:
    """
    ToolResults(data path, vocabulary file name, letter_ranks file, loc_allow_dups)
    The wordle tool all wrapped up into one being, including the grep command list.
    """

    def __init__(self,
                 data_path: str,
                 vocabulary: str,
                 letter_ranks: str,
                 allow_dups: bool,
                 rank_mode: int,
                 ordr_by_rank: bool,
                 cull_pu=False,
                 pu_vocab='') -> None:
        """
        @param data_path: words list folder name
        @param vocabulary: words list file name less path
        @param letter_ranks: letter ranking textfile name
        @param allow_dups: allow multiple same letters bool flag
        @param rank_mode: letter ranking mode integer
        @param ordr_by_rank: order results by rank bool flag
        """
        self.data_path = data_path
        self.vocab = vocabulary  # vocabulary is the words list textfile
        self.ltr_ranks = letter_ranks  # ltr_ranks is the letter ranking textfile
        self.allow_dups = allow_dups  # loc_allow_dups is the-allow-duplicate-letters flag
        self.cull_pu = cull_pu
        self.pu_vocab = pu_vocab
        self.rank_mode = rank_mode
        self.no_ordr = not ordr_by_rank
        wrd_list_file_name = get_word_list_path_name(self.data_path + self.vocab)
        rank_file = self.data_path + self.ltr_ranks

        self.ltr_rank_dict = make_ltr_rank_dictionary(rank_file)  # ltr_rank_dict is the rank dictionary

        # Initialize and set up the ShellCmdList class instance that holds the
        # grep filtering command stack. Guessing because it is a class instance is why it
        # can be passed around as a global variable where it gets modified along the way.
        self.tool_command_list = ShellCmdList(wrd_list_file_name)  # init with cat wordlistfile
        # At this point the grep stack is ready for executing in as a class function.
        self.ranked_wrds_dict = {}  # dictionary of ranked words resulting from grep filtering
        self.raw_cnt = 0
        self.ranked_cnt = 0

    def get_result_of_grep_wrd_lst(self) -> list:
        """
        @return: Return the results words list without any ranking or sorting.
        """
        with Popen(self.tool_command_list.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
            return list(map(lambda i: i[: -1], proc.stdout.readlines()))
        # return os.popen(self.tool_command_list.full_cmd()).read().split("\n")

    def get_ranked_grep_result_wrd_lst(self, no_rank=False) -> dict:
        """
        Ranking and filtering the words into a dictionary
        Set loc_allow_dups to prevent letters from occurring more than once
        First pick should not use duplicates, later picks should consider them.
        Exclude all empty string. This can happen at the file end.
        @param no_rank:
        @return: Returns ranked results words list as sorted dictionary.
        """
        wrds = self.get_result_of_grep_wrd_lst()
        if self.cull_pu:
            pu_wrds = get_wordlist(get_word_list_path_name(self.data_path + self.pu_vocab, False))
            cull_sol_list(wrds, pu_wrds)
        self.raw_cnt = len(wrds)
        self.ranked_wrds_dict = make_ranked_filtered_result_dictionary(wrds,
                                                                       self.ltr_rank_dict,
                                                                       self.allow_dups,
                                                                       self.rank_mode,
                                                                       self.no_ordr,
                                                                       no_rank)
        self.ranked_cnt = len(self.ranked_wrds_dict)
        return self.ranked_wrds_dict

    def get_status(self) -> str:
        """
        @return: Returns the status text line.
        """
        status = '{} words shown from the {} full word list.'.format(self.ranked_cnt, self.raw_cnt)
        return status

    def get_grep_cmd_str(self) -> str:
        """
        Returns the entire fully assembled grep command line.
        This line includes the full path names.
        @return: fully assembled grep command line
        """
        return self.tool_command_list.full_cmd()

    def get_grep_cmd_less_filepath(self) -> str:
        """
        Returns the entire fully assembled grep command line. This line excluded
        the full path names and so is used in the GUI display.
        @return: Returns the entire fully assembled grep command line,less pathname
        """
        full_cmd = self.tool_command_list.full_cmd()
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path)
        part_cmd = full_cmd.replace(full_path_name, '', 1)
        return part_cmd

    def get_word_list(self, guess_no: int, guess_wrd='', verbose=False, no_rank=False) -> dict:
        """
        Used when a guess word has been recently used to be the filter basis
        for a ranked word list.
        Combines returning the ranked word list dictionary with
        printing out information if needed.
        @param guess_no: The current guess number
        @param guess_wrd: The guess word basis is the was one
        @param verbose: Flag to indicate display
        @param no_rank: Flag to indicate no ranking or sorting, used for speed
        @return: The ranked word list corresponding to the filtering
        arguments already passed to the wordletool device.
        """
        the_word_list = self.get_ranked_grep_result_wrd_lst(no_rank)
        if verbose:
            print()
            if guess_no > 1:
                print('Selection pool for guess {} based on guess {} => {}'
                      .format(guess_no, (guess_no - 1), guess_wrd))
            else:
                print('Selection pool for guess {}'.format(guess_no))
            print(self.get_status())
            print(self.get_grep_cmd_less_filepath())
            print_word_list_col_format(the_word_list, 6)
        return the_word_list


class CustomText(tk.Text):
    """A text widget with a new method, highlight_pattern()
    example:
    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")
    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    """

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def remove_tag(self, tag):
        self.tag_remove(tag, "1.0", "end")


    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=True, remove_priors=True, do_scroll=True, mode=0) -> int:
        """Apply the given tag to all text that matches the given pattern.
        If 'regexp' is True, pattern is treated as a Tcl regular expression.

        :param pattern:       Text or regex to find.
        :param tag:           Highlight colour tag to apply.
        :param start:         Search start position (default "1.0").
        :param end:           Search end position (default "end").
        :param regexp:        Use regex matching.
        :param remove_priors: Remove all prior highlighting for this tag first.
        :param do_scroll:     Scroll to each found occurrence during search;
                              always scrolls to first match when done.
        :param mode:          0 = find all; 1 = find first match only.
        :return:              Number of matches found.
        """
        if remove_priors:
            self.remove_tag(tag)

        if not pattern:
            return 0

        self.mark_set("matchStart", self.index(start))
        self.mark_set("matchEnd",   self.index(start))
        self.mark_set("searchLimit", self.index(end))

        count = tk.IntVar()
        first_index = ""
        fnd_cnt = 0

        while True:
            try:
                index = self.search(pattern, "matchEnd", "searchLimit",
                                    count=count, regexp=regexp)
            except Exception as e:
                messagebox.showinfo(title=None, message=f'Regex error: "{e}".')
                break

            if index == "":
                break  # no (more) matches

            if count.get() == 0:
                break  # degenerate pattern that matches zero-length strings

            fnd_cnt += 1
            if first_index == "":
                first_index = index

            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index}+{count.get()}c")
            self.tag_add(tag, "matchStart", "matchEnd")

            if do_scroll:
                self.see(index)

            if mode == 1:
                break  # caller only wants the first match

        # Post-loop: report outcome once, then settle on first match.
        if fnd_cnt == 0:
            if "^" not in pattern:
                msg = (
                    f'Did not find "{pattern}".'
                    f"\n\nThe word that was searched is not in the vocabulary that was used for guesses."
                    f"\n\nIs Hard Mode selected? Hard Mode excludes guesses from the vocabulary."
                )
            else:
                msg = (
                    f'Did not find "{pattern}".'
                    f'\n\n"Find" in the non-condensed format verbose mode includes "for: " in the search '
                    f"text because the main use is to find the outcomes for a particular word. Adding the "
                    f'"for: " does this because the outcome header uniquely includes "for: ".'
                    f'\n\n"Find" operates a regex search on the entire text.'
                    f' Putting "^", which means "starting with", works in the unkeyed condensed report '
                    f"because each line starts with the guess word and it is the guess word that is usually "
                    f"what one searches for."
                )
            messagebox.showinfo(title=None, message=msg)
        elif first_index:
            self.see(first_index)  # settle view on first match, not last

        return fnd_cnt


class RptWnd(ctk.CTkToplevel):
    """Verbose information window."""

    _TAG = 'opt'
    _DEFAULT_SEARCH = 'for: '

    def clear_msg1(self) -> None:
        self.verbose_data.configure(state='normal')
        self.verbose_data.delete(1.0, tk.END)
        self.verbose_data.configure(state='disabled')
        self._reset_next_button()

    def close_rpt(self) -> None:
        self.destroy()

    def find_the_text(self, _event=None) -> None:
        regex = self.search_text.get().strip()
        org_title = self.title()
        self.title(f'> > Busy on "{regex}", Please Wait < <')
        self.update()

        if len(regex) > 4:
            self._run_search(regex)
        else:
            msg = (
                f'Find "{regex}"?\n\nIn a verbose report one usually searches for a five letter guess word'
                f' preceded by "for:", which is then very quickly highlighted.\n\nThe same, but without "for:",'
                f' is typically how one searches in the condensed verbose report.\n\nFind can accept any text, '
                f'including a regex pattern. A regex pattern can do most of the work required to find hard mode '
                f'candidates in the condensed list.\n\nFor example, "^.t..p" would indicate words where t and p '
                f'are at those positions. The "^" is important. The "^" indicates the next character ".", which '
                f'means any character, must be at the text line beginning. Thus five letter words and not parts '
                f'of larger words are highlighted. It is best to not have the condensed report keyed.'
                f'\n\nThe "|" character allows for multiple search criteria. For example, "^..c..|^.ed..|^....h"'
                f' finds words matching any one of those three patterns.'
                f'\n\nThe time it takes to highlight the search depends on the amount of text to search and the '
                f'number of items to be highlighted. The report scrolls to the first found instance.'
            )
            if messagebox.askokcancel(title=None, message=msg):
                if regex and regex != self._DEFAULT_SEARCH.strip():
                    self._run_search(regex)

        self.title(org_title)
        self.update()

    def _run_search(self, regex: str) -> None:
        fnd_cnt = self.verbose_data.highlight_pattern(
            regex, self._TAG, remove_priors=True, mode=0)

        # Collect match start positions from tag ranges without a second search pass.
        ranges = self.verbose_data.tag_ranges(self._TAG)
        self._match_positions = [str(ranges[i]) for i in range(0, len(ranges), 2)]
        self._match_index = 0

        if fnd_cnt > 1:
            self._button_next.configure(state='normal', text=f'Next  1/{fnd_cnt}')
        else:
            self._reset_next_button()

    def next_match(self) -> None:
        if not self._match_positions:
            return
        self._match_index = (self._match_index + 1) % len(self._match_positions)
        self.verbose_data.see(self._match_positions[self._match_index])
        n = len(self._match_positions)
        self._button_next.configure(text=f'Next  {self._match_index + 1}/{n}')

    def _reset_next_button(self) -> None:
        self._match_positions = []
        self._match_index = 0
        if hasattr(self, '_button_next'):
            self._button_next.configure(state='disabled', text='Next')

    def back_to_summary(self) -> None:
        """Scroll to 'Outcome summary' by highlighting it briefly, then remove the highlight."""
        self.verbose_data.highlight_pattern(
            'Outcome summary', self._TAG, remove_priors=True, mode=1)
        self.verbose_data.remove_tag(self._TAG)
        self._reset_next_button()

    def rpt_show_grps_driller(self) -> None:
        if self.rpt_grpsdriller_window is None or not self.rpt_grpsdriller_window.winfo_exists():
            self.rpt_grpsdriller_window = outcomedrilling.OutcmsDrillingMain()
        else:
            self.rpt_grpsdriller_window.focus()

    def __init__(self, context: str = '') -> None:
        super().__init__()
        self.context = context
        self.resizable(width=True, height=True)

        is_data = (context == 'Data')
        size_and_position_this_window(self, 600 if is_data else 790,
                                           440 if is_data else 600, 0, 0)

        self.option_add('*Font', ('Helvetica', 14, 'normal'))
        self.search_text = tk.StringVar(value=self._DEFAULT_SEARCH)
        self.rpt_grpsdriller_window = None
        self._match_positions: list = []
        self._match_index: int = 0

        self.verbose_info_frame = ctk.CTkFrame(self, corner_radius=10)
        self.verbose_info_frame.pack(fill='both', padx=2, pady=0, expand=True)
        self.verbose_info_frame.grid_columnconfigure(0, weight=1)
        self.verbose_info_frame.grid_rowconfigure(0, weight=1)

        self.verbose_data = CustomText(
            self.verbose_info_frame,
            wrap='word',
            font=('Courier', 12, 'normal'),
            padx=6, pady=6,
            background='#dedede',
            borderwidth=0,
            highlightthickness=0,
        )
        self.verbose_data.grid(row=0, column=0, padx=6, pady=0, sticky='nsew')
        self.verbose_data.tag_configure(self._TAG, background='#ffd700')

        verbose_rpt_sb = ttk.Scrollbar(self.verbose_info_frame, orient='vertical')
        verbose_rpt_sb.grid(row=0, column=1, sticky='ens')
        self.verbose_data.config(yscrollcommand=verbose_rpt_sb.set)
        verbose_rpt_sb.config(command=self.verbose_data.yview)

        button_q = ctk.CTkButton(self, text='Close', text_color='black',
                                 width=100, command=self.close_rpt)
        button_q.pack(side='right', padx=10, pady=10)
        self.protocol('WM_DELETE_WINDOW', self.close_rpt)

        if not is_data:
            entry_find = ctk.CTkEntry(self, textvariable=self.search_text)
            entry_find.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)
            entry_find.bind('<KeyRelease-Return>', self.find_the_text)

            ctk.CTkButton(self, text='Find', text_color='black', width=110,
                          command=self.find_the_text).pack(side=tk.LEFT, padx=4, pady=10)

            # Created and packed here to fix its position between Find and Summary;
            # starts disabled and is enabled only when a search yields more than one match.
            self._button_next = ctk.CTkButton(self, text='Next', text_color='black', width=110,
                                              state='disabled', command=self.next_match)
            self._button_next.pack(side=tk.LEFT, padx=4, pady=10)

            ctk.CTkButton(self, text='Summary', text_color='black',
                          command=self.back_to_summary).pack(side=tk.LEFT, padx=4, pady=10)

            ctk.CTkButton(self, text='Outcome Driller', text_color='black',
                          command=self.rpt_show_grps_driller).pack(side=tk.LEFT, padx=4, pady=10)




# class HelpWindow(ctk.CTkToplevel):
#     """
#     The help information window
#     """
#
#     def close_help(self) -> None:
#         self.destroy()
#
#     def get_rank_data(self) -> str:
#         """
#         @return: Returns string that is the information
#         """
#         full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, self.letter_rank_file)
#         if os.path.exists(full_path_name):
#             f = open(full_path_name, "r", encoding="UTF8").read()
#         else:
#             f = 'Could not find. ' + str(full_path_name)
#         return f
#
#     def get_info(self) -> str:
#         full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, 'helpinfo.txt')
#         if os.path.exists(full_path_name):
#             f = open(full_path_name, "r", encoding="UTF8").read()
#         else:
#             f = 'This is all the help you get because file helpinfo.txt has gone missing.'
#         return f
#
#     def show_info(self) -> None:
#         self.help_msg.configure(state='normal')
#         self.help_msg.delete(1.0, tk.END)
#         self.help_msg.insert(tk.END, self.get_info())
#         self.help_msg.configure(state='disabled')
#
#     def show_rank_info(self) -> None:
#         self.help_msg.configure(state='normal')
#         self.help_msg.delete(1.0, tk.END)
#         raw_rank_data = self.get_rank_data()
#         f = raw_rank_data.replace(":", "\t")
#         self.help_msg.insert(tk.END, "Using file: " + self.letter_rank_file + "\n")
#         self.help_msg.insert(tk.END, "RNK = Rank for any occurrence\n")
#         self.help_msg.insert(tk.END, "RNK-X = Rank at position X in the word\n\n")
#         self.help_msg.insert(tk.END, "LTR\tRNK\tRNK-1\tRNK-2\tRNK-3\tRNK-4\tRNK-5\n")
#         self.help_msg.insert(tk.END, "---\t---\t-----\t-----\t-----\t-----\t-----\n")
#         self.help_msg.insert(tk.END, f)
#         self.help_msg.configure(state='disabled')
#
#     def __init__(self, data_path, letter_rank_file):
#         super().__init__()
#         self.data_path = data_path
#         self.letter_rank_file = letter_rank_file
#         self.resizable(width=True, height=True)
#         self.title('Some Information For You')
#         help_wd = 530
#         help_ht = 500
#         size_and_position_this_window(self, help_ht, help_wd, 0, 0)
#
#         # configure style
#         style = ttk.Style()
#         style.theme_use()
#         help_font_tuple_n = ("Courier", 12, "normal")
#         self.option_add("*Font", help_font_tuple_n)
#
#         self.help_info_frame = tk.Frame(self,
#                                         borderwidth=0
#                                         )
#         self.help_info_frame.pack(side='top', fill='both', padx=2, pady=0, expand=True)
#         self.help_info_frame.grid_rowconfigure(0, weight=1)
#         self.help_info_frame.grid_columnconfigure(0, weight=1)
#
#         self.help_msg = tk.Text(self.help_info_frame,
#                                 wrap='word',
#                                 padx=10,
#                                 pady=8,
#                                 background='#dedede',
#                                 borderwidth=0,
#                                 highlightthickness=0
#                                 )
#         self.help_msg.grid(row=0, column=0, padx=6, pady=0, sticky="nsew")
#
#         # scrollbar for help
#         help_sb = ttk.Scrollbar(self.help_info_frame, orient='vertical')
#         help_sb.grid(row=0, column=1, padx=1, pady=2, sticky='ens')
#         self.help_msg.config(yscrollcommand=help_sb.set)
#         help_sb.config(command=self.help_msg.yview)
#         self.show_info()
#
#         button_q = ctk.CTkButton(self, text="Close",
#                                  text_color="black",
#                                  command=self.close_help)
#         button_q.pack(side="right", padx=10, pady=10)
#         self.protocol("WM_DELETE_WINDOW", self.close_help)  # assign to closing button [X]
#
#         button_r = ctk.CTkButton(self, text="Letter Ranking",
#                                  text_color="black",
#                                  command=self.show_rank_info
#                                  )
#         button_r.pack(side="left", padx=10, pady=10)
#
#         button_i = ctk.CTkButton(self, text="Information",
#                                  text_color="black",
#                                  command=self.show_info
#                                  )
#         button_i.pack(side="left", padx=10, pady=10)

class HelpWindow(ctk.CTkToplevel):
    """
    Help information window displaying general info and letter ranking data.
    """

    def _read_file(self, filename: str, missing_msg: str) -> str:
        """
        Read a text file from the data path, returning a fallback message if absent.

        :param filename: Filename within the data path.
        :param missing_msg: Message to return if the file is not found.
        :return: File contents or fallback message.
        """
        full_path = os.path.join(os.path.dirname(__file__), self.data_path, filename)
        if not os.path.exists(full_path):
            return missing_msg
        with open(full_path, encoding='utf-8') as fh:
            return fh.read()

    def get_rank_data(self) -> str:
        return self._read_file(
            self.letter_rank_file,
            f'Could not find: {os.path.join(self.data_path, self.letter_rank_file)}'
        )

    def get_info(self) -> str:
        return self._read_file(
            'helpinfo.txt',
            'This is all the help you get because file helpinfo.txt has gone missing.'
        )

    def _display(self, content: str) -> None:
        """Replace the help text widget contents with content."""
        self.help_msg.configure(state='normal')
        self.help_msg.delete(1.0, tk.END)
        self.help_msg.insert(tk.END, content)
        self.help_msg.configure(state='disabled')

    def show_info(self) -> None:
        self._display(self.get_info())

    def show_rank_info(self) -> None:
        header = (
            f"Using file: {self.letter_rank_file}\n"
            "RNK = Rank for any occurrence\n"
            "RNK-X = Rank at position X in the word\n\n"
            "LTR\tRNK\tRNK-1\tRNK-2\tRNK-3\tRNK-4\tRNK-5\n"
            "---\t---\t-----\t-----\t-----\t-----\t-----\n"
        )
        self._display(header + self.get_rank_data().replace(':', '\t'))

    def close_help(self) -> None:
        self.destroy()

    def __init__(self, data_path, letter_rank_file):
        super().__init__()
        self.data_path = data_path
        self.letter_rank_file = letter_rank_file
        self.resizable(width=True, height=True)
        self.title('Some Information For You')

        size_and_position_this_window(self, 530, 500, 0, 0)

        style = ttk.Style()
        style.theme_use()
        self.option_add("*Font", ("Courier", 12, "normal"))

        self.help_info_frame = tk.Frame(self, borderwidth=0)
        self.help_info_frame.pack(side='top', fill='both', padx=2, pady=0, expand=True)
        self.help_info_frame.grid_rowconfigure(0, weight=1)
        self.help_info_frame.grid_columnconfigure(0, weight=1)

        self.help_msg = tk.Text(self.help_info_frame,
                                wrap='word', padx=10, pady=8,
                                background='#dedede', borderwidth=0,
                                highlightthickness=0)
        self.help_msg.grid(row=0, column=0, padx=6, pady=0, sticky='nsew')

        help_sb = ttk.Scrollbar(self.help_info_frame, orient='vertical')
        help_sb.grid(row=0, column=1, padx=1, pady=2, sticky='ens')
        self.help_msg.config(yscrollcommand=help_sb.set)
        help_sb.config(command=self.help_msg.yview)

        self.show_info()

        button_q = ctk.CTkButton(self, text='Close', text_color='black', command=self.close_help)
        button_q.pack(side='right', padx=10, pady=10)
        self.protocol('WM_DELETE_WINDOW', self.close_help)

        button_r = ctk.CTkButton(self, text='Letter Ranking', text_color='black', command=self.show_rank_info)
        button_r.pack(side='left', padx=10, pady=10)

        button_i = ctk.CTkButton(self, text='Information', text_color='black', command=self.show_info)
        button_i.pack(side='left', padx=10, pady=10)