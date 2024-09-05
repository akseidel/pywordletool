# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
from subprocess import Popen, PIPE
import sys
import os
import random
import math
import tkinter as tk  # assigns tkinter stuff to tk namespace
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own
# ttk namespace so that tk is preserved
from tkinter import messagebox
import customtkinter as ctk
import groupdrilling

gc_z = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


# Returns the wordle word list full pathname
# Exits program if not found
def get_word_list_path_name(local_path_file_name: str) -> str:
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_file_name)
    if os.path.exists(full_path_name):
        # print("Using " + local_path_file_name)
        return full_path_name
    else:
        msg = f'The wordle word list file {local_path_file_name} was not found. Expected here: {full_path_name}'
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
def print_word_list_col_format(the_word_list, n_col):
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
                                           rank_mode: int, no_ordr: bool, no_rank=False) -> dict:
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
        if no_ordr:
            return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[0]))
        else:
            return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))
    else:
        return wrds_dict


# Returns the list of words that pass the grep command list
def get_results_word_list(this_sh_cmd_lst) -> list:
    with Popen(this_sh_cmd_lst.full_cmd(), shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
        return list(map(lambda i: i[: -1], proc.stdout.readlines()))


# Clears the console window
def clear_scrn():
    os.system("cls" if os.name == "nt" else "clear")


# Return a word's genetic code
# example:woody
# returns:[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0]
# translated: idx 0-25 'abc...xyz' letter count, idx 26 duplicates count, idx 27 genetic rank
# genetic rank applies in context of a list of words, so it is calculated later
def get_gencode(word) -> list:
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


# returns genetic letter tally list for a gendictionary
# this list is 26 members where each member corresponds
# to the count for that letter position idx 0-25 where
# idx 0=a and idx 25=z
def get_gendict_tally(gendict) -> list:
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


# Assigns the genetic rank to the gendict members and returns
# the maximum genetic rank seen.
def assign_genrank(gendict: dict, gen_tally: list) -> int:
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


# returns list of the max genrankers in the gendict
def get_maxgenrankers(gendict, maxrank) -> list:
    max_rankers = []
    for w, g in gendict.items():
        if maxrank == g[27]:
            max_rankers.append(w)
    return max_rankers


# returns a regex formatted pattern string for highlighting
def regex_maxgenrankers(max_rankers: list, wordsdict: dict) -> str:
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
                             r_pos_dict: dict):
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
    lself.tool_command_list.add_require_cmd(pat)
    return pat


# The filter builder. filter arguments for each type are added to the grep command argument list
def load_grep_arguments(wordle_tool, excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict):
    pipe = "|"
    pipe2 = "| "
    # Builds the grep line for excluding letters
    # example 'grep -vE \'b|f|k|w\''
    if len(excl_l) > 0:
        args = pipe.join(excl_l)
        grep_exclude = f"grep -vE \'{args}\'"
        wordle_tool.tool_command_list.add_cmd(grep_exclude)

    # Builds the grep line for requiring letters
    # Each letter gets its own grep
    if len(requ_l) > 0:
        itms = []
        for ltr in requ_l:
            itms.append(f"grep -E \'{ltr}\'")
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
        # This appears to be the correct context.
        genpat = get_genpattern(guess_word, subject_word)
        if genpat not in groups_dict:
            groups_dict[genpat] = [subject_word]
        else:
            groups_dict[genpat].append(subject_word)
    return groups_dict


def get_a_groups_stats(a_groups_dict: dict) -> tuple[int, int, int, float, float, float]:
    """
    Given a single guess group's dictionary, returns stats:
    pattern group quantity,
    smallest pattern group size,
    largest pattern group size,
    average pattern group size
    list size/ largest group ratio
    group population variance
    group entropy
    @param a_groups_dict: dictionary for a single guess group
    @return: tuple - quantity, smallest, largest, average
    """
    g_qty = len(a_groups_dict)  # number of groups
    smallest = g_qty  # smallest group size
    largest = 0  # largest group size
    sums = 0  # group size sums, this is the number of words
    p2 = 0.0  # group population variance
    g_ent = 0.0 # group entropy
    for k, v in a_groups_dict.items():
        size = len(v)
        sums = sums + size
        largest = max(largest, size)
        smallest = min(smallest, size)
    # mean = group average size
    mean = sums / g_qty
    for k, v in a_groups_dict.items():
        size = len(v)
        p2 += (size - mean) ** 2
        i_p = size/sums
        i_entropy = -(i_p * math.log(i_p,2))
        g_ent = g_ent + i_entropy
    p2 /= g_qty
    return g_qty, smallest, largest, mean, p2, g_ent



