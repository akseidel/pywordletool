# ----------------------------------------------------------------
# pywordletool AKS 5/2022
# ----------------------------------------------------------------

import helpers
import random

data_path = 'worddata/'  # path from here to data folder
letter_rank_file = 'letter_ranks.txt'

vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list

x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
excl_l = []  # exclude list
requ_l = []  # require list

# Set allow_dups to prevent letters from occurring more than once
# allow_dups = False
no_dups = True

# rank mode:
# 0 = Occurrence
# 1 = Position
# 2 = Both
rank_mode = 2

helpers.clear_scrn()  # clears terminal


def get_word_list(verbose=False) -> dict:
    the_word_list = wordletool.get_ranked_results_wrd_lst()
    if verbose:
        helpers.print_word_list_col_format(the_word_list, 6)
        print(wordletool.get_status())
        print(wordletool.get_cmd_less_filepath())
    return the_word_list


def clean_slate(excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict):
    x_pos_dict.clear()
    r_pos_dict.clear()
    excl_l.clear()
    requ_l.clear()


the_word_list = {}

sample_number = 100
target_wrd = 'baker'
tot = 0
guessin2 = 0
guessin1 = 0

print('target_wrd : ' + target_wrd + ' Sampling ' + str(sample_number) + ' solving runs with random guesses ...')
for x in range(sample_number):
    # initialize a wordletool instance
    wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, no_dups, rank_mode)
    guesses = 0
    run_stats = []
    run_stats.append(target_wrd)
    clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)
    helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
    the_word_list.clear()
    the_word_list = get_word_list()
    # This loop ends when the last guess results in only one remaining word that fits the
    # pattern. That word, being the target word, will be the solving guess. The loop's last
    # guess is therefore the actual second to last guess, except when it happens by chance
    # to be the target word.
    while len(the_word_list) > 1:
        word, rank = random.choice(list(the_word_list.items()))
        # word, rank = list(the_word_list.items())[-1]
        guesses += 1
        run_stats.append(word)
        helpers.analyze_pick_to_solution(target_wrd, word, excl_l, x_pos_dict, r_pos_dict)
        helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
        the_word_list = get_word_list()
        run_stats.append(len(the_word_list))
    # The ending guess is the second to last guess, except when it happens by chance
    # to be the target word.
    if not word == target_wrd:
        guesses += 1
    tot = tot + guesses
    if guesses == 2:
        print(x, run_stats, guesses)
        guessin2 += 1
    if guesses == 1:
        print(x, run_stats, guesses)
        guessin1 += 1
    del wordletool

average = tot / sample_number
print('target_wrd ' + target_wrd + ' : ' + str(average) + ' random guesses to solve. ' + str(sample_number) + ' runs.')
print('guessin2 % is ' + str(100 * (guessin2 / sample_number)))
print('guessin2 count is ' + str(guessin2))
print('guessin1 count is ' + str(guessin1))
