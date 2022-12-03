# ----------------------------------------------------------------
# fmwm.py                                             AKS 5/2022
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
import datetime
import time
from typing import NoReturn
import helpers
import random
import argparse
import csv


def process_any_arguments() -> NoReturn:
    """
    Process any command line arguments
    """
    global debug_mode, reveal_mode, vocab_filename, target_wrd, use_starting_wrd, \
        starting_wrd, rank_mode, allow_dups, rand_mode, guess_mode, run_type, \
        sample_number, vocab_filename, record_run, do_every_wrd, query_guess, \
        query_mode, magic_mode, magic_order

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
    parser.add_argument('-v', action='store_true', help='For guessing, use the Wordle vocabulary that'
                                                        ' includes non-solution words.')
    parser.add_argument('-w', action='store_true', help='Writes output to CVS file having a timestamp filename.')
    parser.add_argument('-a', action='store_true', help='Process every vocabulary word as a target word.')
    parser.add_argument('-q', action='store', type=int,
                        help='Query list guesses Q.')
    parser.add_argument('-m', action='store', type=int,
                        help='Find the order M magic words for a target word.')

    args = parser.parse_args()
    debug_mode = args.d  # prints out lists, guesses etc.
    reveal_mode = args.l  # lists each solution run data
    magic_mode = args.m  # Find the magic words for a target word.

    if args.m is not None:
        magic_order = args.m
        if query_guess < 1:
            print(f'Aborting this run. The -m argument must be larger than 0. It was {query_guess}.')
            exit()

    if args.q is not None:
        query_guess = args.q
        if query_guess > 0:
            reveal_mode = True  # ie as if -l argument is used
            query_mode = True
        else:
            print(f'Aborting this run. The -q argument must be larger than 0. It was {query_guess}.')
            exit()

    if args.a:
        # Process every vocabulary word as a target word.
        do_every_wrd = True

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

        set_context_msg(rand_mode, rank_mode)

    if args.x is not None:
        if args.x < 1:
            sample_number = 1
            print('===> Negative value not allowed. Runs number is set to ' + str(sample_number))
        elif args.x > 1000000:
            sample_number = 1000000
            print('===> Honestly, even 1,000,000 is too many. Runs number is set to ' + str(sample_number))
            print('===> Control + C will stop the program.')
        else:
            sample_number = args.x


def clean_slate(loc_excl_l: list, loc_requ_l: list, loc_x_pos_dict: dict, loc_r_pos_dict: dict) -> NoReturn:
    """
    Clears all the objects used to hold the letter filtering information
    @param loc_excl_l: List of letters to exclude.
    @param loc_requ_l: List of letters to require
    @param loc_x_pos_dict: Dictionary of letter at positions to exclude
    @param loc_r_pos_dict: Dictionary of letters at position to require
    """
    loc_x_pos_dict.clear()
    loc_r_pos_dict.clear()
    loc_excl_l.clear()
    loc_requ_l.clear()


def get_set_target_word() -> NoReturn:
    """
    Establish and verify the target word.
    Any already set target word is verified to be in the_word_list.
    If not in list or not set, then ask for it.
    The_word_list is the selection pool. The target word has to be in the
    selection pool for solution guess verification to work properly.
    """
    global target_wrd
    while target_wrd not in the_word_list:
        target_wrd = input('Enter a valid Wordle target word: ').lower()


def get_set_starting_guess() -> NoReturn:
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


def get_set_guess_mode() -> NoReturn:
    """
    Gets and sets the general run type: random guess or ranked guess.
    If ranked guess then get and set the ranking type.
    """
    global guess_mode, allow_dups, rank_mode, rand_mode, run_type
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
        guess_mode = 'random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = 'rank mode type ' + str(rank_mode + 1) + " guesses"
        # In ranked mode the loc_allow_dups flag will be not be forced
        # so that its influence on the first and second guess can be observed.


def set_context_msg(loc_rand_mode, loc_rank_mode):
    """
    Sets the loc_guess_mode string that is used to append a status message.
    """
    global guess_mode, allow_dups
    if loc_rand_mode:
        guess_mode = 'random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = 'rank mode type ' + str(loc_rank_mode + 1) + " guesses"
        # In ranked mode the loc_allow_dups flag will be not be forced
        # so that its influence on the first and second guess can be observed.


def imwm_fname() -> str:
    """
    Returns a time timestamp like .csv filename
    @rtype: str
    """
    ts = str(datetime.datetime.now()).replace(' ', '_')
    ts = ts.replace(':', '_')
    return ts + ".csv"


