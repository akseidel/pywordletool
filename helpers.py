# ----------------------------------------------------------------
# helpers AKS 5/2022
# ----------------------------------------------------------------
import sys
import os
import random
import grepper

# Returns the wordle word list full pathname
# Exits program if not found
def get_word_list_path_name(local_path_file_name):
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_file_name)
    if os.path.exists(full_path_name):
        print("Using " + local_path_file_name)
        return full_path_name
    else:
        print(
            "Stopping here, wordle word list file "
            + local_path_file_name
            + " was not found."
        )
        print("Expected here: " + full_path_name)
        print()
        sys.exit()


# Make and return the letter ranking dictionary
def make_ltr_rank_dictionary(local_path_rank_file):
    full_path_name = os.path.join(os.path.dirname(__file__), local_path_rank_file)
    ltr_rank_dict = {}  # ltr_rank_dict will be the rank dictionary
    if os.path.exists(full_path_name):
        print("Using " + local_path_rank_file)
        with open(full_path_name) as f:
            for l in f:
                l = l.split(":")
                ltr_rank_dict[l[0]] = float(l[1])
    else:
        print(
            "Letter ranking file "
            + local_path_rank_file
            + " not found. Switching to built in letter ranking."
        )
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
    for l in wrd:
        ltr_d[l] = l
    return len(ltr_d) < len(wrd)


# List out the ranked word list
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

#
# def show_list_in_textbox(the_word_list, n_col, tbox_result):
#     tbox_result.delete(1.0, END)



# Ranking and filtering the words into a dictionary
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


# Returns the number of matching words
def get_raw_word_count(this_sh_cmd_lst):
    sh_cmd_cnt = this_sh_cmd_lst.full_cmd() + " | wc -l"
    return os.popen(sh_cmd_cnt).read().strip()


# Returns the results words list
def get_results_word_list(this_sh_cmd_lst):
    result = os.popen(this_sh_cmd_lst.full_cmd()).read()
    return result.split("\n")


# Clears the console
def clear_scrn():
    os.system("cls" if os.name == "nt" else "clear")


# A class used for holding list stack of the shell commands
# It has functions that build greps related to filtering wordle
# letter conditions.
class ShellCmdList:
    shCMDlist = list()

    def __init__(self, list_file_name):
        self.shCMDlist.append("cat " + list_file_name)

    def add_cmd(self, s):
        self.shCMDlist.append(s)

    # word includes random letter from list lst
    # returns the random pick letter
    def add_rand_incl_frm_cmd(self, lst):
        rand_frm_l = random.choice(lst)
        self.shCMDlist.append("grep -E '" + rand_frm_l + "'")
        return rand_frm_l

    # word requires this letter l
    def add_require_cmd(self, l):
        self.shCMDlist.append("grep -E '" + l + "'")

    # word excludes this letter l
    def add_excl_any_cmd(self, l):
        self.shCMDlist.append("grep -vE '" + l + "'")

    # word excludes letter from position number
    def add_excl_pos_cmd(self, l, p):
        # can have letter
        self.shCMDlist.append("grep -E '" + l + "'")
        # but not in this position
        if p == 1:
            self.shCMDlist.append("grep -vE '" + l + "....'")
        elif p == 2:
            self.shCMDlist.append("grep -vE '." + l + "...'")
        elif p == 3:
            self.shCMDlist.append("grep -vE '.." + l + "..'")
        elif p == 4:
            self.shCMDlist.append("grep -vE '..." + l + ".'")
        elif p == 5:
            self.shCMDlist.append("grep -vE '...." + l + "'")

    # word includes letter in position number
    def add_incl_pos_cmd(self, l, p):
        # Have letter in this position
        if p == 1:
            self.shCMDlist.append("grep -E '" + l + "....'")
        elif p == 2:
            self.shCMDlist.append("grep -E '." + l + "...'")
        elif p == 3:
            self.shCMDlist.append("grep -E '.." + l + "..'")
        elif p == 4:
            self.shCMDlist.append("grep -E '..." + l + ".'")
        elif p == 5:
            self.shCMDlist.append("grep -E '...." + l + "'")

    # returns the list assembled into one command line
    def full_cmd(self):
        pc = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pc
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd

# ToolResults(vocabulary file, letter_ranks file, no_dups)
class ToolResults:
    # constructor
    def __init__(self, data_path, vocabulary, letter_ranks, no_dups):
        self.data_path = data_path
        self.vocab = vocabulary  # vocabulary is the words list textfile
        self.ltr_ranks = letter_ranks  # ltr_ranks is the letter ranking textfile
        self.no_dups = no_dups  # no_dups is the allow duplicate letters flag
        #self.g_cmd_lst = grep_cmd_lst  # grep_cmd_lst is the list of grep commands

        # we have all the setting so do the grep
        wrdListFileName = get_word_list_path_name(self.data_path + self.vocab)
        rankFile = self.data_path + self.ltr_ranks
        self.ltr_rank_dict = make_ltr_rank_dictionary(rankFile)  # ltr_rank_dict is the rank dictionary
        # Initialize and setup the ShellCmdList class instance that holds the
        # grep filtering command stack. Guessing because it is a class instance is why it
        # can be passed around as a global variable where it gets modified along the way.
        self.this_sh_cmd_lst = ShellCmdList(wrdListFileName) # init with cat wordlistfile
        grepper.setup_grep_filtering(self.this_sh_cmd_lst)  # fills the cmd stack with grep assignments
        # At this point the grep stack is ready for executing
        self.ranked_wrds_dict ={} # dictionary of ranked words resulting from grep filtering
        self.raw_cnt = 0
        self.ranked_cnt = 0

    # returns results words list
    def get_results_wrd_lst(self):
        return os.popen(self.this_sh_cmd_lst.full_cmd()).read().split("\n")


    # returns ranked results words list
    def get_ranked_results_wrd_lst(self):
        # Ranking and filtering the words into a dictionary
        # Set no_dups to prevent letters from occurring more than once
        # First pick should not use duplicates, later picks should consider them.
        wrds = self.get_results_wrd_lst()
        self.ranked_wrds_dict = make_ranked_filtered_result_dictionary(wrds, self.ltr_rank_dict, self.no_dups)
        self.ranked_cnt = len(self.ranked_wrds_dict)
        return  self.ranked_wrds_dict


    # Get the grepped word count
    def get_results_raw_cnt(self):
        sh_cmd_for_cnt = self.this_sh_cmd_lst.full_cmd() + " | wc -l"
        self.raw_cnt = os.popen(sh_cmd_for_cnt).read().strip()
        return self.raw_cnt

    # returns ranked word list formatted into columns
    def show_col_format_ranked_list(self, n_col):
        return show_this_word_list(self.get_ranked_results_wrd_lst(),n_col)

    def show_status(self):
        status = '=> Showing word list of ' + str(self.ranked_cnt) + " from raw list of " + str(self.get_results_raw_cnt()) + " having duplicates."
        return status

    def show_full_cmd(self):
        return '=> ' + self.this_sh_cmd_lst.full_cmd()