def groups_stat_summary(best_rank_dict: dict) -> tuple[int, int, int, float, float, float]:
    """
    Summarizes the groups best_rank_dictionary, mainly to extract the
    minimum and maximum group sizes
    @param best_rank_dict:
    @return: groups_stat_summary tuple:
    [0]:qty,
    [1]:smallest,
    [2]:largest,
    [3]:average,
    [4]:population variance,
    [5]:entropy bits,
    all as a tuple
    """
    # The grp_stats for each best_rank_dict member are:
    # [0]:qty, [1]:smallest, [2]:largest, [3]:average, [4]:population variance and [5]:entropy bits as tuple parts
    # Each member is 'best' because they have the maximum found grps_qty as the [0]:qty.
    # The 'best' are equal in grps_qty and average but could have varying
    # [2]:largest values and thus varying [4]:population variance values and [5] entropy bits
    # BTW, optimal_rank ([3]:average) in this function is an old name. It is not always optimal.
    #
    # This function's purpose, groups_stat_summary, it to summarize the group stats in all the found
    # best words that have their group stats contained by the best_rank_dictionary for reporting group
    # optimal words. The summary report is for noticing when better word selections exist. Because a groups stat
    # largest group count ([2]:largest) identifies a better selection within the best_rank_dictionary the
    # max_grp_size this function reports will actually be the minimum of the [3]:largest present in the
    # best_rank_dictionary. This is where we get the minimum of the maximums (min_max) idea. This is a subtlety
    # noticed occasionally where some word selections among words all having the same grps_qty could be better
    # because they have more balanced word group sizes, ie smaller population variance. Perhaps they also happen
    # to be from the list showing. These selections would be harder to spot when the summary reports the max group
    # size instead of the min_max group size.
    g_stats = best_rank_dict[list(best_rank_dict.keys())[0]]
    optimal_rank = g_stats[3]
    grps_qty = g_stats[0]
    min_grp_size = g_stats[2]  # Seed with a member's largest
    max_grp_size = g_stats[2]  # The min_max is desired. Seed with a member's largest
    min_grp_p2 = g_stats[4]  # Seed with member's variance
    max_grp_ent = g_stats[5]  # Seed with member's entropy
    for g_stats in best_rank_dict.values():
        (_, min_stat, max_stat, _, p2_stat, e_stat) = g_stats
        min_grp_size = min(min_stat, min_grp_size)
        max_grp_size = min(max_stat, max_grp_size)  # The min_max is desired.
        min_grp_p2 = min(p2_stat, min_grp_p2)
        max_grp_ent = max(max_grp_ent, e_stat)
        # groups_stat_summary are:
        # [0]:qty,
        # [1]:smallest,
        # [2]:largest,
        # [3]:average,
        # [4]:min p2
        # [5]:max entropy bit
        # as a tuple
    return grps_qty, min_grp_size, max_grp_size, optimal_rank, min_grp_p2, max_grp_ent


def extended_best_groups_guess_dict(word_lst: list, reporting: bool, cond_rpt: bool, keyed_rpt: bool, all_targets: dict,
                                    msg1: str, context: str) -> dict:
    """
    Wraps guess word group ranking to return the best
    group rank guesses. Guesses resulting in more groups
    and smaller groups are better guesses.
    @param context: String used in title so indicate owner
    @param reporting: flag for verbose printing to rptwnd
    @param cond_rpt: flag for condensed verbose printing to rptwnd
     @param keyed_rpt: flag for keyed by word verbose printing to rptwnd
    @param word_lst: possible guess words
    @param all_targets: vocabulary dictionary
    @param msg1: text to pass to verbose window
    @return: dictionary of the best group ranked guesses
    """
    guess_rank_dict = {}
    best_rank_dict = {}
    min_score = len(word_lst)
    rptwnd = RptWnd(context)
    rptwnd.withdraw()
    if reporting:
        rptwnd.deiconify()
        reporting_header_to_window(msg1, all_targets, rptwnd, cond_rpt)

    for guess in all_targets:
        guess_groups_dict = groups_for_this_guess(guess, word_lst)
        # grp_stats are: [0]:qty, [1]:smallest, [2]:largest, [3]:average as a tuple
        grp_stats = get_a_groups_stats(guess_groups_dict)

        if reporting:
            clue_pattern_groups_to_window(guess, grp_stats, guess_groups_dict, rptwnd, cond_rpt, keyed_rpt)

        # The rank is calculated as the average of the group's sizes.
        # Guesses that have the same number of groups but have a larger largest group have a
        # slightly higher prob. than other guesses having the same average.
        # grp_stats are:
        # [0]:qty,
        # [1]:smallest,
        # [2]:largest,
        # [3]:average,
        # [4]:population variance
        # as a tuple
        guess_rank_dict[guess] = grp_stats

        # Record the smallest average pattern groups size.
        min_score = min(grp_stats[3], min_score)

    # Populate the best_rank_dict with the best guesses.
    # This dictionary's values are grp_stats tuples.
    for g, s in guess_rank_dict.items():
        if s[3] == min_score:
            if g not in best_rank_dict:
                best_rank_dict[g] = s

    if reporting:
        report_footer_wrapper(msg1, word_lst, best_rank_dict, rptwnd)

    return best_rank_dict