def output_msg(msg: any, also2file: bool, loc_fname: str) -> NoReturn:
    """
    Outputs content to console and to csv file.
    @param msg: The content to be output
    @type also2file: bool, If true then save to csv file also.
    @param loc_fname: The filename for saving to csv file
    """
    fn_csv = loc_fname
    if also2file:
        with open(fn_csv, 'a') as f:
            if type(msg) is str:
                f.write(str(msg) + '\n')
            if type(msg) is list:
                csvwriter = csv.writer(f)
                csvwriter.writerow(msg)
    else:
        sys.stdout.write('\033[K' + str(msg) + '\n')
    return


def prelude_output(loc_sample_number, loc_guess_mode, loc_allow_dups, loc_record_run, loc_run_fname,
                   loc_starting_wrd, loc_vocab_filename, loc_do_every_wrd) -> NoReturn:
    global conditions, magic_mode, magic_order

    if not magic_mode:
        conditions = f'{loc_sample_number} samples, ' + loc_guess_mode + ', initial duplicates:' + str(loc_allow_dups)
        if len(loc_starting_wrd) == 5:
            conditions = conditions + " , first guess:" + loc_starting_wrd
        output_msg('target wrd: ' + target_wrd + ", " + conditions + ", " + loc_vocab_filename, False, loc_run_fname)
        if loc_record_run:
            if not loc_do_every_wrd:
                msg = ['target wrd', 'samples', 'guess mode', 'initial duplicates', 'first guess', 'vocabulary']
                output_msg(msg, loc_record_run, loc_run_fname)
                msg = [target_wrd, loc_sample_number, loc_guess_mode, str(loc_allow_dups), loc_starting_wrd,
                       loc_vocab_filename]
                output_msg(msg, loc_record_run, loc_run_fname)
            if reveal_mode:
                reveal_hdr = ['Run', 'guesses', 'target wrd', 'G1', 'G1R', 'G2', 'G2R', 'G3', 'G3R', 'G4', 'G4R', 'G5',
                              'G5R', 'G6', 'G6R', 'G7', 'G7R', 'G8', 'G8R', 'G9', 'G9R', 'G10', 'G10R']
                output_msg(reveal_hdr, loc_record_run, loc_run_fname)
    else:
        output_msg(f'Order {magic_order} magic words for: {target_wrd} from {loc_vocab_filename}', False,
                   loc_run_fname)
        if loc_record_run:
            if first_run:
                output_msg(f'{loc_vocab_filename} Magic Words', loc_record_run,
                           loc_run_fname)
            if reveal_mode:
                reveal_hdr = ['Index', 'Guesses', 'Target Wrd', 'Magic Wrd', 'G1R']
                output_msg(reveal_hdr, loc_record_run, loc_run_fname)


def reveal_output(r, guesses, run_stats, loc_record_run, loc_run_fname) -> NoReturn:
    reveal_stat = [r, guesses]
    reveal_stat.extend(run_stats)
    output_msg(reveal_stat, False, loc_run_fname)
    if loc_record_run:
        output_msg(reveal_stat, loc_record_run, loc_run_fname)


def prologue_output(loc_sample_number, loc_guess_mode, loc_allow_dups, loc_record_run, loc_run_fname,
                    loc_target_wrd, loc_starting_wrd, tot, loc_vocab_filename, loc_dur_tw) -> NoReturn:
    global first_run, conditions, query_set, magic_mode
    if not magic_mode:
        average = tot / loc_sample_number
        stat_msg = 'target wrd: ' + loc_target_wrd + ', averaged ' + f'{average:.3f} guesses to solve, '
        stat_msg = stat_msg + conditions + ', ' + loc_vocab_filename + f', {loc_dur_tw:0.4f} seconds'
        output_msg(stat_msg, False, loc_run_fname)

        if loc_record_run:
            if not do_every_wrd or first_run:
                msg = ['target wrd', 'average', 'guess mode', 'initial duplicates', 'first guess',
                       'vocabulary', 'samples', 'seconds']
                output_msg(msg, loc_record_run, loc_run_fname)
            msg = [loc_target_wrd, average, loc_guess_mode, str(loc_allow_dups), loc_starting_wrd,
                   loc_vocab_filename, loc_sample_number, loc_dur_tw]
            output_msg(msg, loc_record_run, loc_run_fname)

    else:
        if loc_record_run:
            if not do_every_wrd or first_run:
                msg = ['Target', 'Qty', 'Sec', 'Magic Wrds =>']
                output_msg(msg, loc_record_run, loc_run_fname)
            record_stat = [target_wrd, len(query_set), f'{loc_dur_tw:0.4f}']
            query_list = list(query_set)
            query_list.sort()
            record_stat.extend(query_list)
            output_msg(record_stat, loc_record_run, loc_run_fname)

    first_run = False
    query_output(target_wrd)


