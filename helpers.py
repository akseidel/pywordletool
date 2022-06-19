# ----------------------------------------------------------------
# helpers akseidel 5/2022
# ----------------------------------------------------------------
import sys
import os
import random
from tkinter import messagebox


# Returns the wordle word list full pathname
# Exits program if not found
def get_word_list_path_name(local_path_file_name):
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


# Make and return the letter ranking dictionary
def make_ltr_rank_dictionary(local_path_rank_file):
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_rank_file)
    ltr_rank_dict = {}  # ltr_rank_dict will be the rank dictionary
    if os.path.exists(full_path_name):
        # print("Using " + local_path_rank_file)
        with open(full_path_name) as f:
            for ltr in f:
                ltr = ltr.split(":")
                ltr_rank_dict[ltr[0]] = float(ltr[1])
    else:
        msg = "Letter ranking file " \
              + local_path_rank_file \
              + " not found. Switching to built in letter ranking."
        print(msg)
        messagebox.showwarning('Warning', message=msg)
        ltr_rank_dict = {
            "e": 39.0,
            "a": 33.6,
            "r": 30.9,
            "o": 24.9,
            "t": 24.7,
            "i": 23.9,
            "l": 23.9,
            "s": 22.9,
            "n": 20.3,
            "u": 16.9,
            "c": 16.5,
            "y": 15.4,
            "h": 14.0,
            "d": 13.7,
            "p": 12.8,
            "g": 11.1,
            "m": 11.0,
            "b": 9.9,
            "f": 7.6,
            "k": 7.5,
            "w": 7.1,
            "v": 5.5,
            "x": 1.4,
            "z": 1.3,
            "q": 1.1,
            "j": 1.0,
        }
    return ltr_rank_dict


# Returns a word's letter frequency ranking
def wrd_rank(wrd, ltr_rank_dict):
    r = 0
    for x in wrd:
        r = r + ltr_rank_dict[x]
    return r


# Returns true if word has duplicate letters
def wrd_has_duplicates(wrd):
    ltr_d = {}
    for ltr in wrd:
        ltr_d[ltr] = ltr
    return len(ltr_d) < len(wrd)


# List out the ranked word list in columns
def show_this_word_list(the_word_list, n_col):
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
def make_ranked_filtered_result_dictionary(wrds, ltr_rank_dict, no_dups):
    wrds_dict = {}
    for w in wrds:
        if len(w) == 5:
            if no_dups:
                if not wrd_has_duplicates(w):
                    wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict))
            else:
                wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict))

    # sorting the ranked word list into a dictionary
    # return dict(sorted(wrds_dict.items(), reverse=True,key= lambda x:x[1]))
    return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))


# Returns the number of words that pass the grep command list
def get_raw_word_count(this_sh_cmd_lst):
    sh_cmd_cnt = this_sh_cmd_lst.full_cmd() + " | wc -ltr"
    return os.popen(sh_cmd_cnt).read().strip()


# Returns the list of words that pass the grep command list
def get_results_word_list(this_sh_cmd_lst):
    result = os.popen(this_sh_cmd_lst.full_cmd()).read()
    return result.split("\n")


# Clears the console window
def clear_scrn():
    os.system("cls" if os.name == "nt" else "clear")


# A class used for holding list stack of the shell commands
# It has functions that build greps related to filtering wordle
# letter conditions. Some functions are not used in the gui
# pywordletool.
class ShellCmdList:
    # The command list is by instance.
    def __init__(self, list_file_name):
        self.shCMDlist = list()
        self.shCMDlist.append("cat " + list_file_name)

    # Adds string s to the command stack.
    def add_cmd(self, s):
        if len(s) > 0:
            self.shCMDlist.append(s)

    # Given a string of letters lst, adds to the command
    # stack a grep filter requiring a letter picked at random
    # from string lst. Returns that random picked letter for
    # feedback purposes.
    def add_rand_incl_frm_cmd(self, lst):
        rand_frm_l = random.choice(lst)
        self.shCMDlist.append("grep -E '" + rand_frm_l + "'")
        return rand_frm_l

    # Adds command to stack to require letter ltr.
    def add_require_cmd(self, ltr):
        if len(ltr) > 0:
            self.shCMDlist.append("grep -E '" + ltr + "'")

    # Adds command to stack to exclude letter ltr.
    def add_excl_any_cmd(self, ltr):
        if len(ltr) > 0:
            self.shCMDlist.append("grep -vE '" + ltr + "'")

    # Adds command to stack to exclude letter from a position number.
    # Context is that letter is known, therefore is required but not
    # at the designated position.
    def add_excl_pos_cmd(self, ltr, p):
        if len(ltr) > 0:
            # Require the letter,
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
    def add_incl_pos_cmd(self, ltr, p):
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
    def full_cmd(self):
        pipe = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pipe
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd


# ToolResults(data path, vocabulary file name, letter_ranks file, no_dups)
# The wordle tool all wrapped up into one being, including the grep command list.
class ToolResults:

    def __init__(self, data_path, vocabulary, letter_ranks, no_dups):
        self.data_path = data_path
        self.vocab = vocabulary  # vocabulary is the words list textfile
        self.ltr_ranks = letter_ranks  # ltr_ranks is the letter ranking textfile
        self.no_dups = no_dups  # no_dups is the-allow-duplicate-letters flag

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
    def get_results_wrd_lst(self):
        return os.popen(self.tool_command_list.full_cmd()).read().split("\n")

    # Returns ranked results words list as dictionary. The ranking function also
    # sorts the dictionary. So result is sorted.
    def get_ranked_results_wrd_lst(self):
        # Ranking and filtering the words into a dictionary
        # Set no_dups to prevent letters from occurring more than once
        # First pick should not use duplicates, later picks should consider them.
        wrds = self.get_results_wrd_lst()
        self.ranked_wrds_dict = make_ranked_filtered_result_dictionary(wrds, self.ltr_rank_dict, self.no_dups)
        self.ranked_cnt = len(self.ranked_wrds_dict)
        return self.ranked_wrds_dict

    # Return the grepped word count
    def get_results_raw_cnt(self):
        sh_cmd_for_cnt = self.tool_command_list.full_cmd() + " | wc -l"
        self.raw_cnt = os.popen(sh_cmd_for_cnt).read().strip()
        return self.raw_cnt

    # Returns sorted ranked word list formatted into n_col columns.
    def show_col_format_ranked_list(self, n_col):
        return show_this_word_list(self.get_ranked_results_wrd_lst(), n_col)

    # Returns the status text line.
    def show_status(self):
        status = '=> Showing ' + str(self.ranked_cnt) + ' words from the raw list of ' + str(
            self.get_results_raw_cnt()) + " duplicate letter words."
        return status

    # Returns the entire fully assembled grep command line. This line includes
    # the full path names.
    def show_full_cmd(self):
        return self.tool_command_list.full_cmd()

    # Returns the entire fully assembled grep command line. This line excluded
    # the full path names and so is used in the GUI display.
    def show_cmd(self):
        full_cmd = self.tool_command_list.full_cmd()
        full_path_name = os.path.join(os.path.dirname(__file__), self.data_path)
        part_cmd = full_cmd.replace(full_path_name, '', 1)
        return part_cmd
