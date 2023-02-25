# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
from subprocess import Popen, PIPE
import sys
import os
import random
import tkinter as tk  # assigns tkinter stuff to tk namespace
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
from tkinter import messagebox
from typing import NoReturn

import customtkinter as ctk

gc_z = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


# Returns the wordle word list full pathname
# Exits program if not found
def get_word_list_path_name(local_path_file_name: str) -> str:
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_file_name)
    if os.path.exists(full_path_name):
        # print("Using " + local_path_file_name)
        return full_path_name
    else:
        msg = 'The wordle word list file ' \
              + local_path_file_name \
              + ' was not found.' \
              + ' Expected here:' + full_path_name
        print(msg)
        print()
        messagebox.showerror(title='Stopping Here', message=msg)
        sys.exit()


# ===== Start - Letter ranking functions for rank that includes by letter position method
# Make and return the letter ranking dictionary
def make_ltr_rank_dictionary(local_path_rank_file: str) -> dict:
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_rank_file)
    ltr_rank_dict = {}  # ltr_rank_dict will be the rank dictionary
    if os.path.exists(full_path_name):
        # print("Using " + local_path_rank_file)
        with open(full_path_name) as f:
            for ltr in f:
                ltr = ltr.split(":")
                ltr[-1] = ltr[-1].strip()
                k = ltr[0]
                ltr.pop(0)
                ltr_rank_dict[k] = [float(d) for d in ltr]  # want as floats
    else:
        msg = "Letter ranking file " \
              + local_path_rank_file \
              + " not found. Switching to built in letter ranking."
        print(msg)
        messagebox.showwarning('Warning', message=msg)
        ltr_rank_dict = {
            "e": [39.0, 2.28, 7.64, 5.61, 10.08, 13.38],
            "a": [33.6, 4.82, 10.46, 10.46, 10.53, 5.58, 2.17],
            "r": [30.9, 3.62, 9.21, 9.21, 5.62, 5.17, 7.31],
            "o": [24.9, 1.36, 9.22, 9.22, 8.03, 4.36, 1.92],
            "t": [24.7, 5.05, 2.61, 2.61, 3.76, 4.71, 8.57],
            "i": [23.9, 1.21, 7.18, 7.18, 9.50, 5.64, 0.39],
            "l": [23.9, 2.90, 6.67, 6.67, 3.74, 5.41, 5.17],
            "s": [22.9, 12.49, 0.55, 0.55, 2.74, 5.85, 1.23],
            "n": [20.3, 1.31, 3.08, 3.08, 4.85, 6.45, 4.60],
            "u": [16.9, 1.20, 6.70, 6.70, 5.98, 2.97, 0.04],
            "c": [16.5, 6.89, 1.39, 1.39, 1.95, 5.22, 1.08],
            "y": [15.4, 0.22, 0.80, 0.80, 1.05, 0.11, 13.23],
            "h": [14.0, 2.49, 5.20, 5.20, 0.32, 1.01, 4.94],
            "d": [13.7, 3.87, 0.70, 0.70, 2.62, 2.41, 4.11],
            "p": [12.8, 4.94, 2.14, 2.14, 2.00, 1.75, 1.96],
            "g": [11.1, 4.11, 0.39, 0.39, 2.39, 2.71, 1.46],
            "m": [11.0, 3.74, 1.33, 1.33, 2.13, 2.38, 1.47],
            "b": [9.9, 6.13, 0.57, 0.57, 1.91, 0.85, 0.39],
            "f": [7.6, 4.50, 0.27, 0.27, 0.83, 1.17, 0.87],
            "k": [7.5, 0.71, 0.36, 0.36, 0.43, 1.96, 4.03],
            "w": [7.1, 3.02, 1.62, 1.62, 0.96, 0.92, 0.63],
            "v": [5.5, 1.55, 0.54, 0.54, 1.77, 1.62, 0.00],
            "x": [1.4, 0.00, 0.52, 0.52, 0.44, 0.11, 0.30],
            "z": [1.3, 0.10, 0.06, 0.06, 0.36, 0.65, 0.13],
            "q": [1.1, 0.85, 0.19, 0.19, 0.04, 0.00, 0.00],
            "j": [1.0, 0.74, 0.07, 0.07, 0.11, 0.07, 0.00],
        }
    return ltr_rank_dict


