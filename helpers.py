# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
from subprocess import Popen, PIPE
import sys
import os
import random
import math
import re
import tkinter as tk  # assigns tkinter stuff to tk namespace
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own
# ttk namespace so that tk is preserved
from tkinter import messagebox
import customtkinter as ctk
import groupdrilling
from fmwm import debug_mode
from logging import exception

gc_z = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def get_word_list_path_name(local_path_file_name: str, critical = True) -> str:
    """
    Returns the wordle word list full pathname
    Exits program if not found
    @param local_path_file_name:
    @return: wordle word list full pathname
    """
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_file_name)
    if os.path.exists(full_path_name):
        return full_path_name
    else:
        if critical:
            msg = f'The wordle word list file {local_path_file_name} was not found. \n\nExpected here: {full_path_name}'
            print(msg)
            print()
            messagebox.showerror(title='Stopping Here', message=msg)
            sys.exit()
        else:
            msg = (f'The wordle word list file {local_path_file_name} was not found. \n\nExpected here: {full_path_name}'
                   f'\n\nThe option using this file will not use it.')
            messagebox.showerror(title='Will Continue', message=msg)
            return ''

"""
Letter ranking functions for rank that includes by letter position method
"""
def make_ltr_rank_dictionary(local_path_rank_file: str) -> dict:
    """
    Make and return the letter ranking dictionary
    @param local_path_rank_file:
    @return: the letter ranking dictionary
    """
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_rank_file)
    ltr_rank_dict = {}  # ltr_rank_dict will be the rank dictionary
    if os.path.exists(full_path_name):
        with open(full_path_name) as f:
            for ltr in f:
                ltr = ltr.split(":")
                ltr[-1] = ltr[-1].strip()
                k = ltr[0]
                ltr.pop(0)
                ltr_rank_dict[k] = [float(d) for d in ltr]  # want as floats
    else:
        msg = f'Letter ranking file {local_path_rank_file} not found. Switching to built in Classic letter ranking.'
        print(msg)
        messagebox.showwarning('Warning', message=msg)
        ltr_rank_dict = {
            "e": [44.7, 2.30, 8.09, 5.27, 16.48, 12.51],
            "a": [35.1, 5.25, 12.47, 9.39, 5.41, 2.63],
            "r": [31.2, 4.03, 8.22, 6.28, 5.06, 7.61],
            "o": [27.3, 1.57, 11.41, 7.53, 4.44, 2.36],
            "i": [25.3, 1.27, 8.87, 8.98, 5.56, 0.61],
            "t": [24.6, 5.24, 2.31, 4.77, 4.58, 7.70],
            "l": [23.3, 3.38, 6.00, 4.29, 4.99, 4.63],
            "s": [22.5, 11.72, 0.69, 3.02, 5.48, 1.59],
            "n": [20.5, 1.55, 3.16, 5.43, 5.95, 4.36],
            "d": [19.9, 4.17, 0.82, 3.17, 2.19, 9.57],
            "u": [17.8, 1.39, 7.60, 5.57, 3.09, 0.14],
            "y": [16.8, 0.39, 0.78, 1.01, 0.17, 14.48],
            "c": [16.7, 7.30, 1.54, 2.33, 4.52, 1.03],
            "p": [14.5, 5.55, 1.86, 2.68, 2.02, 2.34],
            "h": [13.8, 3.07, 4.80, 0.56, 1.03, 4.35],
            "m": [12.2, 4.18, 1.41, 2.58, 2.58, 1.44],
            "g": [11.3, 4.14, 0.46, 2.62, 2.64, 1.44],
            "b": [10.9, 6.49, 0.57, 2.34, 0.94, 0.54],
            "k": [8.6, 1.05, 0.39, 1.28, 2.39, 3.52],
            "f": [7.8, 4.56, 0.26, 0.95, 1.18, 0.85],
            "w": [7.4, 3.06, 1.59, 1.30, 0.85, 0.60],
            "v": [5.6, 1.56, 0.56, 2.01, 1.50, 0.00],
            "z": [1.9, 0.15, 0.05, 0.64, 0.81, 0.24],
            "x": [1.9, 0.06, 0.53, 0.79, 0.08, 0.42],
            "j": [1.3, 0.97, 0.06, 0.14, 0.11, 0.00],
            "q": [1.0, 0.77, 0.20, 0.03, 0.00, 0.00]
        }
    return ltr_rank_dict

def wrd_rank(wrd: str, ltr_rank_dict: dict, method: int) -> float:
    """
    Returns a word's letter frequency ranking.
    # Any word longer than 5 letters has undefined rank.
    # This allows for wordlist flexibility.
    @param wrd: subject word
    @param ltr_rank_dict: ranking dictionary
    @param method: int 0=occurrence, 1=position, 2=both occurrence and position
    @return: Returns a word's letter frequency ranking.
    """
    if len(wrd) > 5:
        return 0
    r = 0
    if method == 0:  # rank by anywhere in word
        for x in wrd:
            # 0th position is rank by anywhere
            if 97 <= ord(x) <= 122:
                r = r + ltr_rank_dict[x][0]
        return r
    if method == 1:  # rank by position in the word
        p = 1
        for x in wrd:
            # 1 to 5th position is rank for being in that position
            if 97 <= ord(x) <= 122:
                r = r + ltr_rank_dict[x][p]
                p += 1
        return r
    if method == 2:  # rank by position in the word
        p = 1
        for x in wrd:
            # combine methods 0 and 1
            if 97 <= ord(x) <= 122:
                r = r + ltr_rank_dict[x][0] + ltr_rank_dict[x][p]
                p += 1
        return r
    return 0

def wrd_has_duplicates(wrd) -> bool:
    """
    Checks is a word has duplicate letters.
    This function is also used for the special pattern
    where '.' is allowed. These would not be duplicates.
    @param wrd: word in question
    @return: true=has duplicate letters, false=no duplicate letters
    """
    ltr_d = {}
    wrd = wrd.replace('.', '')
    wrd = wrd.replace(' ', '')
    for ltr in wrd:
        ltr_d[ltr] = ltr
    return len(ltr_d) < len(wrd)

