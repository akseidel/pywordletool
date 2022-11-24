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
from datetime import datetime

import helpers
import random
import argparse
import csv


def set_context_msg():
    """
    Sets the guess_mode string that is used to append a status message.
    """
    global rand_mode, guess_mode, allow_dups, rank_mode
    if rand_mode:
        guess_mode = 'random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = 'rank mode ' + str(rank_mode + 1) + " guesses"
        # In ranked mode the allow_dups flag will be not be forced
        # so that its influence on the first and second guess can be observed.


def process_any_arguments():
    """
    Process any command line arguments
    """
    global debug_mode, reveal_mode, vocab_filename, target_wrd, use_starting_wrd, \
        starting_wrd, rank_mode, allow_dups, rand_mode, guess_mode, run_type, \
        sample_number, vocab_filename, record_run

    parser = argparse.ArgumentParser(description='Process command line settings.')
    parser.add_argument('-d', action='store_true', help='Prints out lists, guesses etc.')
    parser.add_argument('-l', action='store_true', help='Lists each solution run data')
    parser.add_argument('-n', action='store_true', help='Random first guess word, ie skip asking about it')
    parser.add_argument('-t', action='store', help='Use this target word T.')
    parser.add_argument('-s', action='store', help='Use this first guess word S.')
    parser.add_argument('-r', action='store', type=int, choices=range(0, 4),
                        help='Guess type: Random(0),Rank Occurrence (1),Rank Position (2) or Both (3)')
    parser.add_argument('-x', action='store', type=int,
                        help='Override the number of sampling runs to be this number X.')
    parser.add_argument('-v', action='store_true', help='Use the Wordle vocabulary that includes non-solution words.')
    parser.add_argument('-w', action='store_true', help='Writes output to CVS file having a timestamp filename.')

    args = parser.parse_args()
    debug_mode = args.d  # prints out lists, guesses etc.
    reveal_mode = args.l  # lists each solution run data

    if args.w:
        # Writes output to CVS file having a timestamp filename.
        record_run = True

    if args.v:
        # Use the Wordle vocabulary that includes non-solution words
        vocab_filename = 'nyt_wordlist.txt'  # total vocabulary list

    if args.n:
        # no starting word, skip asking about it
        use_starting_wrd = 0

    if args.t is not None:
        # use this target word
        target_wrd = args.t

    if args.s is not None:
        use_starting_wrd = 1
        starting_wrd = args.s

    if args.r is not None:
        if args.r == 0:
            rand_mode = True
            run_type = 0
        else:
            rand_mode = False
            run_type = 1
        # wordletool rank mode ranges from 0 to 2. Random was not a rank mode.
        # But for command line argument reasons random and rank modes are
        # combined. So ui rank 1 is wordletool rank 0 etc.
        if args.r == 1:
            # Rank by Occurrence (1)
            rank_mode = 0
        if args.r == 2:
            # Rank by Position (2)
            rank_mode = 1
        if args.r == 3:
            # Rank by Both (3),
            rank_mode = 2

        set_context_msg()

    if args.x is not None:
        if args.x < 1:
            sample_number = 1
            print('===> Negative value not allowed. Runs number is set to ' + str(sample_number))
        elif args.x > 20000:
            sample_number = 20000
            print('===> Honestly, even 20,000 is too many. Runs number is set to ' + str(sample_number))
            print('===> Control + C will stop the program.')
        else:
            sample_number = args.x


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
    global rank_mode, allow_dups, rand_mode, guess_mode, run_type
    if run_type != -1:
        return
    while run_type == -1:
        response: str = input(
            'Guess Type? Random(0), or Rank by Occurrence (1), Position (2) or Both (3), Enter 0,1,2 or 3: ')
        if response == '0':
            rand_mode = True
            run_type = 0
        if response == '1':
            rand_mode = False
            run_type = 1
            rank_mode = 0
        if response == '2':
            rand_mode = False
            run_type = 1
            rank_mode = 1
        if response == '3':
            rand_mode = False
            run_type = 1
            rank_mode = 2

    if rand_mode:
        guess_mode = ' random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = ' rank mode ' + str(rank_mode) + " guesses"
        # In ranked mode the allow_dups flag will be not be forced
        # so that its influence on the first and second guess can be observed.


def imwm_fname() -> str:
    """
    Returns a time timestamp like .csv filename
    @rtype: str
    """
    ts = str(datetime.now()).replace(' ', '_')
    ts = ts.replace(':', '_')
    return ts + ".csv"


def output_msg(msg: any, also2file: bool, fname: str):
    fn_csv = fname
    if also2file:
        with open(fn_csv, 'a') as f:
            if type(msg) is str:
                f.write(str(msg) + '\n')
            if type(msg) is list:
                csvwriter = csv.writer(f)
                csvwriter.writerow(msg)
    else:
        print(str(msg))
    return


