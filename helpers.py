# ----------------------------------------------------------------
# helpers AKS 5/2022
# ----------------------------------------------------------------
import sys
import os
import random


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
def show_this_word_list(the_word_list):
    print("Word  : Rank")
    for key, value in the_word_list.items():
        msg = key + " : " + str(value)
        print(msg)


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

    def full_cmd(self):
        pc = " | "
        this_cmd = ""
        for w in self.shCMDlist[:-1]:
            this_cmd = this_cmd + w + pc
        this_cmd = this_cmd + self.shCMDlist[-1]
        return this_cmd