def print_word_list_col_format(the_word_list, n_col):
    """
    List out the ranked word list into n_col columns.
    @param the_word_list:
    @param n_col: number of columns to fill.
    """
    n_items = len(the_word_list)
    h_txt = " Word : Rank "
    left_pad = ""
    mid_pad = "   "
    h_line = left_pad + h_txt
    for i in range(1, n_col):
        h_line = h_line + mid_pad + h_txt
    print(h_line)
    c = 0
    i = 0
    l_msg = ""
    for key, value in the_word_list.items():
        msg = key + " : " + str(value)
        i = i + 1
        if c == 0:
            l_msg = left_pad + msg
        else:
            l_msg = l_msg + mid_pad + msg
        c = c + 1
        if c == n_col:
            print(l_msg)
            c = 0
            l_msg = ""
        if i == n_items:
            print(l_msg)

def make_ranked_filtered_result_dictionary(wrds: list, ltr_rank_dict: dict, allow_dups: bool,
                                           rank_mode: int, no_ordr: bool, no_rank=False) -> dict:
    """
    Ranking and filtering the words into a dictionary.
    @param wrds: The filtered words list
    @param ltr_rank_dict: Letter ranking dictionary
    @param allow_dups:  Allows duplicate letters bool
    @param rank_mode: Letter ranking mode to use
    @param no_ordr: Omit ordering bool
    @param no_rank: Omit ranking bool
    @return: dictionary sorted by the word rank
    """
    wrds_dict = {}
    for w in wrds:
        # currently, the wrd_rank function can handle only 5-letter words
        # if len(w) == 5:
        if len(w) == 0:
            print("len 0")
        if allow_dups:
            # every word goes into the dictionary
            if not no_rank:
                wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))
            else:
                # no ranking for speed since pick will be random
                wrds_dict[w] = '000'
        else:
            # only words having no duplicates goes into the dictionary
            if not wrd_has_duplicates(w):
                if not no_rank:
                    wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))
                else:
                    # no ranking for speed since pick will be random
                    wrds_dict[w] = '000'

    # sorting the ranked word list into a dictionary
    if not no_rank:
        if no_ordr:
            return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[0]))
        else:
            return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))
    else:
        return wrds_dict