def query_output(loc_target_wrd):
    if query_mode:
        query_list = list(query_set)
        query_list.sort()
        if not magic_mode:
            stat_msg = f'Encountered {len(query_set)} #{query_guess - 1} guesses ' \
                       f'that eliminate all but the solution {loc_target_wrd} guess:\n{query_list}'
        else:
            stat_msg = f'Encountered {len(query_set)} #1 order {magic_order} magic word guesses ' \
                       f'that eliminate all but {magic_order} guesses:\n{query_list}'
        # print(stat_msg)
        sys.stdout.write(f'\033[K {stat_msg}\n')


def standard_monkey(loc_sample_number: int, loc_wrd_x: int):
    global dur_tw, guess_mode, allow_dups, rank_mode, rand_mode, run_type, query_set

    if record_run:
        print('Output being written to ' + run_fname)

    print(f'{loc_wrd_x}  word: Average guesses to solve Wordle by sampling {loc_sample_number} tries.')
    # Confirm the target Wordle word the guessing sessions is trying to discover. Note: The monkey can
    # be started with the target word already set.
    get_set_target_word()
    # Set the first guess if desired.
    get_set_starting_guess()
    # Set the guess mode and rank mode.
    get_set_guess_mode()
    # All samples are identical when there is a fixed starting word and
    # a fixed rank selection method. So run only one sample.
    if use_starting_wrd == 1 and not rand_mode:
        loc_sample_number = 1

    tot: int = 0  # total number of guesses
    word: str = ''  # the guess

    prelude_output(loc_sample_number, guess_mode, allow_dups, record_run, run_fname, starting_wrd,
                   vocab_filename, do_every_wrd)
    start_mt = time.perf_counter()  # record monkey start time
    for x in range(loc_sample_number):
        # initialize a fresh wordletool instance
        wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, allow_dups, rank_mode)
        guesses = 0
        run_stats = list([])
        run_stats.append(target_wrd)
        clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)
        helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
        # Get the word list using the optional no_rank argument with loc_rand_mode.
        # No ranking or sorting is needed when all guesses are random.
        loc_the_word_list = wordletool.get_word_list(guesses + 1, '', debug_mode, rand_mode)
        # This loop ends when the last guess results in only one remaining word that fits the
        # pattern. That word, being the target word, will be the solving guess. The loop's last
        # guess is therefore the actual second to last guess, except when it happens by chance
        # to be the target word.
        while len(loc_the_word_list) > 1:
            if guesses == 0 and use_starting_wrd == 1:
                word = starting_wrd
            else:
                if rand_mode:
                    word, rank = random.choice(list(loc_the_word_list.items()))
                else:
                    if guesses == 0:
                        # first pick has to be random in this sampling scheme
                        word, rank = random.choice(list(loc_the_word_list.items()))
                        # word, rank = list(loc_the_word_list.items())[-1]
                    else:
                        # all other picks are top rank
                        word, rank = list(loc_the_word_list.items())[-1]

            run_stats.append(word)
            # At this point the guess word has been selected from the results of the prior guess.
            # Normal strategy for non loc_rand_mode, ie not picking anything random, is to not select
            # words having duplicate letters for at least the first two guesses. Allow_dups is
            # likely already false for the first selection pool, ie the first pick does not allow dups.
            # Dups should be allowed for the third guess and beyond. Dups at the second guess depends
            # on how many dups there are compared to the number of non dups.

            # analyze this new word against the target word and update the filter criteria
            helpers.analyze_pick_to_solution(target_wrd, word, excl_l, x_pos_dict, r_pos_dict)

            if guesses > 0 and not allow_dups:  # need a new wordletool allowing dups
                del wordletool
                wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, rank_mode)
                allow_dups = True

            # Now load in the filter criteria
            helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
            # Get the revised word list using the optional no_rank argument with loc_rand_mode
            # No ranking or sorting is needed when all guesses are random.
            loc_the_word_list = wordletool.get_word_list(guesses + 2, word, debug_mode, rand_mode)
            # Because the target word is known to exist in the overall pool then loc_the_word_list can
            # only be less than 1 when the target had duplicate letters and the pool was not
            # allowing duplicates. Here that condition is checked and the pool revised to allow
            # duplicates.
            if len(loc_the_word_list) < 1:
                del wordletool
                wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, rank_mode)
                helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)
                loc_the_word_list = wordletool.get_word_list(guesses + 2, word, debug_mode, rand_mode)

            run_stats.append(len(loc_the_word_list))
            guesses += 1

        # The ending guess is the second to last guess, except when it happens by chance
        # to be the target word. The next guess being the target word can only happen if the
        # loc_allow_dups allows for that word to be in the list. Otherwise, we get a wrong count.
        # This is a problem.
        if not word == target_wrd:
            guesses += 1
        tot = tot + guesses

        r = x + 1
        # Reveal_mode is where output is desired to show the guesses and their pool impact or
        # to show particular guess by words.
        if reveal_mode:
            if not query_mode:
                reveal_output(r, guesses, run_stats, record_run, run_fname)
            else:
                if guesses == query_guess and run_stats[(query_guess - 1) * 2] == 1:
                    reveal_output(r, guesses, run_stats, record_run, run_fname)
                    query_set.add(run_stats[(query_guess - 1) * 2 - 1])

        del wordletool
        average = tot / r
        # animated in progress showing
        sys.stdout.write('\033[K' + ">" + str(r) + '  avg: ' + f'{average:.2f}' + '\r')

    dur_tw = time.perf_counter() - start_mt  # this word's process time
    prologue_output(loc_sample_number, guess_mode, allow_dups, record_run, run_fname,
                    target_wrd, starting_wrd, tot, vocab_filename, dur_tw)

    sys.stdout.write('\n')


