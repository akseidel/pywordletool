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


def process_any_arguments():
    """
    Process any command line arguments
    """
    global debug_mode, reveal_mode, vocab_filename, use_starting_wrd
    if '-d' in sys.argv:
        # prints out lists, guesses etc.
        debug_mode = True
    if '-r' in sys.argv:
        # reveals each solution run data
        reveal_mode = True
    if '-tv' in sys.argv:
        # reveals each solution run data
        vocab_filename = 'nyt_wordlist.txt'
    if '-ns' in sys.argv:
        # no starting word, skip asking about it
        use_starting_wrd = 0

# The number of times to run guessing sessions
sample_number: int = 6000
debug_mode = False  # prints out lists, guesses etc.
reveal_mode = False  # reveals each solution run data
data_path = 'worddata/'  # path from what will be helpers.py folder to data folder
letter_rank_file = 'letter_ranks.txt'

vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list

x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
excl_l = []  # exclude letters list
requ_l = []  # require letters list
rank_mode = 2
rand_mode = True
allow_dups = False
target_wrd = ''
guess_mode = ''
starting_wrd = ''
use_starting_wrd = -1
process_any_arguments()
# the ranked word list dictionary, created now to use for valid input word checking
the_word_list = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, 0).get_ranked_results_wrd_lst()


def get_word_list(guess_no: int, gwrd='', verbose=False) -> dict:
    """
    Combines returning the ranked word list dictionary with
    printing out information if needed.
    @param guess_no: The current guess number
    @param gwrd: The guess word basis is the was one
    @param verbose: Flag to indicate display
    @return: The ranked word list corresponding to the filtering
    arguments already passed to the wordletool device.
    """
    the_word_list = wordletool.get_ranked_results_wrd_lst()
    if verbose:
        print()
        if guess_no > 1:
            print('Selection pool for guess ' + str(guess_no) + ' based on guess ' + str(guess_no - 1) + ' => ' + gwrd)
        else:
            print('Selection pool for guess ' + str(guess_no))
        print(wordletool.get_status())
        print(wordletool.get_cmd_less_filepath())
        helpers.print_word_list_col_format(the_word_list, 6)
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


def get_set_target_word():
    """
    Ask and set the target word.
    """
    global target_wrd
    while target_wrd not in the_word_list:
        target_wrd = input('Enter a valid Wordle target word: ').lower()


def get_set_starting_guess():
    """
    Ask for and set a given first guess word to be used in every session.
    """
    global starting_wrd, use_starting_wrd
    while use_starting_wrd == -1:
        response = input('Run using a given first guess? Enter y/n: ').lower()
        if response == 'y':
            while starting_wrd not in the_word_list:
                starting_wrd = input('Enter a valid Wordle first guess word: ').lower()
                use_starting_wrd = 1
        if response == 'n':
            use_starting_wrd = 0


def get_set_guess_mode():
    """
    Gets and sets the general run type: random guess or ranked guess.
    If ranked guess then get and set the ranking type.
    """
    global rank_mode, allow_dups, rand_mode, guess_mode
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
    rand_mode = True
    # rand_mode = False
    run_type = -1
    while run_type == -1:
        response: str = input('Random Guesses (0) or Ranked Guesses (1), Enter 0 or 1: ')
        if response == '0':
            rand_mode = True
            run_type = 0
        if response == '1':
            rand_mode = False
            run_type = 1

    if rand_mode:
        guess_mode = ' random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        del allow_dups
        allow_dups = True
    else:
        rank_mode = -1
        while rank_mode == -1:
            response: str = input('Rank by Occurrence (0), Position (1) or Both (2), Enter 0,1 or 2: ')
            if response == '0':
                rank_mode = 0
            if response == '1':
                rank_mode = 1
            if response == '2':
                rank_mode = 2

        guess_mode = ' rank mode ' + str(rank_mode) + " guesses"
        # In ranked mode the allow_dups flag will be not be forced
        # so that its influence on the first and second guess can be observed.


# ====================================== start ================================================

# helpers.clear_scrn()  # clears terminal
print()
print('Average guesses to solve Wordle sampling')
# Get the target Wordle word the guessing sessions is trying to discover.
get_set_target_word()
# Set the first guess if desired.
get_set_starting_guess()
# Set the guess mode and rank mode.
get_set_guess_mode()
# All samples are identical when there is a fixed starting word and
# a fixed rank selection method. So run only one sample.
if use_starting_wrd == 1 and not rand_mode:
    sample_number = 1

tot: int = 0  # total number of guesses
guessin2: int = 0  # total number of second getters
guessin1: int = 0  # total number of first getters
average: float = 0  # average guesses to find the target word
word: str = ''  # the guess

print('target_wrd: ' + target_wrd)
conditions = str(sample_number) + ' runs,' + guess_mode + ', initial allow duplicates: ' + str(allow_dups)
if len(starting_wrd) == 5:
    conditions = conditions + " , first guess = " + starting_wrd
print(conditions)
for x in range(sample_number):
    # initialize a wordletool instance
    wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, allow_dups, rank_mode)
    guesses = 0
    run_stats = list([])
    run_stats.append(target_wrd)
    clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)
    helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
    the_word_list.clear()
    the_word_list = get_word_list(guesses + 1, '', debug_mode)
    # This loop ends when the last guess results in only one remaining word that fits the
    # pattern. That word, being the target word, will be the solving guess. The loop's last
    # guess is therefore the actual second to last guess, except when it happens by chance
    # to be the target word.
    while len(the_word_list) > 1:
        if guesses == 0 and use_starting_wrd == 1:
            word = starting_wrd
        else:
            if rand_mode:
                word, rank = random.choice(list(the_word_list.items()))
            else:
                if guesses == 0:
                    # first pick has to be random in this sampling scheme
                    word, rank = random.choice(list(the_word_list.items()))
                    # word, rank = list(the_word_list.items())[-1]
                else:
                    # all other picks are top rank
                    word, rank = list(the_word_list.items())[-1]

        run_stats.append(word)
        # At this point the guess word has been selected from the results of the prior guess.
        # Normal strategy for non rand_mode, ie not picking anything random, is to not select
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
        the_word_list = get_word_list(guesses + 2, word, debug_mode)
        run_stats.append(len(the_word_list))
        guesses += 1
        # if debug_mode:
        #     print(x+1, run_stats, guesses)
        # print(x + 1, run_stats, guesses)

    # The ending guess is the second to last guess, except when it happens by chance
    # to be the target word. The next guess being the target word can only happen if the
    # allow_dups allows for that word to be in the list. Otherwise, we get a wrong count.
    # This is a problem.
    if not word == target_wrd:
        guesses += 1
    tot = tot + guesses

    # if guesses == 2:
    #     # print(x, guesses, run_stats)
    #     guessin2 += 1
    # if guesses == 1:
    #     # print(x, guesses, run_stats)
    #     guessin1 += 1

    if reveal_mode:
        print(x + 1, guesses, run_stats)

    del wordletool
    average = tot / (x + 1)
    sys.stdout.write('\033[K' + ">" + str(x + 1) + '  avg: ' + f'{average:.2f}' + '\r')
    # sys.stdout.write('\033[K' + ">" + str(x + 1) + '\r')

# print(x + 1, run_stats, guesses)
average = tot / sample_number
print('target_wrd: ' + target_wrd + ' , averaged ' + f'{average:.3f}' + ' guesses to solve. ' + conditions)
sys.stdout.write('\n')
# print('guessin2 % is ' + f'{(100 * (guessin2 / sample_number)):.2f}')
# print('guessin2 count is ' + str(guessin2))
# print('guessin1 count is ' + str(guessin1))
