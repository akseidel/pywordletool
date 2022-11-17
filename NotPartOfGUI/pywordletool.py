# ----------------------------------------------------------------
# pywordletool AKS 5/2022
# ----------------------------------------------------------------
import sys

import helpers
import random

data_path = '../worddata/'  # path from here to data folder
letter_rank_file = 'letter_ranks.txt'

vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list

x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
excl_l = []  # exclude list
requ_l = []  # require list

# Set allow_dups to prevent letters from occurring more than once
allow_dups = False
# allow_dups = True

# rank mode:
# 0 = Occurrence
# 1 = Position
# 2 = Both
rank_mode = 2


# helpers.clear_scrn()  # clears terminal


def get_word_list(guess_no: int, verbose=False) -> dict:
    the_word_list = wordletool.get_ranked_results_wrd_lst()
    if verbose:
        print()
        print('Selection pool for guess ' + str(guess_no))
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

sample_number = 400
target_wrd = 'class'

# monkey type
# rando_mode = True
rando_mode = False
if rando_mode:
    guess_mode = ' random guesses ...'
else:
    guess_mode = ' rank mode ' + str(rank_mode) + " guesses ..."

tot = 0
guessin2 = 0
guessin1 = 0
average = 0

print()
print('target_wrd : ' + target_wrd + ' Sampling ' + str(sample_number) + ' solving runs with' + guess_mode)
for x in range(sample_number):
    # initialize a wordletool instance
    wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, allow_dups, rank_mode)
    guesses = 0
    run_stats = []
    run_stats.append(target_wrd)
    clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)
    helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
    the_word_list.clear()
    the_word_list = get_word_list(guesses+1,False)
    # This loop ends when the last guess results in only one remaining word that fits the
    # pattern. That word, being the target word, will be the solving guess. The loop's last
    # guess is therefore the actual second to last guess, except when it happens by chance
    # to be the target word.
    while len(the_word_list) > 1:
        if rando_mode:
            word, rank = random.choice(list(the_word_list.items()))
        else:
            if guesses == 0:
                # first pick has to be random in this sampling scheme
                word, rank = random.choice(list(the_word_list.items()))
            else:
                # all other picks are top rank
                word, rank = list(the_word_list.items())[-1]

        run_stats.append(word)
        # At this point the guess word has been selected from the results of the prior guess.
        # Normal strategy in for non rando_mode, ie not picking anything random is to not select
        # any words having duplicate letters for at least the first two guesses. Allow_dups is
        # likely already false for the first selection pool, ie the first pick does not allow dups.
        # Dups should be allowed for the third guess and beyond. Dups at the second guess depends
        # on how many dups there are compared to the number of non dups.

        # analyze this new word against the target word and update the filter criteria
        helpers.analyze_pick_to_solution(target_wrd, word, excl_l, x_pos_dict, r_pos_dict)

        if guesses > 0 and not allow_dups:  # need a new wordletool allowing dups
            del wordletool
            wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, rank_mode)

        # Now load in the filter criteria
        helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
        the_word_list = get_word_list(guesses+2,False)
        run_stats.append(len(the_word_list))
        guesses += 1

    # The ending guess is the second to last guess, except when it happens by chance
    # to be the target word. The next guess being the target word can only happen if the
    # allow_dups allows for that word to be in the list. Otherwise we get a wrong count.
    # This is a problem.
    if not word == target_wrd:
        guesses += 1
    tot = tot + guesses

    # if guesses == 2:
    #     # print(x, run_stats, guesses)
    #     guessin2 += 1
    # if guesses == 1:
    #     # print(x, run_stats, guesses)
    #     guessin1 += 1

    # print(x, run_stats, guesses)

    del wordletool
    average = tot / (x + 1)
    sys.stdout.write('\033[K' + ">" + str(x + 1) + '  avg: ' + f'{average:.2f}' + '\r')
    # sys.stdout.write('\033[K' + ">" + str(x + 1) + '\r')

average = tot / sample_number
print('target_wrd: ' + target_wrd + ' ' + str(average) + ' random guesses to solve. ' + str(sample_number) + ' runs using' + guess_mode)
sys.stdout.write('\n')
# print('guessin2 % is ' + str(100 * (guessin2 / sample_number)))
# print('guessin2 count is ' + str(guessin2))
# print('guessin1 count is ' + str(guessin1))