def charm_word_monkey(loc_wrd_x: int) -> NoReturn:
    """
    Intended to find only the first guess words that reduce the -v vocabulary selection
    pool to the target word.
    @param loc_wrd_x:
    """
    global dur_tw, guess_mode, allow_dups, rank_mode, rand_mode, run_type, query_set,\
        query_mode, target_wrd, magic_order

    if record_run:
        print('Output being written to ' + run_fname)

    print(f'{loc_wrd_x}  Finding lucky charms for: {target_wrd}')
    # Confirm the target Wordle word the guessing sessions is trying to discover. Note: The monkey can
    # be started with the target word already set.
    get_set_target_word()
    # Need to iterate through all unranked words in the -v vocabulary
    candidate_list = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, 0) \
        .get_ranked_results_wrd_lst(True)
    r = 0
    mw_qty = 0
    rand_mode = True
    guess_mode = 'iterate guesses'
    allow_dups = True
    query_mode = True
    query_set.clear()
    loc_n = len(candidate_list)
    prelude_output(loc_wrd_x, guess_mode, allow_dups, record_run, run_fname, starting_wrd,
                   vocab_filename, do_every_wrd)
    # Iterate through each word in the candidates list
    start_mt = time.perf_counter()  # record monkey start time
    for loc_key in candidate_list:
        # initialize a fresh wordletool instance, loc_allow_dups must be true
        wordletool = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True, 0)
        guesses = 1
        run_stats = list([])
        run_stats.append(target_wrd)
        clean_slate(excl_l, requ_l, x_pos_dict, r_pos_dict)

        # This loop ends when the last guess results in only one remaining word that fits the
        # pattern. That word, being the target word, will be the solving guess. The loop's last
        # guess is therefore the actual second to last guess, except when it happens by chance
        # to be the target word.
        word = loc_key
        run_stats.append(word)

        # At this point the guess word is selected.
        # Analyze this new word against the target word and update the filter criteria
        helpers.analyze_pick_to_solution(target_wrd, word, excl_l, x_pos_dict, r_pos_dict)

        # Now load in the resulting filter criteria
        helpers.load_grep_arguments(wordletool, excl_l, requ_l, x_pos_dict, r_pos_dict)

        # Get the word list using the optional no_rank argument with loc_rand_mode
        # No ranking or sorting is needed when all guesses are random.
        loc_the_word_list = wordletool.get_word_list(guesses + 2, word, debug_mode, True)

        # Because the target word is known to exist in the overall pool then loc_the_word_list can
        # only be 1 when the filter criteria filters to only the target.

        run_stats.append(len(loc_the_word_list))

        if len(loc_the_word_list) == magic_order:
            # Word is the target or is a charm word.
            # The ending guess is the second to last guess, except when it happens by chance
            # to be the target word. The next guess being the target word can only happen if the
            # loc_allow_dups allows for that word to be in the list. Otherwise, we get a wrong count.
            #
            if not word == target_wrd:
                guesses += 1

            # Only the first guess word that results in the desired magic_order pool size is of interest.
            # Guesses would be 2 at this point.
            if guesses == 2 and run_stats[2] == magic_order:
                query_set.add(run_stats[1])
                # Reveal_mode is where output is desired to show the guesses and their pool impact
                if reveal_mode:
                    reveal_output(r, guesses, run_stats, record_run, run_fname)

        del wordletool
        # animated in progress showing
        r += 1
        mw_qty = len(query_set)
        sys.stdout.write(f'\033[K> {r} Searching through {loc_n} words in {vocab_filename}'
                         f' for {target_wrd} magic word ...  finding: {mw_qty}\r')

    dur_tw = time.perf_counter() - start_mt  # this word's process time
    prologue_output(loc_wrd_x, guess_mode, allow_dups, record_run, run_fname,
                    target_wrd, starting_wrd, mw_qty, vocab_filename, dur_tw)

    sys.stdout.write('\n')


