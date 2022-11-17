# ----------------------------------------------------------------
# imwm.py                                             AKS 5/2022
# Infinite Monkey Wordle Machine
# Measures the average number of guesses required to arrive at the
# Wordle target word using various guess strategies. Guesses are
# selected from the vocabulary list that has words removed based
# upon the previous guesses in the sample trial. The play is
# 'hard mode'.
# The base strategy is to guess only random words. One purpose is
# to examine the average required guesses as word difficulty.
# ----------------------------------------------------------------
import sys
import helpers
import random

data_path = 'worddata/'  # path from what will be helpers.py folder to data folder
letter_rank_file = 'letter_ranks.txt'

vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list

x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
excl_l = []  # exclude letters list
requ_l = []  # require letters list
the_word_list = {}  # the ranked word list dictionary


def get_word_list(guess_no: int, verbose=False) -> dict:
    """
    Combines returning the ranked word list dictionary with
    printing out information if needed.
    @param guess_no: The current guess number
    @param verbose: Flag to indicate display
    @return: The ranked word list corresponding to the filtering
    arguments already passed to the wordletool device.
    """
    the_word_list = wordletool.get_ranked_results_wrd_lst()
    if verbose:
        print()
        print('Selection pool for guess ' + str(guess_no))
        helpers.print_word_list_col_format(the_word_list, 6)
        print(wordletool.get_status())
        print(wordletool.get_cmd_less_filepath())
    return the_word_list


def clean_slate(excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict):
    """
    Clears all the objects used to hold the letter filtering information
    @param excl_l: List of letters to exclude.
    @param requ_l: List of letters to require
    @param x_pos_dict: Dictionary of letter at positions to exclude
    @param r_pos_dict: Dictionary of letters at position to require
    """
    x_pos_dict.clear()
    r_pos_dict.clear()
    excl_l.clear()
    requ_l.clear()


# The number of times to run guessing sessions
sample_number: int = 600
# The target Wordle word the guessing sessions is trying to discover.
target_wrd: str = 'snarl'

# rank mode:
# 0 = Occurrence
# 1 = Position
# 2 = Both
rank_mode = 2

# Set allow_dups to prevent letters from occurring more than once.
# This condition is used mainly for the first two guesses. Duplicate
# letter words are allowed after the second guess and due to the code
# is required to be able to correctly handle target words that have
# duplicate letters.
#
allow_dups = False
# allow_dups = True

# monkey type
rando_mode = True
# rando_mode = False
if rando_mode:
    guess_mode = ' random guesses'
    # For random mode to represent a base condition, duplicate letter
    # words show be allowed regardless of its previous setting.
    allow_dups = True
else:
    guess_mode = ' rank mode ' + str(rank_mode) + " guesses"
    # In ranked mode the allow duplicates flag will be not be forced
    # so that its influence on the first and second guess can be observed.

tot: int = 0  # total number of guesses
guessin2: int = 0  # total number of second getters
guessin1: int = 0  # total number of first getters
average: float = 0  # average guesses to find the target word
word: str = ''  # the guess

# helpers.clear_scrn()  # clears terminal
print()
print('Average guesses to solve Wordle sampling')
print('target_wrd: ' + target_wrd)
conditions = str(sample_number) + ' runs,' + guess_mode + ', initial allow duplicates: ' + str(allow_dups)
print(conditions)
for x in range(sample_number):
    # initialize a wordletool instance
    wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, allow_dups, rank_mode)
    guesses = 0
    run_stats = []
    run_stats.append(target_wrd)
    clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)
    helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
    the_word_list.clear()
    the_word_list = get_word_list(guesses + 1, False)
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
        # Normal strategy for non rando_mode, ie not picking anything random, is to not select
        # words having duplicate letters for at least the first two guesses. Allow_dups is
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
        the_word_list = get_word_list(guesses + 2, False)
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
    #     print(x, run_stats, guesses)
    #     guessin2 += 1
    # if guesses == 1:
    #     print(x, run_stats, guesses)
    #     guessin1 += 1

    # print(x, run_stats, guesses)

    del wordletool
    average = tot / (x + 1)
    sys.stdout.write('\033[K' + ">" + str(x + 1) + '  avg: ' + f'{average:.2f}' + '\r')
    # sys.stdout.write('\033[K' + ">" + str(x + 1) + '\r')

average = tot / sample_number
print('target_wrd: ' + target_wrd + ' , averaged ' + f'{average:.3f}' + ' guesses to solve. ' + conditions)
sys.stdout.write('\n')
# print('guessin2 % is ' + str(100 * (guessin2 / sample_number)))
# print('guessin2 count is ' + str(guessin2))
# print('guessin1 count is ' + str(guessin1))