def prelude_output():
    global conditions, sample_number, guess_mode, allow_dups, record_run, run_fname, starting_wrd, vocab_filename
    conditions = str(sample_number) + ' runs, ' + guess_mode + ', initial duplicates: ' + str(allow_dups)
    if len(starting_wrd) == 5:
        conditions = conditions + " , first guess = " + starting_wrd
    output_msg('target_wrd: ' + target_wrd + ", " + conditions + ", " + vocab_filename, False, run_fname)
    if record_run:
        msg = ['target wrd', 'samples', 'guess mode', 'initial duplicates', 'first guess', 'vocabulary']
        output_msg(msg, record_run, run_fname)
        msg = [target_wrd, sample_number, guess_mode, str(allow_dups), starting_wrd, vocab_filename]
        output_msg(msg, record_run, run_fname)
        if reveal_mode:
            reveal_hdr = ['Run', 'guesses', 'target wrd', 'G1', 'G1R', 'G2', 'G2R', 'G3', 'G3R', 'G4', 'G4R', 'G5',
                          'G5R', 'G6', 'G6R', 'G7', 'G7R', 'G8', 'G8R', 'G9', 'G9R', 'G10', 'G10R']
            output_msg(reveal_hdr, record_run, run_fname)


def reveal_output():
    global r, guesses, run_stats, record_run, run_fname
    reveal_stat = [r, guesses]
    reveal_stat.extend(run_stats)
    output_msg(reveal_stat, False, run_fname)
    if record_run:
        output_msg(reveal_stat, record_run, run_fname)


def prologue_output():
    global conditions, sample_number, guess_mode, allow_dups, record_run, run_fname
    global target_wrd, starting_wrd, tot, vocab_filename
    average = tot / sample_number
    stat_msg = 'target_wrd: ' + target_wrd + ' , averaged ' + f'{average:.3f}' + ' guesses to solve, '
    stat_msg = stat_msg + conditions + ", " + vocab_filename
    output_msg(stat_msg, False, run_fname)
    if record_run:
        msg = ['target wrd', 'average', 'guess mode', 'initial duplicates', 'first guess', 'vocabulary']
        output_msg(msg, record_run, run_fname)
        msg = [target_wrd, average, guess_mode, str(allow_dups), starting_wrd, vocab_filename]
        output_msg(msg, record_run, run_fname)


# ====================================== setup ================================================

# Many of these variables can be overriden by command line argument
# The number of times to run guessing sessions
sample_number: int = 100
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
# rank mode:
# 0 = Occurrence
# 1 = Position
# 2 = Both
rank_mode = 2
# monkey type
rand_mode = True  # random monkeys
# rand_mode = False  # smart monkeys
# Set allow_dups to prevent letters from occurring more than once.
# This condition is used mainly for the first two guesses. Duplicate
# letter words are allowed after the second guess and due to the code
# is required to be able to correctly handle target words that have
# duplicate letters.
allow_dups = False
target_wrd = ''
guess_mode = ''
starting_wrd = ''
use_starting_wrd = -1
run_type = -1
# Timestamp like filename used for record_run
run_fname = imwm_fname()
# Records output to a CVS file having a timestamp like filename
record_run = False
# These command line arguments processed next will override and previously set variables.
process_any_arguments()
# the ranked word list dictionary, created now to use for valid input word checking
the_word_list = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, 0).get_ranked_results_wrd_lst()

# ====================================== main ================================================

# helpers.clear_scrn()  # clears terminal
print()
if record_run:
    print('Output being written to ' + run_fname)

print('Average guesses to solve Wordle sampling')
# Get the target Wordle word the guessing sessions is trying to discover.drive
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
conditions: str = ''

prelude_output()
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

    # The ending guess is the second to last guess, except when it happens by chance
    # to be the target word. The next guess being the target word can only happen if the
    # allow_dups allows for that word to be in the list. Otherwise, we get a wrong count.
    # This is a problem.
    if not word == target_wrd:
        guesses += 1
    tot = tot + guesses

    # if guesses == 2:
    #     reveal_stat = [r, guesses]
    #     reveal_stat.extend(run_stats)
    #     output_msg(reveal_stat, record_run, run_fname)
    #     guessin2 += 1
    # if guesses == 1:
    #     reveal_stat = [r, guesses]
    #     reveal_stat.extend(run_stats)
    #     output_msg(reveal_stat,record_run, run_fname)
    #     guessin1 += 1

    r = x + 1
    if reveal_mode:
        reveal_output()

    del wordletool
    average = tot / r
    # animated in progress showing
    sys.stdout.write('\033[K' + ">" + str(r) + '  avg: ' + f'{average:.2f}' + '\r')

prologue_output()

sys.stdout.write('\n')
# output_msg('guessin2 % is ' + f'{(100 * (guessin2 / sample_number)):.2f}', record_run, run_fname)
# output_msg('guessin2 count is ' + str(guessin2), record_run, run_fname)
# output_msg('guessin1 count is ' + str(guessin1), record_run, run_fname)