# Returns a word's letter frequency ranking
def wrd_rank(wrd, ltr_rank_dict, method) -> float:
    # Any word longer than 5 letters has undefined rank.
    # This allows for wordlist flexibility,
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


# Returns true if word has duplicate letters
def wrd_has_duplicates(wrd) -> bool:
    ltr_d = {}
    # This function is also used for the special pattern
    # where '.' is allowed. These would not be duplicates.
    wrd = wrd.replace('.', '')
    wrd = wrd.replace(' ', '')
    for ltr in wrd:
        ltr_d[ltr] = ltr
    return len(ltr_d) < len(wrd)


# List out the ranked word list into n_col columns.
def print_word_list_col_format(the_word_list, n_col) -> NoReturn:
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


# Ranking and filtering the words into a dictionary.
# Returns that dictionary sorted by the word rank.
def make_ranked_filtered_result_dictionary(wrds: list, ltr_rank_dict: dict, allow_dups: bool,
                                           rank_mode: int, no_rank=False) -> dict:
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
    # return dict(sorted(wrds_dict.items(), reverse=True,key= lambda x:x[1]))
    if not no_rank:
        return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))
    else:
        return wrds_dict


# Returns the list of words that pass the grep command list
def get_results_word_list(this_sh_cmd_lst) -> list:
    with Popen(this_sh_cmd_lst.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
        return list(map(lambda i: i[: -1], proc.stdout.readlines()))


# Clears the console window
def clear_scrn() -> NoReturn:
    os.system("cls" if os.name == "nt" else "clear")


# returns a regex formatted pattern string for highlighting
def regex_maxgenrankers(max_rankers, wordsdict) -> str:
    pat_list = []
    mid_div = " : "
    for w in max_rankers:
        r = wordsdict[w]
        pat_list.append(w + mid_div + r)
    regex_str = '|'.join(pat_list)
    return regex_str


# Updates the exclude, exclude position and include position filtering according to
# what a pick looks like against the solution word.
def analyze_pick_to_solution(sol: str, pick: str, exclude: list, x_pos_dict: dict,
                             r_pos_dict: dict) -> NoReturn:
    candidate_pos = 0
    for pl in pick:
        if sol.find(pl) < 0:
            if not exclude.__contains__(pl):
                exclude.append(pl)
            # done with this letter
            candidate_pos += 1
            continue
        # pl has instances
        key = pl + ',' + str(candidate_pos + 1)
        value = key
        if candidate_pos != sol.find(pl, candidate_pos):
            # exclude from candidate position
            x_pos_dict[key] = value
        else:
            # include at candidate position
            r_pos_dict[key] = value

        candidate_pos += 1


def build_x_pos_grep(lself, this_pos_dict: dict, rq_lts: str) -> NoReturn:
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
    lself.tool_command_list.add_require_cmd(pat)
    return pat


# The filter builder. filter arguments for each type are addedto the grep command argumentlist
def load_grep_arguments(wordle_tool, excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict):
    pipe = "|"
    pipe2 = "| "
    # Builds the grep line for excluding letters
    # example 'grep -vE \'b|f|k|w\''
    if len(excl_l) > 0:
        args = pipe.join(excl_l)
        grep_exclude = "grep -vE \'" + args + "\'"
        wordle_tool.tool_command_list.add_cmd(grep_exclude)

    # Builds the grep line for requiring letters
    # Each letter gets its own grep
    if len(requ_l) > 0:
        itms = []
        for ltr in requ_l:
            itms.append("grep -E \'" + ltr + "\'")
        grep_require_these = pipe2.join(itms)
        wordle_tool.tool_command_list.add_cmd(grep_require_these)

    # Build exclude from position, but require
    rq_ltrs = "".join(requ_l)
    build_x_pos_grep(wordle_tool, x_pos_dict, rq_ltrs)
    # Build require at position
    build_r_pos_grep(wordle_tool, r_pos_dict)


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


def groups_for_this_guess(guess_word: str, word_list: list) -> dict:
    """
    Returns a dictionary of the word groups the guess_word would result
    from applying the guess_word on the word_list. The key values will be
    five-digit codes where 0 means letter is not present, 1 letter is present
    but at wrong position and 2 means letter is present and in correct position.
    @param guess_word: target word
    @param word_list: list of subject words
    @return: The keys will be five-digit codes where 0 means letter is
    not present, 1 letter is present but at wrong position and 2 means letter
    is present and in correct position. Values are the words categorized by that code.
    """
    groups_dict = {}
    for subject_word in word_list:
        genpat = get_genpattern(subject_word, guess_word)
        if genpat not in groups_dict:
            groups_dict[genpat] = [subject_word]
        else:
            groups_dict[genpat].append(subject_word)
    return groups_dict


def max_group_size(groups_dict: dict) -> tuple:
    """
    Given a group's dictionary, returns the group
    pattern that has the maximum number of words
    and that word count.
    @param groups_dict:
    @return: max group pattern, word count for that pattern
    """
    max_grp = ""
    max_size = 0
    for k, v in groups_dict.items():
        sz = len(v)
        if sz > max_size:
            max_size = sz
            max_grp = k
    return max_grp, max_size


def group_stats(groups_dict: dict) -> tuple:
    """
    Given a guess group's dictionary and the guess, returns group stats:
    pattern group quantity,
    largest pattern group size,
    average pattern group size
    @param groups_dict:
    @return: tuple - quantity, largest, average
    """
    sums = 0
    largest = 0
    qty = len(groups_dict)
    for k, v in groups_dict.items():
        size = len(v)
        sums = sums + size
        largest = max(largest, size)
    return qty, largest, sums / qty


def ave_group_size(groups_dict: dict) -> float:
    """
    Given a group's dictionary, returns the average of
    the group sizes.
    @param groups_dict:
    @return: average as float
    """
    sums = 0
    for k, v in groups_dict.items():
        sz = len(v)
        sums = sums + sz
    return sums / len(groups_dict)


def x_best_groups_guess_dict(word_lst: list, reporting: bool, all_targets: dict) -> dict:
    """
    Wraps guess word group ranking to return the best
    group rank guesses. Guesses resulting in more groups
    and smaller groups are better guesses.
    @param reporting: flag for verbose printing to rptwnd
    @param word_lst: possible guess words
    @return: dictionary of the best group ranked guesses
    """
    guess_rank_dict = {}
    best_rank_dict = {}
    min_score = len(word_lst)

    if reporting:
        rptwnd = RptWnd()
        rptwnd.title("Group Pattern Reporting")
        rptl = "-- Current Vocabulary Words List (" + '{0:.0f}'.format(len(all_targets)) + " words) Pattern Groups --\n"
        rptwnd.msg1.insert(tk.END, rptl)

    for guess in all_targets.keys():
        groups_dict = groups_for_this_guess(guess, word_lst)
        # grp_stats are: qty, largest, average as a tuple
        grp_stats = group_stats(groups_dict)

        if reporting:
            rptl = '\n> > > > Clue pattern groups for: ' + guess + ' < < < < '
            rptwnd.msg1.insert(tk.END, rptl)
            data = tuple(str(x) for x in grp_stats)
            rptl = '\n> qty: ' + data[0] + ', largest size: ' + data[1] + ', average size: ' + '{0:.3f}'.format(
                grp_stats[2])
            rptwnd.msg1.insert(tk.END, rptl)
            rptwnd.msg1.insert(tk.END, '\n')
            for key in sorted(groups_dict):
                g = groups_dict[key]
                rptl = 'pat: ' + key + ', ' + str(len(g)) + ' wrds: ' + ', '.join(g)
                rptwnd.msg1.insert(tk.END, '\n' + rptl)
            rptwnd.msg1.insert(tk.END, '\n')

        # The rank is calculated as the average of the group's sizes.
        # Guesses that have the same number of groups but have a larger
        # , largest group have equal prob. to other guesses having the same
        # average.
        guess_rank_dict[guess] = grp_stats

        # Record the smallest average pattern groups size.
        min_score = min(grp_stats[2], min_score)

    # Populate the best_rank_dict with the best guesses.
    for g, s in guess_rank_dict.items():
        if s[2] == min_score:
            if g not in best_rank_dict:
                best_rank_dict[g] = s

    if reporting:
        wrds = list(best_rank_dict.keys())
        rptl = "\nOut Of Current Vocabulary Words List Of " + '{0:.0f}'.format(len(all_targets)) + " Words"
        rptwnd.msg1.insert(tk.END, rptl)
        rptl = '\nOptimal group guesses: ' + ', '.join(wrds)
        rptwnd.msg1.insert(tk.END, rptl)
        g_stats = best_rank_dict[list(best_rank_dict.keys())[0]]
        optimal_rank = g_stats[2]
        grps_qty = g_stats[0]
        max_grp_size = g_stats[1]
        rptl = "\nGroup qty: " + '{0:.0f}'.format(grps_qty) + \
               ", max size: " + '{0:.0f}'.format(max_grp_size) + \
               ", ave size: " + '{0:.2f}'.format(optimal_rank) + ")"
        rptwnd.msg1.insert(tk.END, rptl)
        rptwnd.msg1.see('end')
    return best_rank_dict


def best_groups_guess_dict(word_lst: list, reporting: bool) -> dict:
    """
    Wraps guess word group ranking to return the best
    group rank guesses. Guesses resulting in more groups
    and smaller groups are better guesses.
    @param reporting: flag for verbose printing to rptwnd
    @param word_lst: possible guess words
    @return: dictionary of the best group ranked guesses
    """
    guess_rank_dict = {}
    best_rank_dict = {}
    min_score = len(word_lst)

    if reporting:
        rptwnd = RptWnd()
        rptwnd.title("Group Pattern Reporting")
        rptl = "-- Current Displayed Words List (" + '{0:.0f}'.format(len(word_lst)) + " words) Pattern Groups --\n"
        rptwnd.msg1.insert(tk.END, rptl)

    for guess in word_lst:
        groups_dict = groups_for_this_guess(guess, word_lst)
        # grp_stats are: qty, largest, average as a tuple
        grp_stats = group_stats(groups_dict)

        if reporting:
            rptl = '\n> > > > Clue pattern groups for: ' + guess + ' < < < < '
            rptwnd.msg1.insert(tk.END, rptl)
            data = tuple(str(x) for x in grp_stats)
            rptl = '\n> qty: ' + data[0] + ', largest size: ' + data[1] + ', average size: ' + '{0:.3f}'.format(
                grp_stats[2])
            rptwnd.msg1.insert(tk.END, rptl)
            rptwnd.msg1.insert(tk.END, '\n')
            for key in sorted(groups_dict):
                g = groups_dict[key]
                rptl = 'pat: ' + key + ', ' + str(len(g)) + ' wrds: ' + ', '.join(g)
                rptwnd.msg1.insert(tk.END, '\n' + rptl)
            rptwnd.msg1.insert(tk.END, '\n')

        # The rank is calculated as the average of the group's sizes.
        # Guesses that have the same number of groups but have a larger
        # , largest group have equal prob. to other guesses having the same
        # average.
        guess_rank_dict[guess] = grp_stats

        # Record the smallest average pattern groups size.
        min_score = min(grp_stats[2], min_score)

    # Populate the best_rank_dict with the best guesses.
    for g, s in guess_rank_dict.items():
        if s[2] == min_score:
            if g not in best_rank_dict:
                best_rank_dict[g] = s

    if reporting:
        wrds = list(best_rank_dict.keys())
        rptl = "\nOut Of Current Displayed Words List Of " + '{0:.0f}'.format(len(word_lst)) + " Words"
        rptwnd.msg1.insert(tk.END, rptl)
        rptl = '\nOptimal group guesses: ' + ', '.join(wrds)
        rptwnd.msg1.insert(tk.END, rptl)
        g_stats = best_rank_dict[list(best_rank_dict.keys())[0]]
        optimal_rank = g_stats[2]
        grps_qty = g_stats[0]
        max_grp_size = g_stats[1]
        rptl = "\nGroup qty: " + '{0:.0f}'.format(grps_qty) + \
               ", max size: " + '{0:.0f}'.format(max_grp_size) + \
               ", ave size: " + '{0:.2f}'.format(optimal_rank) + ")"
        rptwnd.msg1.insert(tk.END, rptl)
        rptwnd.msg1.see('end')
    return best_rank_dict


# A class used for holding list stack of the shell commands
# It has functions that build greps related to filtering wordle
# letter conditions. Some functions are not used in the gui
# pywordletool.
class ShellCmdList:
    # The command list is by instance.
    def __init__(self, list_file_name: str) -> None:
        self.shCMDlist = list()
        self.shCMDlist.append("cat " + list_file_name)

    # Adds string s to the command stack.
    def add_cmd(self, s: str) -> NoReturn:
        if len(s) > 0:
            self.shCMDlist.append(s)

    # Given a string of letters lst, adds to the command
    # stack a grep filter requiring a letter picked at random
    # from string lst. Returns that random picked letter for
    # feedback purposes.
    def add_rand_incl_frm_cmd(self, lst: str) -> str:
        rand_frm_l = random.choice(lst)
        self.shCMDlist.append("grep -E '" + rand_frm_l + "'")
        return rand_frm_l

    # Adds command to stack to require letter ltr.
    def add_require_cmd(self, ltr: str) -> NoReturn:
        if len(ltr) > 0:
            self.shCMDlist.append("grep -E '" + ltr + "'")

    # Adds command to stack to exclude the letter ltr.
    def add_excl_cmd(self, ltr: str) -> NoReturn:
        if len(ltr) > 0:
            self.shCMDlist.append("grep -vE '" + ltr + "'")

    # Adds command to stack to exclude letter from a position number.
    # Context is that letter is known, therefore is required but not
    # at the designated position.
    def add_excl_pos_cmd(self, ltr: str, p: int, add_e: bool) -> NoReturn:
        if len(ltr) > 0:
            # add_E a requirement argument, being managed
            # outside the shCMDList so that the shCMDList
            # does not duplicate the greg -E for any one letter.
            if add_e:  # Require the letter if not already done
                self.shCMDlist.append("grep -E '" + ltr + "'")
            # but not in this position.
            c = 5
            dp = ''.rjust(p - 1, '.')
            dpn = ''.rjust(c - p, '.')
            self.shCMDlist.append("grep -vE '" + dp + ltr + dpn + "'")

    # Adds command to stack to require letter at a position number.
    def add_incl_pos_cmd(self, ltr: str, p: int) -> NoReturn:
        if len(ltr) > 0:
            # Have letter in this position
            c = 5
            dp = ''.rjust(p - 1, '.')
            dpn = ''.rjust(c - p, '.')
            self.shCMDlist.append("grep -E '" + dp + ltr + dpn + "'")

    # Returns the command stack assembled into one command line.
    def full_cmd(self) -> str:
        pipe = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pipe
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd


# ToolResults(data path, vocabulary file name, letter_ranks file, loc_allow_dups)
# The wordle tool all wrapped up into one being, including the grep command list.
class ToolResults:

    def __init__(self, data_path, vocabulary, letter_ranks, allow_dups, rank_mode):
        self.data_path = data_path
        self.vocab = vocabulary  # vocabulary is the words list textfile
        self.ltr_ranks = letter_ranks  # ltr_ranks is the letter ranking textfile
        self.allow_dups = allow_dups  # loc_allow_dups is the-allow-duplicate-letters flag
        self.rank_mode = rank_mode

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

    # Return the results words list without any ranking or sorting.
    def get_results_wrd_lst(self) -> list:
        with Popen(self.tool_command_list.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
            return list(map(lambda i: i[: -1], proc.stdout.readlines()))
        # return os.popen(self.tool_command_list.full_cmd()).read().split("\n")

    # Returns ranked results words list as dictionary. The ranking function also
    # sorts the dictionary. So result is sorted.
    def get_ranked_results_wrd_lst(self, no_rank=False) -> dict:
        # Ranking and filtering the words into a dictionary
        # Set loc_allow_dups to prevent letters from occurring more than once
        # First pick should not use duplicates, later picks should consider them.
        # Exclude all empty string. This can happen at the file end.
        wrds = list(filter(None, self.get_results_wrd_lst()))
        self.ranked_wrds_dict = make_ranked_filtered_result_dictionary(wrds, self.ltr_rank_dict, self.allow_dups,
                                                                       self.rank_mode, no_rank)
        self.ranked_cnt = len(self.ranked_wrds_dict)
        return self.ranked_wrds_dict

    # Return the grepped word count
    def get_results_raw_cnt(self) -> str:
        sh_cmd_for_cnt = self.tool_command_list.full_cmd() + " | wc -l"
        with Popen(sh_cmd_for_cnt, shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
            return proc.stdout.readline().strip()
        # self.raw_cnt = os.popen(sh_cmd_for_cnt).read().strip()
        # return self.raw_cnt

    # Returns the status text line.
    def get_status(self) -> str:
        status = 'Showing ' + str(self.ranked_cnt) + ' words from the ' + str(
            self.get_results_raw_cnt()) + " duplicate letter word list."
        return status

    # Returns the entire fully assembled grep command line. This line includes
    # the full path names.
    def get_full_cmd(self) -> str:
        return self.tool_command_list.full_cmd()

    # Returns the entire fully assembled grep command line. This line excluded
    # the full path names and so is used in the GUI display.
    def get_cmd_less_filepath(self) -> str:
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
        the_word_list = self.get_ranked_results_wrd_lst(no_rank)
        if verbose:
            print()
            if guess_no > 1:
                print('Selection pool for guess ' + str(guess_no) + ' based on guess ' + str(
                    guess_no - 1) + ' => ' + guess_wrd)
            else:
                print('Selection pool for guess ' + str(guess_no))
            print(self.get_status())
            print(self.get_cmd_less_filepath())
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

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=True):
        """Apply the given tag to all text that matches the given pattern
        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "":
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
            self.see(index)  # scroll widget to show the index's line


# The verbose information window
class RptWnd(ctk.CTkToplevel):

    def clear_msg1(self) -> NoReturn:
        self.msg1.configure(state='normal')
        self.msg1.delete(1.0, tk.END)
        self.msg1.configure(state='disabled')

    def close_rpt(self) -> NoReturn:
        self.destroy()

    def __init__(self):
        super().__init__()
        self.resizable(width=True, height=True)
        self.geometry('740x600')

        font_tuple_n = ("Courier", 14, "normal")

        self.info_frame = ctk.CTkFrame(self,
                                       corner_radius=10,
                                       borderwidth=0
                                       )
        self.info_frame.pack(fill='both',
                             padx=2,
                             pady=0,
                             expand=True
                             )
        self.info_frame.grid_columnconfigure(0, weight=1)  # non-zero weight allows grid to expand
        self.info_frame.grid_rowconfigure(0, weight=1)  # non-zero weight allows grid to expand
        self.msg1 = tk.Text(self.info_frame,
                            wrap='word',
                            padx=6,
                            pady=6,
                            background='#dedede',
                            borderwidth=0,
                            highlightthickness=0
                            )
        self.msg1.grid(row=0, column=0, padx=6, pady=0, sticky='nsew')
        self.msg1.configure(font=font_tuple_n)
        # scrollbar for rpt
        rpt_sb = ttk.Scrollbar(self.info_frame, orient='vertical')
        rpt_sb.grid(row=0, column=1, sticky='ens')

        self.msg1.config(yscrollcommand=rpt_sb.set)
        rpt_sb.config(command=self.msg1.yview)

        button_q = ctk.CTkButton(self, text="Close",
                                 command=self.close_rpt)
        button_q.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.close_rpt)  # assign to closing button [X]
