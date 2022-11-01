# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
import sys
import os
import random
import tkinter as tk  # assigns tkinter stuff to tk namespace
from tkinter import messagebox
from typing import NoReturn

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
    r = 0
    if method == 0:  # rank by anywhere in word
        for x in wrd:
            # 0th position is rank by anywhere
            r = r + ltr_rank_dict[x][0]
        return r
    if method == 1:  # rank by position in the word
        p = 1
        for x in wrd:
            # 1 to 5th position is rank for being in that position
            r = r + ltr_rank_dict[x][p]
            p += 1
        return r
    if method == 2:  # rank by position in the word
        p = 1
        for x in wrd:
            # combine methods 0 and 1
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


# List out the ranked word list in columns
def print_this_word_list(the_word_list, n_col) -> NoReturn:
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
def make_ranked_filtered_result_dictionary(wrds: list, ltr_rank_dict: dict, allow_dups: bool, rank_mode: int) -> dict:
    wrds_dict = {}
    for w in wrds:
        if len(w) == 5:
            if allow_dups:
                wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))
            else:
                if not wrd_has_duplicates(w):
                    wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict, rank_mode))

    # sorting the ranked word list into a dictionary
    # return dict(sorted(wrds_dict.items(), reverse=True,key= lambda x:x[1]))
    return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))


# Returns the number of words that pass the grep command list
def get_raw_word_count(this_sh_cmd_lst) -> str:
    sh_cmd_cnt = this_sh_cmd_lst.full_cmd() + " | wc -ltr"
    return os.popen(sh_cmd_cnt).read().strip()


# Returns the list of words that pass the grep command list
def get_results_word_list(this_sh_cmd_lst) -> list:
    result = os.popen(this_sh_cmd_lst.full_cmd()).read()
    return result.split("\n")


# Clears the console window
def clear_scrn() -> NoReturn:
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
def assign_genrank(gendict, gen_tally) -> int:
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
def regex_maxgenrankers(max_rankers, wordsdict) -> str:
    pat_list = []
    mid_div = " : "
    for w in max_rankers:
        r = wordsdict[w]
        pat_list.append(w + mid_div + r)
    regex_str = '|'.join(pat_list)
    return regex_str


# A class used for holding list stack of the shell commands
# It has functions that build greps related to filtering wordle
# letter conditions. Some functions are not used in the gui
# pywordletool.
class ShellCmdList:
    # The command list is by instance.
    def __init__(self, list_file_name: str) -> NoReturn:
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

    # Adds command to stack to exclude letter ltr.
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
            if p == 1:
                self.shCMDlist.append("grep -vE '" + ltr + "....'")
            elif p == 2:
                self.shCMDlist.append("grep -vE '." + ltr + "...'")
            elif p == 3:
                self.shCMDlist.append("grep -vE '.." + ltr + "..'")
            elif p == 4:
                self.shCMDlist.append("grep -vE '..." + ltr + ".'")
            elif p == 5:
                self.shCMDlist.append("grep -vE '...." + ltr + "'")

    # Adds command to stack to require letter at a position number.
    def add_incl_pos_cmd(self, ltr: str, p: int) -> NoReturn:
        if len(ltr) > 0:
            # Have letter in this position
            if p == 1:
                self.shCMDlist.append("grep -E '" + ltr + "....'")
            elif p == 2:
                self.shCMDlist.append("grep -E '." + ltr + "...'")
            elif p == 3:
                self.shCMDlist.append("grep -E '.." + ltr + "..'")
            elif p == 4:
                self.shCMDlist.append("grep -E '..." + ltr + ".'")
            elif p == 5:
                self.shCMDlist.append("grep -E '...." + ltr + "'")

    # Returns the command stack assembled into one command line.
    def full_cmd(self) -> str:
        pipe = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pipe
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd


# ToolResults(data path, vocabulary file name, letter_ranks file, allow_dups)
# The wordle tool all wrapped up into one being, including the grep command list.
class ToolResults:

    def __init__(self, data_path, vocabulary, letter_ranks, allow_dups, rank_mode):
        self.data_path = data_path
        self.vocab = vocabulary  # vocabulary is the words list textfile
        self.ltr_ranks = letter_ranks  # ltr_ranks is the letter ranking textfile
        self.allow_dups = allow_dups  # allow_dups is the-allow-duplicate-letters flag
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
        return os.popen(self.tool_command_list.full_cmd()).read().split("\n")

    # Returns ranked results words list as dictionary. The ranking function also
    # sorts the dictionary. So result is sorted.
    def get_ranked_results_wrd_lst(self) -> dict:
        # Ranking and filtering the words into a dictionary
        # Set allow_dups to prevent letters from occurring more than once
        # First pick should not use duplicates, later picks should consider them.
        wrds = self.get_results_wrd_lst()
        self.ranked_wrds_dict = make_ranked_filtered_result_dictionary(wrds, self.ltr_rank_dict, self.allow_dups,
                                                                       self.rank_mode)
        self.ranked_cnt = len(self.ranked_wrds_dict)
        return self.ranked_wrds_dict

    # aks to do
    # Genetic note: We still want to know the letter freq rank for the genetic ranked words. The plan will
    # be to show the normal ranked list with the highest genetics highlighted.
    # Multiple highlighting is possible. Tested

    # Return the grepped word count
    def get_results_raw_cnt(self) -> str:
        sh_cmd_for_cnt = self.tool_command_list.full_cmd() + " | wc -l"
        self.raw_cnt = os.popen(sh_cmd_for_cnt).read().strip()
        return self.raw_cnt

    # Returns sorted ranked word list formatted into n_col columns.
    def print_col_format_ranked_list(self, n_col: int) -> NoReturn:
        print_this_word_list(self.get_ranked_results_wrd_lst(), n_col)

    # Returns the status text line.
    def get_status(self) -> str:
        status = '=> Showing ' + str(self.ranked_cnt) + ' words from the raw list of ' + str(
            self.get_results_raw_cnt()) + " duplicate letter words."
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