def best_groups_guess_dict(word_lst: list, reporting: bool, cond_rpt: bool, keyed_rpt: bool, context: str) -> dict:
    """
    Wraps guess word group ranking to return the best
    group rank guesses. Guesses resulting in more groups
    and smaller groups are better guesses.
    @param context: String used in title so indicate owner
    @param reporting: flag for verbose printing to rptwnd
    @param cond_rpt: flag for condensed verbose printing to rptwnd
    @param keyed_rpt: flag for keyed by word verbose printing to rptwnd
    @param word_lst: possible guess words
    @return: dictionary of the best group ranked guesses where
    guess words are the keys, grp_stats tuples are the values
    grp_stats tuples are:
    [0]:qty,
    [1]:smallest,
    [2]:largest,
    [3]:average,
    [4]:population variance
    """
    guess_rank_dict = {}
    best_rank_dict = {}
    min_score = len(word_lst)
    rptwnd = RptWnd(context)
    rptwnd.withdraw()
    if reporting:
        rptwnd.deiconify()
        reporting_header_to_window("Words Showing", word_lst, rptwnd, cond_rpt)

    for guess in word_lst:
        guess_groups_dict = groups_for_this_guess(guess, word_lst)
        # grp_stats are: [0]:qty,
        # [1]:smallest,
        # [2]:largest,
        # [3]:average,
        # [4]:population variance
        # all as a tuple
        grp_stats = get_a_groups_stats(guess_groups_dict)

        if reporting:
            clue_pattern_groups_to_window(guess, grp_stats, guess_groups_dict, rptwnd, cond_rpt, keyed_rpt)

        # The rank is calculated as the average of the group's sizes.
        # Guesses that have the same number of groups but have a larger largest group have a
        # slightly higher prob. than other guesses having the same average.
        # grp_stats are: [0]:qty, [1]:smallest, [2]:largest, [3]:average, [4]:grp qty population variance as a tuple
        guess_rank_dict[guess] = grp_stats
        # Record the smallest average pattern groups size.
        min_score = min(grp_stats[3], min_score)

    # Populate the best_rank_dict with the best guesses.
    # This dictionary's values are grp_stats tuples.
    for g, s in guess_rank_dict.items():
        if s[3] == min_score:
            if g not in best_rank_dict:
                best_rank_dict[g] = s

    # Reporting only the best ranking guesses. These were collected into the
    # best_rank_dict dictionary of words as keys, grp_stats as values.
    if reporting:
        report_footer_wrapper("Words Showing", word_lst, best_rank_dict, rptwnd)

    return best_rank_dict


def report_footer_wrapper(msg1: str, word_lst: list, best_rank_dict: dict, rptwnd: ctk):
    report_footer_summary_header_to_window(msg1, word_lst, rptwnd)
    report_footer_stats_summary_to_window(best_rank_dict, rptwnd)
    report_footer_opt_wrds_to_window(best_rank_dict, rptwnd)
    report_footer_optimal_wrds_stats_to_window(best_rank_dict, rptwnd)
    rptwnd.back_to_summary()


def report_footer_summary_header_to_window(msg: str, source_list: any, rptwnd: ctk):
    rptl = "\n\n> >  Groups summary using the " + msg + " words for guesses on the " + \
           '{0:.0f}'.format(len(source_list)) + " words.  < <"
    rptwnd.msg1.insert(tk.END, rptl)