# ==== setup ======= These variables can be overriden by command line argument. ================

# The number of times to run guessing sessions
sample_number: int = 100
debug_mode = False  # prints out lists, guesses etc.
reveal_mode = False  # reveals each solution run data
data_path = 'worddata/'  # path from what will be helpers.py folder to data folder
letter_rank_file = 'letter_ranks.txt'
vocab_sol_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# loc_vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list

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
# loc_rand_mode = False  # smart monkeys
# Set loc_allow_dups to prevent letters from occurring more than once.
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
first_run = True
do_every_wrd = False  # Process every vocabulary word as a target word.
conditions = ''
dur_tw = 0.0  # seconds to process word
dur_sf = 0.0  # seconds so far in list process
query_set = set()
query_guess = 1
query_mode = False
magic_order = 1
magic_mode = False
# Timestamp like filename used for loc_record_run
run_fname = imwm_fname()
# Records output to a CVS file having a timestamp like filename
record_run = False
# These command line arguments processed next will override all previously set variables.
process_any_arguments()

# ====================================== main ================================================
if __name__ == "__main__":
    try:
        wrd_x = 1
        if do_every_wrd:
            # The targets are the words for which the monkey seeks guesses to solve.
            # Here only the words that can be a solution will be considered a target word.
            # The target pool is not the guess pool. The -v argument selects the guess pool.
            targets = helpers.ToolResults(data_path, vocab_sol_filename, letter_rank_file, True, 0) \
                .get_ranked_results_wrd_lst(True)
            n = len(targets)
            dsf = datetime.timedelta(0)
            avg_t = 0
            for key in targets:
                target_wrd = key
                # A ranked word list dictionary is now created to use for valid input word checking,
                # Ranking is not needed. For faster running the optional no_rank argument is True.
                the_word_list = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True,
                                                    0).get_ranked_results_wrd_lst(True)
                # Run the monkey. The monkey will notice this loc_target_wrd
                if not magic_mode:
                    standard_monkey(sample_number, wrd_x)
                else:
                    charm_word_monkey(wrd_x)

                dur_sf = dur_sf + dur_tw
                avg_t = dur_sf / wrd_x
                etf = datetime.timedelta(seconds=((n - wrd_x) * avg_t))
                dsf = datetime.timedelta(seconds=dur_sf)
                wrd_x += 1
                # Do targets remain?
                if wrd_x < len(targets):
                    print(f'Duration so far: {dsf}, {avg_t:0.4f} seconds/word, ETF: {etf}')
            # Finished all targets
            print(f'Process done. Duration: {dsf}, {avg_t:0.4f} seconds/word')
        else:
            the_word_list = helpers.ToolResults(data_path, vocab_filename, letter_rank_file, True,
                                                0).get_ranked_results_wrd_lst()
            if not magic_mode:
                standard_monkey(sample_number, wrd_x)
            elif magic_mode:
                charm_word_monkey(wrd_x)

    except KeyboardInterrupt:
        sys.stdout.write(f'\033[K user canceled. \n')
        # Output any encountered query results.
        query_output(target_wrd)