def get_results_word_list(this_sh_cmd_lst) -> list:
    """
    Returns the result for the grep command list.
    @param this_sh_cmd_lst: the grep stack of command list
    @return: Returns the list of words that pass the grep command list
    """
    with Popen(this_sh_cmd_lst.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
        return list(map(lambda i: i[: -1], proc.stdout.readlines()))

def get_pu_wordlist(full_path_name) -> list:
    pu_wrds = []
    if os.path.exists(full_path_name):
        with open(full_path_name, 'r') as file:
            for line in file:
                pu_wrds.append(line.split(',', 1)[0].lower())
    return pu_wrds

def cull_sol_list(s_wrds: list, p_wrds: list) -> None:
    """
    Culls the p_wrds list from the s_wrds list. Intended
    for removing the previously used words from thr
    possible solutions word list.
    :param sol_wrds: total solutions wordlist
    :param pu_wrds:  previously used wordlist
    """
    for w in p_wrds:
        try:
            s_wrds.remove(w)
        except ValueError:
            pass

def clear_scrn():
    """
    Clears the console window
    """
    os.system("cls" if os.name == "nt" else "clear")

def get_gencode(word) -> list:
    """
    Return a word's genetic code
    example:woody
    returns:[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0]
    translated: idx 0-25 'abc...xyz' letter count, idx 26 duplicates count, idx 27 genetic rank.
    Rank applies in the title_context for a list of words, so it is calculated later
    @param word: a word in question
    @return: a special list of ints that encode the genetic code
    """
    # gencode is the list of integers that will be returned
    gencode = gc_z.copy()
    # dups counts the number of times letters occur more than once
    dups = 0
    # loop through each letter in the word
    for ltr in word:
        idx = ord(ltr) - 97
        # Increment dups if that letter has already been seen.
        if gencode[idx] > 0:
            dups += 1
        # Mark that letter as having been seen.
        gencode[idx] = 1
    gencode[26] = dups
    return gencode

def get_gendict_tally(gendict: dict[str, list]) -> list:
    """
    returns genetic letter tally list for a gendictionary, (dict[str, list])
    this list is 26 members where each member corresponds to the count for
    that letter position idx 0-25 where idx 0=a and idx 25=z
    @param gendict:
    @return:
    """
    gen_tally = []
    for x in range(26):
        gen_tally.append(0)
    # loop through each gencode values list
    for gencode in gendict.values():
        # looking at just the list's a...z letter presence value,
        # add them up
        for idx in range(26):
            if gencode[idx] > 0:
                gen_tally[idx] = gen_tally[idx] + gencode[idx]
    return gen_tally

def assign_genrank(gendict: dict[str, list], gen_tally: list) -> int:
    """
    Places the product sums of gendict values and the gen_tally vector. This value is
    the genetic rank for the gendict words (the keys). The genetic rank is injected into
    the gendict value vector as the 27th item of the 1 x 27 value vector. The maximum
    genetic rank calculated is the integer being returned.
    @param gendict: dictionary of words (keys) with values being 1 x 27 letter count vectors
    @param gen_tally: 1 x 26 vector of letter tallies
    @return: maximum genetic rank seen as integer
    """
    maxrank = 0
    for w, g in gendict.items():
        gr = 0
        for idx in range(26):
            gr = gr + g[idx] * gen_tally[idx]
        gr = gr + g[26]
        new_g = g
        new_g[27] = gr
        if gr > maxrank:
            maxrank = gr
        gendict.update({w: new_g})
    return maxrank

def get_maxgenrankers(gendict: dict[str, list], maxrank: int) -> list:
    """
    returns list of the max genrankers in the gendict
    @param gendict: dict[str, list]
    @param maxrank: int
    @return:
    """
    max_rankers = []
    for w, g in gendict.items():
        if maxrank == g[27]:
            max_rankers.append(w)
    return max_rankers

def regex_maxgenrankers(max_rankers: list, wordsdict: dict) -> str:
    """
    returns a regex formatted pattern string for highlighting
    @param max_rankers:
    @param wordsdict:
    @return:
    """
    pat_list = []
    mid_div = " : "
    for w in max_rankers:
        r = wordsdict[w]
        pat_list.append(w + mid_div + r)
    regex_str = '|'.join(pat_list)
    return regex_str

def analyze_pick_to_solution(sol_wrd: str, pick: str, excl_lst: list, x_pos_dict: dict,
                             r_pos_dict: dict):
    """
    This function is used by fmwm.py only. This function determines what and how a guess
    matches against a target solution. The parameters returned are used to grep filter the
    current remaining word list to be the next remaining word list according how the guess
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
    p_ltr_pos: int = 0 # Current letter position in the pick (pick letter)
    # Multiple same letter accounting is required to filter for multiple same letter
    # instances when they are called for. The user is expected to make that determination
    # in the GUI pywt.py. That determination needs to be coded for fmwm.py.
    multi_clues = MultiClues()  # class for multiple same letter accounting
    for p_ltr in pick:
        # First check for a p_ltr instance.
        if sol_wrd.find(p_ltr) < 0:
            # p_ltr has no matches
            # This must be a GRAY letter.
            if not excl_lst.__contains__(p_ltr):
                excl_lst.append(p_ltr)
            # done with this letter
            # keep track of index position
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
            # Update number of clues for this letter.
            multi_clues.add_multi_ltr_instance(p_ltr)
        else:
            # This must be a YELLOW clue
            # Add p_ltr and p_ltr's position to the exclude position dictionary.
            x_pos_dict[key] = key
            # Check if p_ltr is also elsewhere. If not, then this is only an exclusion clue.
            # Otherwise, there is also a multiple same letter requirement.
            if sol_wrd.count(p_ltr) > 1:
                # There are more p_ltr in the word.
                # Increase the number of required instances for this letter. The grep command assembly
                # will fill out the multiple same letter regex necessary for including the multiple
                # same letter words.
                multi_clues.add_multi_ltr_instance(p_ltr)
        # keep track of index position
        p_ltr_pos += 1
    # end for

    return [excl_lst, x_pos_dict, r_pos_dict, multi_clues.as_code()]

class MultiClues:
    """
    Multiple same letters accounting and functions
    """
    def __init__(self):
        self.multi_clues: dict[str, int] = {}  # dict for multiple same letter accounting

    def add_multi_ltr_instance(self,pl):
        if pl in self.multi_clues:
            self.multi_clues[pl] = self.multi_clues[pl] + 1
        else:
            self.multi_clues[pl] = 1

    def as_code(self) -> str:
        lst = []
        for ltr in self.multi_clues:
            if self.multi_clues[ltr] > 1:
                code = str(self.multi_clues[ltr]) + ltr
                lst.append(code)
        return ','.join(lst)

def build_x_pos_grep(lself, this_pos_dict: dict, rq_lts: str):
    """Builds the grep line for excluding positions
    """
    # example 'grep -vE \'..b..\'' for b,3
    sort_by_key_dict = {}
    for j in sorted(this_pos_dict):
        sort_by_key_dict[j] = this_pos_dict[j]
    for x in sort_by_key_dict:
        parts = this_pos_dict[x].split(',')
        ltr = parts[0].lower()
        p = int(parts[1])
        if rq_lts.__contains__(ltr):
            # add without the requirement, it has been done already
            lself.tool_command_list.add_excl_pos_cmd(ltr, p, False)
        else:
            # add with the requirement
            lself.tool_command_list.add_excl_pos_cmd(ltr, p, True)
            # keep track of its require in this function
            rq_lts += ltr

def build_r_pos_grep(lself, this_pos_dict: dict) -> str:
    """Builds the grep line for including positions
    """
    # example 'grep -vE \'..b.a\'' for (b,3) (a,5)
    pat = ''
    pos = 1
    if len(this_pos_dict) < 1:  # no grep required
        return pat

    # first make a dictionary of the dictionary sorted by the position number
    tlist = sorted(this_pos_dict.items(), key=lambda lx: lx[1].split(',')[1])
    sorted_by_pos_dict = dict(tlist)

    for x in sorted_by_pos_dict:
        parts = sorted_by_pos_dict[x].split(',')
        ltr = parts[0].lower()
        p = int(parts[1])
        while pos < p:
            pat = pat + '.'
            pos += 1
        pat = pat + ltr
        pos += 1

    # fill out the trailing undefined positions
    while len(pat) < 5:
        pat = pat + '.'
    lself.tool_command_list.add_type_cmd(pat, True)
    return pat

def build_multi_code_grep(lself, this_multi_code: str) -> None:
    lself.tool_command_list.add_type_mult_ltr_cmd(this_multi_code.lower(), 1)

def load_grep_arguments(wordle_tool_cmd_lst, excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict, multi_code: str):
    """
    The filter builder. Used only by fmwm.py.
    Filter arguments for each type are added to the grep command argument list
    @param wordle_tool_cmd_lst: the shell command list object
    @param excl_l: exclude letters list
    @param requ_l: required letters list
    @param x_pos_dict: excluded letter position dictionary
    @param r_pos_dict: required letter position dictionary
    @param multi_code: coded multiple same letters string
    """
    pipe = "|"
    pipe2 = "| "
    # Builds the grep line for excluding letters
    # example 'grep -vE \'b|f|k|w\''
    if len(excl_l) > 0:
        args = pipe.join(excl_l)
        grep_exclude = f"grep -vE \'{args}\'"
        wordle_tool_cmd_lst.tool_command_list.add_cmd(grep_exclude)

    # Builds the grep line for requiring letters
    # Each letter gets its own grep
    if len(requ_l) > 0:
        items = []
        for ltr in requ_l:
            items.append(f"grep -E \'{ltr}\'")
        grep_require_these = pipe2.join(items)
        wordle_tool_cmd_lst.tool_command_list.add_cmd(grep_require_these)

    # Build exclude from position, but require
    rq_ltrs = "".join(requ_l)
    build_x_pos_grep(wordle_tool_cmd_lst, x_pos_dict, rq_ltrs)

    # Build require at position
    build_r_pos_grep(wordle_tool_cmd_lst, r_pos_dict)

    # build for the coded multiple letters
    if len(multi_code) > 0:
        build_multi_code_grep(wordle_tool_cmd_lst, multi_code.lower())

def get_genpattern(subject_word: str, target_word: str) -> str:
    """
    Return a subject word's genetic pattern against a target guess word
    example:heavy against leash is the string 12200 pattern
    @param subject_word: The word to check against the guess word.
    @param target_word: The guess word
    @return: String pattern representing each digit in the subject word where
    0 = letter not present, 1 = letter present but not this position and
    2 = letter present at correct position
    """
    ltr_pos = [0, 1, 2, 3, 4]
    genpat = '00000'

    # dictionary of subject sltr instances in target. sltr is key, value is sltr positions
    subj_in_target_dict = {}
    for sltr in subject_word:
        subj_in_target = ([pos for pos, char in enumerate(target_word) if char == sltr])
        if subj_in_target:
            subj_in_target_dict[sltr] = subj_in_target

    rec_pos = ltr_pos.copy()
    # first find all ltr matches, mark as 2s and remove their positions
    # from rec_pos and the subject_in_target dictionary
    for slp in ltr_pos:
        sl = subject_word[slp]
        if subject_word[slp] == target_word[slp]:
            genpat = genpat[:slp] + '2' + genpat[slp + 1:]
            rec_pos.remove(slp)
            subj_in_target_dict[sl].remove(slp)
            if not subj_in_target_dict[sl]:
                subj_in_target_dict.pop(sl)

    # rec_pos now holds only the positions needing further examination
    for slp in rec_pos:
        sl = subject_word[slp]
        if sl in subj_in_target_dict:
            genpat = genpat[:slp] + '1' + genpat[slp + 1:]
            subj_in_target_dict[sl].pop(0)
            if not subj_in_target_dict[sl]:
                subj_in_target_dict.pop(sl)

    return genpat

def outcomes_for_this_guess(guess_word: str, word_list: list) -> dict:
    """
    Returns a dictionary of the word outcomes the guess_word would result
    from applying the guess_word on the word_list. The key values will be
    five-digit codes where 0 means letter is not present, 1 letter is present
    but at wrong position and 2 means letter is present and in correct position.
    @param guess_word: target word
    @param word_list: list of subject words
    @return: The keys will be five-digit codes where 0 means letter is
    not present, 1 letter is present but at wrong position and 2 means letter
    is present and in correct position. Values are the words categorized by that code.
    """
    outcomes_dict = {}
    for subject_word in word_list:
        # This appears to be the correct title_context.
        genpat = get_genpattern(guess_word, subject_word)
        if genpat not in outcomes_dict:
            outcomes_dict[genpat] = [subject_word]
        else:
            outcomes_dict[genpat].append(subject_word)
    return outcomes_dict

def get_outcomes_stats(the_outcomes_dict: dict) -> tuple[int, int, int, float, float, float, float]:
    """
    Given a single guess's outcome dictionary, returns stats:
    outcome pattern quantity,
    smallest outcome pattern size,
    largest outcome pattern size,
    average outcome pattern size,
    outcome population variance,
    outcome entropy,
    outcome expected size
    @param the_outcomes_dict: dictionary for a single guess outcome
    @return: tuple - [0] qty, [1] smallest, [2] largest, [3] ave, [4] var, [5] ent, [6] exp outcome size
    """
    g_qty = len(the_outcomes_dict)  # number of outcomes
    smallest = g_qty  # smallest outcome size
    largest = 0  # largest outcome size
    sums = 0  # outcome size sums, this is the number of words
    p2 = 0.0  # outcome population variance
    g_ent = 0.0  # outcomess entropy
    g_xa = 0.0 # outcomes expected average
    for k, v in the_outcomes_dict.items():
        size = len(v)
        sums = sums + size
        largest = max(largest, size)
        smallest = min(smallest, size)
    # mean = group average size
    mean = sums / g_qty
    for k, v in the_outcomes_dict.items():
        size = len(v)
        p2 += (size - mean) ** 2
        i_p = size / sums
        i_entropy = -(i_p * math.log(i_p, 2))
        g_ent = g_ent + i_entropy
        g_xa = g_xa + size * i_p
    p2 /= g_qty
    return g_qty, smallest, largest, mean, p2, g_ent, g_xa

def outcomes_stat_summary(best_rank_dict: dict) -> tuple[int, int, int, float, float, float, float]:
    """
    Summarizes the outcomes best_rank_dictionary, mainly to extract the
    minimum and maximum group sizes
    @param best_rank_dict:
    @return: outcomes_stat_summary tuple:
    [0]:qty,[1]:smallest,[2]:largest,[3]:average,
    [4]:population variance,[5]:entropy bits,all as a tuple
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
    g_stats = best_rank_dict[list(best_rank_dict.keys())[0]]
    optimal_rank = g_stats[3]
    grps_qty = g_stats[0]
    min_grp_size = g_stats[2]  # Seed with a member's largest
    max_grp_size = g_stats[2]  # The min_max is desired. Seed with a member's largest
    min_grp_p2 = g_stats[4]  # Seed with member's variance
    max_grp_ent = 0.0
    min_grp_xa = g_stats[6] # Seed with member's expected average
    for g_stats in best_rank_dict.values():
        (_, min_stat, max_stat, _, p2_stat, e_stat, xa_stat) = g_stats
        min_grp_size = min(min_stat, min_grp_size)
        max_grp_size = min(max_stat, max_grp_size)  # The min_max is desired.
        min_grp_p2 = min(p2_stat, min_grp_p2)
        max_grp_ent = max(max_grp_ent, e_stat)
        min_grp_xa = min(min_grp_xa, xa_stat)
        # outcomes_stat_summary are:[0]:qty,[1]:smallest,[2]:largest,[3]:average,
        # [4]:min p2,[5]:max entropy bit as a tuple
    return grps_qty, min_grp_size, max_grp_size, optimal_rank, min_grp_p2, max_grp_ent, min_grp_xa

def extended_best_outcomes_guess_dict(remaining_word_lst: list, reporting: bool, byentonly: bool,
                                      cond_rpt: bool, keyed_rpt: bool,
                                      guess_targets: dict,
                                      report_header_msg1: str, title_context: str) -> dict:
    """
    Wraps guess word outcome ranking to return the best
    outcome rank guesses. Guesses resulting in more outcomes
    and smaller outcomes are better guesses.
    @param remaining_word_lst: the remaining solutions word list
    @param reporting: flag for verbose printing to rptwnd
    @param byentonly: flag to return only the highest entropy guesses
    @param cond_rpt: flag for condensed verbose printing to rptwnd
    @param keyed_rpt: flag for keyed by word verbose printing to rptwnd
    @param guess_targets: guess vocabulary dictionary
    @param report_header_msg1: msg string put in verbose report header
    @param title_context: String used in title so indicate owner
    @return: dictionary of the best group ranked guesses
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
        guess_outcomes_dict = outcomes_for_this_guess(guess, remaining_word_lst)
        # outcome_stats are: [0]:qty, [1]:smallest, [2]:largest,
        # [3]:average , [4]:population variance , [5]:entropy as a tuple
        outcome_stats = get_outcomes_stats(guess_outcomes_dict)

        if reporting:
            clue_pattern_outcomes_to_window(guess, outcome_stats, guess_outcomes_dict, rptwnd, cond_rpt, keyed_rpt)
            # saving the condensed stats for later sorting
            if cond_rpt:
                cond_dict[guess] = outcome_stats
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
        guess_rank_dict[guess] = outcome_stats
        # Record the smallest outcome pattern average size. (essentially max outcome qty)
        min_score = min(outcome_stats[3], min_score)
        # Record the maximum entropy seen
        max_ent = max(outcome_stats[5], max_ent)

    # Populate the best_rank_dict with the best guesses.
    # This dictionary's values are outcome_stats tuples.
    for g, s in guess_rank_dict.items():
        # if not only by entropy, then include all with
        # minimum average outcome size (max outcome size)
        if not byentonly:
            if math.isclose(s[3], min_score):
                if g not in best_rank_dict:
                    best_rank_dict[g] = s
        # Also collect the max_ent instances, these are not
        # always with max group size.
        if math.isclose(s[5], max_ent):
            if g not in best_rank_dict:
                best_rank_dict[g] = s

    # make a new dict that is best_rank_dict sorted by ent size
    inorder_best_rank_dict = dict(sorted(best_rank_dict.items(), key=lambda item: item[1][5], reverse=True))
    # Reporting only the best ranking guesses.
    if reporting:
        report_footer_wrapper(report_header_msg1, remaining_word_lst, inorder_best_rank_dict, rptwnd, cond_rpt)
        if cond_rpt:
            report_sorted_cond_guess_stats_to_window(cond_dict, rptwnd)

    return inorder_best_rank_dict

def best_outcomes_from_showing_as_guess_dict(remaining_word_lst: list, reporting: bool, byentonly: bool,
                                             cond_rpt: bool, keyed_rpt: bool,
                                             title_context: str) -> dict:
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
        # always with max group size.
        if math.isclose(s[5], max_ent):
            if g not in best_stat_dict:
                best_stat_dict[g] = s

    # make a new dict that is best_stat_dict sorted by ent size
    inorder_best_rank_dict = dict(sorted(best_stat_dict.items(), key=lambda item: item[1][5], reverse=True))
    # Reporting only the best ranking guesses.
    if reporting:
        report_footer_wrapper("Words Showing", remaining_word_lst, inorder_best_rank_dict, rptwnd, cond_rpt)
        if cond_rpt:
            report_sorted_cond_guess_stats_to_window(cond_dict, rptwnd)

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

    if debug_mode:
        print(f'Working with {len(targets_word_lst)} remaining possibles. '
              f'Pulling guesses from a {len(guess_word_lst)} guess list.')


    for guess in guess_word_lst:
        guess_outcomes_dict = outcomes_for_this_guess(guess, targets_word_lst)
        outcomes_stats = get_outcomes_stats(guess_outcomes_dict)
        # outcome_stats tuple is: [0]:qty, [1]:smallest, [2]:largest, [3]:average,
        # [4]:population variance, [5]:entropy, [6] expected outcome size

        guess_stat_dict[guess] = outcomes_stats

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
        best_stats_found_dict =  best_desired_dict
        if debug_mode:
            print(f'Using only target best entropy words')

    return best_stats_found_dict

def report_footer_wrapper(msg1: str, word_lst: list, best_rank_dict: dict, rptwnd: ctk, cond_rpt: bool):
    report_footer_summary_header_to_window(msg1, word_lst, rptwnd)
    report_footer_stats_summary_to_window(best_rank_dict, rptwnd)
    report_footer_opt_wrds_to_window(best_rank_dict, rptwnd)
    if not cond_rpt:
        report_footer_optimal_wrds_stats_to_window(best_rank_dict, rptwnd)
    rptwnd.back_to_summary()

def report_footer_summary_header_to_window(msg: str, source_list: any, rptwnd: ctk):
    rptl = "\n\n> >  Groups summary using the " + msg + " words for guesses on the " + \
           '{0:.0f}'.format(len(source_list)) + " words.  < <"
    rptwnd.verbose_data.insert(tk.END, rptl)

def prnt_guesses_header(rptwnd: ctk):
    rptl = '\n\nguess' + '\tqty' + \
           '\tent' + \
           '\tmin' + \
           '\tmax' + \
           '\tave' + \
           '\texp' + \
           '\tp2'
    rptwnd.verbose_data.insert(tk.END, rptl)

def reporting_header_to_window(msg: str, source_list: any, rptwnd: ctk):
    rptl = rptwnd.context + " - Pattern Groups For Guesses From The " + msg + " Words List (" + \
           '{0:.0f}'.format(len(source_list)) + ")"
    rptwnd.title(rptl)
    rptl = "> >  " + rptl + "  < <"
    rptwnd.verbose_data.insert(tk.END, rptl)

def report_sorted_cond_guess_stats_to_window(l_cond_dict: dict, rptwnd: ctk) -> None:
    inorder_cond_dict = dict(sorted(l_cond_dict.items(), key=lambda item: item[1][5], reverse=True))
    prnt_guesses_header(rptwnd)
    for g, s in inorder_cond_dict.items():
        (qty, smallest, largest, average, p2, ent, g_xa) = s
        rptl = '\n' + g + '\t' + str(qty) + \
               '\t' + '{0:.3f}'.format(ent) + \
               '\t' + str(smallest) + \
               '\t' + str(largest) + \
               '\t' + '{0:.3f}'.format(average) + \
               '\t' + '{0:.2f}'.format(g_xa) + \
               '\t' + '{0:.2f}'.format(p2)
        rptwnd.verbose_data.insert(tk.END, rptl)

def clue_pattern_outcomes_to_window(guess: any, outcome_stats: tuple, guess_outcomes_dict: dict,
                                    rptwnd: ctk, cond_rpt: bool, keyed_rpt: bool) -> None:
    (qty, smallest, largest, average, p2, ent, g_xa) = outcome_stats
    # report in full or condensed format according to cond_prt flag
    if not cond_rpt:
        rptl = '\n\n> > > > Clue pattern outcomes for: ' + guess + ' < < < < '
        rptwnd.verbose_data.insert(tk.END, rptl)
        rptl = '\n> qty ' + str(qty) + \
               ', ent ' + '{0:.3f}'.format(ent) + \
               ", sizes: min " + str(smallest) + \
               ", max " + str(largest) + \
               ', ave ' + '{0:.2f}'.format(average) + \
               ', exp ' + '{0:.2f}'.format(g_xa) + \
               ', p2 ' + '{0:.2f}'.format(p2)

        rptwnd.verbose_data.insert(tk.END, rptl)
        rptwnd.verbose_data.insert(tk.END, '\n')
        for key in sorted(guess_outcomes_dict):
            g = guess_outcomes_dict[key]
            if keyed_rpt:
                rptl = guess + '  ' + key + ' ' + '{:3d}'.format(len(g)) + ': ' + ', '.join(sorted(g))
            else:
                rptl = key + ' ' + '{:3d}'.format(len(g)) + ': ' + ', '.join(sorted(g))
            rptwnd.verbose_data.insert(tk.END, '\n' + rptl)

def report_footer_stats_summary_to_window(best_rank_dict: dict, rptwnd: ctk):
    rptwnd.verbose_data.insert(tk.END, outcomes_stats_summary_line(best_rank_dict))
    rptwnd.verbose_data.see('end')

def outcomes_stats_summary_line(best_rank_dict: dict) -> str:
    # stats_summary [0]:qty,[1]:smallest,[2]:largest, [3]:average,
    # [4]:population variance, [5]:entropy bits as a tuple
    (g_qty, g_min, g_max, g_ave, g_p2, g_ent, g_xa) = outcomes_stat_summary(best_rank_dict)
    rptl = "\n> >  Maximum group qty " + '{0:.0f}'.format(g_qty) + \
           ", ent " + '{0:.3f}'.format(g_ent) + \
           ", sizes: min " + '{0:.0f}'.format(g_min) + \
           ", min-max " + '{0:.0f}'.format(g_max) + \
           ", ave " + '{0:.3f}'.format(g_ave) + \
           ", exp " + '{0:.2f}'.format(g_xa) + \
           ", p2 " + '{0:.2f}'.format(g_p2)
    return rptl

def report_footer_opt_wrds_to_window(best_rank_dict: dict, rptwnd: ctk):
    rptwnd.verbose_data.insert(tk.END, opt_wrds_for_reporting(best_rank_dict))

def opt_wrds_for_reporting(best_rank_dict: dict) -> str:
    """
    Takes the dictionary of optimal words, which BTW is already sorted by entropy,
    and then uses the dictionary keys, ie the words, to build a sentence for printing out
    the optimal words list.
    @param best_rank_dict: The dictionary of optimal words.
    @return: The string used for printing out the optimal word list.
    """
    wrds = list(best_rank_dict.keys())
    rptl = '\n> >  {0:.0f}'.format(len(wrds)) + ' optimal ent (1st) followed by highest group qty guess words:' + '\n' + ', '.join(wrds)
    return rptl

def report_footer_optimal_wrds_stats_to_window(best_rank_dict: dict, rptwnd: ctk):
    # stats_summary [0]:qty,[1]:smallest,[2]:largest,[3]:average,
    # [4]:population variance,[5]:entropy bits as a tuple
    stats_summary = outcomes_stat_summary(best_rank_dict)
    rptl = '\n> >  Optimal guess stats, each has group qty ' + '{0:.0f}'.format(
        stats_summary[0]) + ' or is max entropy:'
    rptwnd.verbose_data.insert(tk.END, rptl)
    for w, s in best_rank_dict.items():
        (g_qty, g_min, g_max, g_ave, g_p2, g_ent, g_xa) = s
        rptl = "\n" + w + " - " + \
               "qty " + '{0:.0f}'.format(g_qty) + \
               ", ent " + '{0:.3f}'.format(g_ent) + \
               ", min " + '{0:.0f}'.format(g_min) + \
               ", max " + '{0:.0f}'.format(g_max) + \
               ", ave " + '{0:.3f}'.format(g_ave) + \
               ", exp " + '{0:.2f}'.format(g_xa) + \
               ", p2 " + '{0:.3f}'.format(g_p2)
        rptwnd.verbose_data.insert(tk.END, rptl)
        rptwnd.verbose_data.see('end')
    # lock the text widget to prevent user editing
    rptwnd.verbose_data.configure(state='disabled')

def valid_mult_ltr(s: str) -> bool:
    """
    The format requires the letter placed after the number. The mltr_entry_str
    argument will have already been converted to uppercase.
    @param s: The string being checked.
    @return: Returns True if the second character is an uppercase letter A - Z.
    """
    if len(s) != 2:
        return False
    else:
        valid = 'QWERTYUIOPASDFGHJKLZXCVBNM ,'
        return valid.find(s[1]) > -1

def valid_first_mult_number(s: str) -> bool | None:
    """
    The multiple letter requirement would apply to only
    2 or 3 multiple instances for that letter. The format
    requires the number placed before the letter.
    @param s: True if the first character is a 2 or 3.
    """
    if len(s) > 0:
        if s[0] == '2':
            return True
        if s[0] == '3':
            return True
    else:
        return False

def validate_mult_ltr_sets(mltr_entry_str: str) -> str:
    """
    Most definitely very crude!
    Used to conform the user's entry to a specific format.
    Validates the multiple letter specification to be in the
    correct format <number><letter>,<number><letter>.
    @param mltr_entry_str: The multiple letter specification.
    @return: The cleaned entries in a comma separated string
    """
    r = mltr_entry_str
    if len(mltr_entry_str) > 0:
        if mltr_entry_str[-1] == ',':
            return r
        elif mltr_entry_str[-1] == ' ':
            return r.strip(' ') + ','
        else:
            my_list = mltr_entry_str.upper().split(",")
            valid = []
            for s in my_list:
                if len(s) > 0:
                    if valid_first_mult_number(s):
                        if valid_mult_ltr(s):
                            valid.append(s[0] + s[1] + ',')
                        else:
                            valid.append(s[0])
            r = ','.join(valid).replace(',,', ',').strip(',')
    return r

def size_and_position_this_window(self, this_wnd_width: int, this_wnd_height: int,
                                  offset_h: int, offset_w: int) -> None:
    """
    Sets desired window size and location on the screen
    :param self: tk window
    :param this_wnd_height: desired window height
    :param this_wnd_width: desired window width
    :param offset_w: left to right offset
    :param offset_h: up down offset
    """
    pos_x = int((self.winfo_screenwidth() - this_wnd_width) / 2) + offset_w
    pos_y = int((self.winfo_screenheight() - this_wnd_height) / 2) + offset_h
    self.geometry("{}x{}+{}+{}".format(this_wnd_width, this_wnd_height, pos_x, pos_y))

def hard_mode_guesses(default_guesses: dict, req_pat: str, req_ltrs: list) -> dict:
    """
    Returns hard mode guess words from a dictionary of guess words that comply with
    hard mode for green clues as a regex string and yellow clue letters in a list.
    :param default_guesses: dictionary of guess words
    :param req_pat: green clues a regex string
    :param req_ltrs: yellow clues as a list of letters
    :return: hard mode words dictionary
    """
    return dict(filter(lambda x: (hard_mode_func_grn(x, req_pat)
                       and hard_mode_func_yel(x, req_ltrs)),
                       default_guesses.items()))

def hard_mode_func_grn(pair: tuple, req_pat: str) -> bool:
    """
    A function used in a regex filter.
    Given a guess word dictionary tuple and a required green letter pattern,
    returns true if key word matches to green letter pattern.
    :param pair: dictionary key word and its value
    :param req_pat: regex green clue pattern
    :return: True or False
    """
    key, value = pair
    if re.match(req_pat, key):
        return True
    else:
        return False

def hard_mode_func_yel(pair: tuple, req_ltrs: list) -> bool:
    """
    A function used in a regex filter.
    Given a guess word dictionary tuple and a required yellow letters list,
    returns true if key word contains all the yellow letters.
    :param pair: dictionary key word and its value
    :param req_ltrs: yellow letters as a list
    :return: True or False
    """
    key, value = pair
    # return False if anyone fails
    for l in req_ltrs:
        if not re.findall(l,key):
            return False
    return True

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

    def add_type_mult_ltr_cmd(self, mult_ltr_definition: str, typ: int)-> None:
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
                 cull_pu = False,
                 pu_vocab = '') -> None:
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
            pu_wrds = get_pu_wordlist(get_word_list_path_name(self.data_path + self.pu_vocab, False))
            cull_sol_list(wrds,pu_wrds)
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
                          regexp=True, remove_priors=True, do_scroll=True, mode=0):
        """Apply the given tag to all text that matches the given pattern
        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        mode=1 finds only first match
        :param pattern: text to find, can be regex expression
        :param tag: highlight color tag
        :param start: start position
        :param end: end position
        :param regexp: use regex
        :param remove_priors:  remove all prior highlighting
        :param do_scroll: scroll text as it is found
        :param mode: 0=scroll every, 1=scroll only to first found
        """
        if remove_priors:
            self.remove_tag(tag)
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        is_first_pass = True
        not_found = False
        first_index=""
        count = tk.IntVar()
        while True:
            try:
                index = self.search(pattern, "matchEnd", "searchLimit",
                                    count=count, regexp=regexp)
                if index == "":
                    # text not found
                    if is_first_pass:
                        # if first pass then text cannot be found
                        # so set not_found flag
                        not_found=True
                    # stop searching
                    break
                else:
                    # text was found
                    if first_index == "":
                        # text found must be the first found
                        # save first found index so that it can be scrolled
                        # to instead of scrolling to the last found.
                        first_index = index
                        # no longer in first pass
                        is_first_pass=False
                        if mode == 1:
                            # only the first match is sought. This is specifically
                            # used to return to the Groups Summary text for one of the
                            # report types
                            break
                if count.get() == 0:
                    break  # degenerate pattern which matches zero-length strings
                self.mark_set("matchStart", index)
                self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
                self.tag_add(tag, "matchStart", "matchEnd")
                if do_scroll:
                    self.see(index)  # scroll widget to show the index's line
            except Exception as e:
                msg = (f"Regex error: \"{e}\".")
                messagebox.showinfo(title=None, message=msg)
                break

        if not_found:
            msg = (f"Did not find \"{pattern}\"."
                   f"\n\nThe word that was searched is not in the vocabulary that was used for guesses."
                   f"\n\nIs Hard Mode selected? Hard Mode excludes guesses from the vocabulary.")
            messagebox.showinfo(title=None, message=msg)
        else:
            self.see(first_index)

class RptWnd(ctk.CTkToplevel):
    """
    The verbose information window
    """

    def clear_msg1(self) -> None:
        self.verbose_data.configure(state='normal')
        self.verbose_data.delete(1.0, tk.END)
        self.verbose_data.configure(state='disabled')

    def close_rpt(self) -> None:
        self.destroy()

    def search_for_text(self):
        self.find_the_text()

    def entry_release_return(self, event):
        self.find_the_text()

    def find_the_text(self):
        org_title =  self.title()
        find_text = ''
        regex: find_text = self.search_text.get().strip()
        self.title(f"> > Busy on \"{regex}\", Please Wait < <")
        self.update()
        if len(regex) > 4:
            self.verbose_data.highlight_pattern(regex, 'grp', remove_priors=True, mode=0)
        else:
            msg = (f"Search for \"{regex}\"?\n\nIn a verbose report one usually searches for a five letter guess word"
                   f" preceded by \"for:\", which is then very quickly highlighted.\n\nThe same, but without \"for:\","
                   f" is typical in the condensed verbose report.\n\nSearch can accept any text, including a regex"
                   f" pattern. A regex pattern can do most of the work required to find hard mode candidates in the condensed"
                   f" list..\n\nFor example, \"^.t..p\" would indicate words where t and p are at those positions. The "
                   f"\"^\" is important. It indicates the next character \".\", which means any character, must be at"
                   f" the text beginning. Thus five letter words and not parts of larger words are highlighted."
                   f"\n\nThe time it takes to highlight the search depends on the amount of text to search and the "
                   f"number of items to be highlighted.")
            if messagebox.askokcancel(title=None, message=msg):
                self.verbose_data.highlight_pattern(regex, 'grp', remove_priors=True, mode=0)
        self.title(org_title)
        self.update()

    def back_to_summary(self):
        """
        Scrolls the window to the part that says 'Groups summary'. It does
        this by highlighting the text, which causes the scroll, and then removes
        the highlight pattern.
        """
        search_text = ''
        regex: search_text = 'Groups summary'
        self.verbose_data.highlight_pattern(regex, 'grp', remove_priors=True, mode=1)
        self.verbose_data.remove_tag('grp')

    def rpt_show_grps_driller(self) -> None:
        if self.rpt_grpsdriller_window is None or not self.rpt_grpsdriller_window.winfo_exists():
            self.rpt_grpsdriller_window = groupdrilling.GrpsDrillingMain()  # create window if its None or destroyed
        else:
            self.rpt_grpsdriller_window.focus()  # if window exists focus it

    def __init__(self, context=''):
        super().__init__()
        self.context = context
        self.resizable(width=True, height=True)
        size_and_position_this_window(self, 790, 600, 0, 0)

        verbose_font_tuple_n = ("Helvetica", 14, "normal")
        self.option_add("*Font", verbose_font_tuple_n)

        self.search_text = tk.StringVar()
        self.search_text.set('for: ')
        self.rpt_grpsdriller_window = None

        self.verbose_info_frame = ctk.CTkFrame(self,
                                               corner_radius=10
                                               )
        self.verbose_info_frame.pack(fill='both',
                                     padx=2,
                                     pady=0,
                                     expand=True
                                     )
        self.verbose_info_frame.grid_columnconfigure(0, weight=1)  # non-zero weight allows grid to expand
        self.verbose_info_frame.grid_rowconfigure(0, weight=1)  # non-zero weight allows grid to expand

        self.verbose_data = CustomText(self.verbose_info_frame,
                                       wrap='word',
                                       font=("Courier", 14, "normal"),
                                       padx=6,
                                       pady=6,
                                       background='#dedede',
                                       borderwidth=0,
                                       highlightthickness=0
                                       )
        self.verbose_data.grid(row=0, column=0, padx=6, pady=0, sticky='nsew')
        self.verbose_data.tag_configure('grp', background='#ffd700')
        # scrollbar for rpt
        verbose_rpt_sb = ttk.Scrollbar(self.verbose_info_frame, orient='vertical')
        verbose_rpt_sb.grid(row=0, column=1, sticky='ens')

        self.verbose_data.config(yscrollcommand=verbose_rpt_sb.set)
        verbose_rpt_sb.config(command=self.verbose_data.yview)

        button_q = ctk.CTkButton(self, text="Close",
                                 text_color="black",
                                 command=self.close_rpt)
        button_q.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.close_rpt)  # assign to closing button [X]

        entry_find = ctk.CTkEntry(self,
                                  textvariable=self.search_text
                                  )
        entry_find.pack(side=tk.LEFT, padx=10, pady=10)
        entry_find.bind('<KeyRelease-Return>', self.entry_release_return)

        button_f = ctk.CTkButton(self, text="Find",
                                 text_color="black",
                                 command=self.search_for_text
                                 )
        button_f.pack(side="left", padx=0, pady=10)

        button_drill = ctk.CTkButton(self, text="Groups Driller",
                                     text_color="black",
                                     width=40, command=self.rpt_show_grps_driller)
        button_drill.pack(side=tk.RIGHT, padx=4, pady=3, fill=tk.X, expand=True)

        button_b = ctk.CTkButton(self, text="Summary",
                                 text_color="black",
                                 command=self.back_to_summary
                                 )
        button_b.pack(side="left", padx=10, pady=10)

class HelpWindow(ctk.CTkToplevel):
    """
    The help information window
    """

    def close_help(self) -> None:
        self.destroy()

    def get_rank_data(self) -> str:
        """
        @return: Returns string that is the information
        """
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, self.letter_rank_file)
        if os.path.exists(full_path_name):
            f = open(full_path_name, "r", encoding="UTF8").read()
        else:
            f = 'Could not find. ' + str(full_path_name)
        return f

    def get_info(self) -> str:
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, 'helpinfo.txt')
        if os.path.exists(full_path_name):
            f = open(full_path_name, "r", encoding="UTF8").read()
        else:
            f = 'This is all the help you get because file helpinfo.txt has gone missing.'
        return f

    def show_info(self) -> None:
        self.help_msg.configure(state='normal')
        self.help_msg.delete(1.0, tk.END)
        self.help_msg.insert(tk.END, self.get_info())
        self.help_msg.configure(state='disabled')

    def show_rank_info(self) -> None:
        self.help_msg.configure(state='normal')
        self.help_msg.delete(1.0, tk.END)
        raw_rank_data = self.get_rank_data()
        f = raw_rank_data.replace(":", "\t")
        self.help_msg.insert(tk.END, "Using file: " + self.letter_rank_file + "\n")
        self.help_msg.insert(tk.END, "RNK = Rank for any occurrence\n")
        self.help_msg.insert(tk.END, "RNK-X = Rank at position X in the word\n\n")
        self.help_msg.insert(tk.END, "LTR\tRNK\tRNK-1\tRNK-2\tRNK-3\tRNK-4\tRNK-5\n")
        self.help_msg.insert(tk.END, "---\t---\t-----\t-----\t-----\t-----\t-----\n")
        self.help_msg.insert(tk.END, f)
        self.help_msg.configure(state='disabled')

    def __init__(self, data_path, letter_rank_file):
        super().__init__()
        self.data_path = data_path
        self.letter_rank_file = letter_rank_file
        self.resizable(width=True, height=True)
        self.title('Some Information For You')
        help_wd = 530
        help_ht = 500
        size_and_position_this_window(self, help_ht, help_wd, 0, 0)

        # configure style
        style = ttk.Style()
        style.theme_use()
        help_font_tuple_n = ("Courier", 14, "normal")
        self.option_add("*Font", help_font_tuple_n)

        self.help_info_frame = tk.Frame(self,
                                        borderwidth=0
                                        )
        self.help_info_frame.pack(side=tk.TOP, fill='both', padx=2, pady=0, expand=True)
        self.help_info_frame.grid_rowconfigure(0, weight=1)
        self.help_info_frame.grid_columnconfigure(0, weight=1)

        self.help_msg = tk.Text(self.help_info_frame,
                                wrap='word',
                                padx=10,
                                pady=8,
                                background='#dedede',
                                borderwidth=0,
                                highlightthickness=0
                                )
        self.help_msg.grid(row=0, column=0, padx=6, pady=0, sticky="nsew")


        # scrollbar for help
        help_sb = ttk.Scrollbar(self.help_info_frame, orient='vertical')
        help_sb.grid(row=0, column=1, padx=1, pady=2, sticky='ens')
        self.help_msg.config(yscrollcommand=help_sb.set)
        help_sb.config(command=self.help_msg.yview)
        self.show_info()

        button_q = ctk.CTkButton(self, text="Close",
                                 text_color="black",
                                 command=self.close_help)
        button_q.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.close_help)  # assign to closing button [X]

        button_r = ctk.CTkButton(self, text="Letter Ranking",
                                 text_color="black",
                                 command=self.show_rank_info
                                 )
        button_r.pack(side="left", padx=10, pady=10)

        button_i = ctk.CTkButton(self, text="Information",
                                 text_color="black",
                                 command=self.show_info
                                 )
        button_i.pack(side="left", padx=10, pady=10)