def reporting_header_to_window(msg: str, source_list: any, rptwnd: ctk, cond_rpt: bool):
    rptl = rptwnd.context + " - Pattern Groups For Guesses From The " + msg + " Words List (" + \
           '{0:.0f}'.format(len(source_list)) + ")"
    rptwnd.title(rptl)
    rptl = "> >  " + rptl + "  < <"
    rptwnd.msg1.insert(tk.END, rptl)
    if cond_rpt:
        rptl = '\n\nguess' + '\tqty' + \
               '\tmin' + \
               '\tmax' + \
               '\tave' + \
               '\tp2' + \
               '\tent'
        rptwnd.msg1.insert(tk.END, rptl)


def clue_pattern_groups_to_window(guess: any, grp_stats: tuple, guess_groups_dict: dict,
                                  rptwnd: ctk, cond_rpt: bool, keyed_rpt: bool) -> None:
    (qty, smallest, largest, average, p2, ent) = grp_stats
    # report in full or condensed format according to cond_prt flag
    if not cond_rpt:
        rptl = '\n\n> > > > Clue pattern groups for: ' + guess + ' < < < < '
        rptwnd.msg1.insert(tk.END, rptl)
        rptl = '\n> qty ' + str(qty) + \
               ', smallest size ' + str(smallest) + \
               ', largest size ' + str(largest) + \
               ', average size ' + '{0:.3f}'.format(average) + \
               ', p2 ' + '{0:.2f}'.format(p2) + \
               ', ent ' + '{0:.2f}'.format(ent)

        rptwnd.msg1.insert(tk.END, rptl)
        rptwnd.msg1.insert(tk.END, '\n')
        for key in sorted(guess_groups_dict):
            g = guess_groups_dict[key]
            if keyed_rpt:
                rptl = guess + '  ' + key + ' ' + '{:3d}'.format(len(g)) + ': ' + ', '.join(sorted(g))
            else:
                rptl = key + ' ' + '{:3d}'.format(len(g)) + ': ' + ', '.join(sorted(g))
            rptwnd.msg1.insert(tk.END, '\n' + rptl)
    else:
        rptl = '\n' + guess + '\t' + str(qty) + \
               '\t' + str(smallest) + \
               '\t' + str(largest) + \
               '\t' + '{0:.3f}'.format(average) + \
               '\t' + '{0:.2f}'.format(p2) + \
               '\t' + '{0:.2f}'.format(ent)
        rptwnd.msg1.insert(tk.END, rptl)


def report_footer_stats_summary_to_window(best_rank_dict: dict, rptwnd: ctk):
    rptwnd.msg1.insert(tk.END, groups_stats_summary_line(best_rank_dict))
    rptwnd.msg1.see('end')


def groups_stats_summary_line(best_rank_dict: dict) -> str:
    # stats_summary
    # [0]:qty,
    # [1]:smallest,
    # [2]:largest,
    # [3]:average,
    # [4]:population variance
    # [5]:entropy bits
    # as a tuple
    (g_qty, g_min, g_max, g_ave, g_p2, g_ent) = groups_stat_summary(best_rank_dict)
    rptl = "\n> >  Maximum group qty " + '{0:.0f}'.format(g_qty) + \
           ", sizes: min " + '{0:.0f}'.format(g_min) + \
           ", min-max " + '{0:.0f}'.format(g_max) + \
           ", ave " + '{0:.3f}'.format(g_ave) + \
           ", p2 " + '{0:.2f}'.format(g_p2) + \
           ", ent " + '{0:.2f}'.format(g_ent)
    return rptl


def report_footer_opt_wrds_to_window(best_rank_dict: dict, rptwnd: ctk):
    rptwnd.msg1.insert(tk.END, opt_wrds_for_reporting(best_rank_dict))


def opt_wrds_for_reporting(best_rank_dict: dict) -> str:
    wrds = list(best_rank_dict.keys())
    rptl = '\n> >  {0:.0f}'.format(len(wrds)) + ' Optimal group guess words:' + '\n' + ', '.join(wrds)
    return rptl


def report_footer_optimal_wrds_stats_to_window(best_rank_dict: dict, rptwnd: ctk):
    # stats_summary
    # [0]:qty,
    # [1]:smallest,
    # [2]:largest,
    # [3]:average,
    # [4]:population variance,
    # [5]:entropy bits,
    # as a tuple
    stats_summary = groups_stat_summary(best_rank_dict)
    rptl = '\n> >  Optimal guess word stats, each has group qty ' + '{0:.0f}'.format(stats_summary[0]) + ':'
    rptwnd.msg1.insert(tk.END, rptl)
    for w, s in best_rank_dict.items():
        (_, g_min, g_max, g_ave, g_p2, g_ent) = s
        rptl = "\n" + w + " - sizes:" + \
               " min " + '{0:.0f}'.format(g_min) + \
               ", max " + '{0:.0f}'.format(g_max) + \
               ", ave " + '{0:.3f}'.format(g_ave) + \
               ", p2 " + '{0:.3f}'.format(g_p2) + \
               ", ent " + '{0:.2f}'.format(g_ent)
        rptwnd.msg1.insert(tk.END, rptl)
        rptwnd.msg1.see('end')
    # lock the text widget to prevent user editing
    rptwnd.msg1.configure(state='disabled')


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
    def add_cmd(self, s: str) -> None:
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
    def add_require_cmd(self, ltr: str) -> None:
        if len(ltr) > 0:
            self.shCMDlist.append("grep -E '" + ltr + "'")

    # Adds command to stack to exclude the letter ltr.
    def add_excl_cmd(self, ltr: str) -> None:
        if len(ltr) > 0:
            self.shCMDlist.append("grep -vE '" + ltr + "'")

    # Adds command to stack to exclude letter from a position number.
    # Context is that letter is known, therefore is required but not
    # at the designated position.
    def add_excl_pos_cmd(self, ltr: str, p: int, add_e: bool) -> None:
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
    def add_incl_pos_cmd(self, ltr: str, p: int) -> None:
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

    def __init__(self,
                 data_path: str,
                 vocabulary: str,
                 letter_ranks: str,
                 allow_dups: bool,
                 rank_mode: int,
                 ordr_by_rank: bool) -> None:
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
                                                                       self.rank_mode, self.no_ordr, no_rank)

        self.ranked_cnt = len(self.ranked_wrds_dict)
        return self.ranked_wrds_dict

    # Return the grepped word count
    def get_results_raw_cnt(self) -> str:
        sh_cmd_for_cnt = self.tool_command_list.full_cmd() + " | wc -l"
        with Popen(sh_cmd_for_cnt, shell=True, stdout=PIPE, text=True, close_fds=True) as proc:
            return proc.stdout.readline().strip()

    # Returns the status text line.
    def get_status(self) -> str:
        status = '{} words shown from the {} full word list.'.format(self.ranked_cnt, self.get_results_raw_cnt())
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
                print('Selection pool for guess {} based on guess {} => {}'
                      .format(guess_no, (guess_no - 1), guess_wrd))
            else:
                print('Selection pool for guess {}'.format(guess_no))
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

    def remove_tag(self, tag):
        self.tag_remove(tag, "1.0", "end")

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=True, remove_priors=True, do_scroll=True):
        """Apply the given tag to all text that matches the given pattern
        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        """
        if remove_priors:
            self.remove_tag(tag)

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
            if do_scroll:
                self.see(index)  # scroll widget to show the index's line


# The verbose information window
class RptWnd(ctk.CTkToplevel):

    def clear_msg1(self) -> None:
        self.msg1.configure(state='normal')
        self.msg1.delete(1.0, tk.END)
        self.msg1.configure(state='disabled')

    def close_rpt(self) -> None:
        self.destroy()

    def search_for_text(self):
        self.find_the_text()

    def entry_release_return(self, event):
        self.find_the_text()

    def find_the_text(self):
        search_text = ''
        regex: search_text = self.search_text.get().strip()
        if len(regex) > 4:
            self.msg1.highlight_pattern(regex, 'grp', remove_priors=True)

    def back_to_summary(self):
        search_text = ''
        regex: search_text = 'Groups summary'
        self.msg1.highlight_pattern(regex, 'grp', remove_priors=True)
        self.msg1.remove_tag('grp')

    def rpt_show_grps_driller(self) -> None:
        if self.rpt_grpsdriller_window is None or not self.rpt_grpsdriller_window.winfo_exists():
            self.rpt_grpsdriller_window = groupdrilling.GrpsDrillingMain()  # create window if its None or destroyed
        else:
            self.rpt_grpsdriller_window.focus()  # if window exists focus it

    def __init__(self, context=''):
        super().__init__()
        self.context = context
        self.resizable(width=True, height=True)
        self.geometry('780x600')

        font_tuple_n = ("Courier", 14, "normal")
        self.search_text = tk.StringVar()
        self.search_text.set('for: ')
        self.rpt_grpsdriller_window = None

        self.info_frame = ctk.CTkFrame(self,
                                       corner_radius=10
                                       )
        self.info_frame.pack(fill='both',
                             padx=2,
                             pady=0,
                             expand=True
                             )
        self.info_frame.grid_columnconfigure(0, weight=1)  # non-zero weight allows grid to expand
        self.info_frame.grid_rowconfigure(0, weight=1)  # non-zero weight allows grid to expand

        self.msg1 = CustomText(self.info_frame,
                               wrap='word',
                               padx=6,
                               pady=6,
                               background='#dedede',
                               borderwidth=0,
                               highlightthickness=0
                               )
        self.msg1.grid(row=0, column=0, padx=6, pady=0, sticky='nsew')
        self.msg1.configure(font=font_tuple_n)
        self.msg1.tag_configure('grp', background='#ffd700')
        # scrollbar for rpt
        rpt_sb = ttk.Scrollbar(self.info_frame, orient='vertical')
        rpt_sb.grid(row=0, column=1, sticky='ens')

        self.msg1.config(yscrollcommand=rpt_sb.set)
        rpt_sb.config(command=self.msg1.yview)

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

    def close_help(self) -> None:
        self.destroy()

    # Returns string that is the information
    def get_rank_data(self) -> str:
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, self.letter_rank_file)
        if os.path.exists(full_path_name):
            f = open(full_path_name, "r", encoding="UTF8").read()
        else:
            f = 'Could not find. ' + self.full_path_name
        return f

    def get_info(self) -> str:
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path, 'helpinfo.txt')
        if os.path.exists(full_path_name):
            f = open(full_path_name, "r", encoding="UTF8").read()
        else:
            f = 'This is all the help you get because file helpinfo.txt has gone missing.'
        return f

    def show_info(self) -> None:
        self.msg1.configure(state='normal')
        self.msg1.delete(1.0, tk.END)
        self.msg1.insert(tk.END, self.get_info())
        self.msg1.configure(state='disabled')

    def show_rank_info(self) -> None:
        self.msg1.configure(state='normal')
        self.msg1.delete(1.0, tk.END)
        raw_rank_data = self.get_rank_data()
        f = raw_rank_data.replace(":", "\t")
        self.msg1.insert(tk.END, "Using file: " + self.letter_rank_file + "\n")
        self.msg1.insert(tk.END, "RNK = Rank for any occurrence\n")
        self.msg1.insert(tk.END, "RNK-X = Rank at position X in the word\n\n")
        self.msg1.insert(tk.END, "LTR\tRNK\tRNK-1\tRNK-2\tRNK-3\tRNK-4\tRNK-5\n")
        self.msg1.insert(tk.END, "---\t---\t-----\t-----\t-----\t-----\t-----\n")
        self.msg1.insert(tk.END, f)
        self.msg1.configure(state='disabled')

    def __init__(self, data_path, letter_rank_file):
        super().__init__()
        self.data_path = data_path
        self.letter_rank_file = letter_rank_file
        self.wm_title('Some Information For You')
        self.resizable(width=False, height=False)
        self.title('Some Information For You')

        # configure style
        style = ttk.Style()
        style.theme_use()
        help_font_tuple_n = ("Courier", 14, "normal")

        self.info_frame = ttk.LabelFrame(self,
                                         borderwidth=0,
                                         )
        self.info_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=0, expand=True)

        self.msg1 = tk.Text(self.info_frame,
                            wrap='word',
                            padx=10,
                            pady=8,
                            background='#dedede',
                            borderwidth=0,
                            highlightthickness=0,
                            )
        self.msg1.grid(row=0, column=0, padx=6, pady=0)
        self.msg1.configure(font=help_font_tuple_n)
        # scrollbar for help
        help_sb = ttk.Scrollbar(self.info_frame, orient='vertical')
        help_sb.grid(row=0, column=1, padx=1, pady=2, sticky='ens')
        self.msg1.config(yscrollcommand=help_sb.set)
        help_sb.config(command=self.msg1.yview)
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
