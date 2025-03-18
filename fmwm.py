# ----------------------------------------------------------------
# fmwm.py                                             AKS 10/2022
# Finite Monkey Wordle Machine
# Measures the average number of guesses required to arrive at the
# Wordle target word using various guess strategies. Guesses are
# selected from the vocabulary list that has words removed based
# upon the previous guesses in the sample trial. The play is
# 'hard mode'.
# The base strategy is to guess only random words. One purpose is
# to examine the average required guesses as word difficulty.
#
# Expanded to find M order magic words.
# ----------------------------------------------------------------
# This code suffers from being the first ever code!   AKS 03/2025
# ----------------------------------------------------------------
import sys
import datetime
import time
import helpers
import random
import argparse
import csv


def process_any_arguments() -> None:
    """
    Process any command line arguments
    """
    global debug_mode, reveal_mode, botadd_sol_filename, vocab_full_filename,\
        vocab_standard_target_filename, vocab_standard_guess_filename, \
        vocab_magic_target_filename, vocab_magic_guess_filename, use_starting_wrd, \
        starting_wrd, target_wrd, rank_mode, allow_dups, rand_mode, guess_mode, run_type, \
        sample_number, record_run, do_every_wrd, query_guess, \
        query_mode, magic_mode, magic_order, ts_ptw, ts_psw, ts_pmo, ts_pqm, ts_ptw, \
        ts_prt, ts_psn, ts_ppw, resume, resume_after_wrd

    parser = argparse.ArgumentParser(description='Process command line settings.')
    parser.add_argument('-d', action='store_true', help='Prints out lists, guesses etc.')
    parser.add_argument('-l', action='store_true', help='Lists each solution run data')
    parser.add_argument('-n', action='store_true', help='Random first guess word, ie skip asking about it')
    parser.add_argument('-t', action='store', help='Use this target word T.')
    parser.add_argument('-s', action='store', help='Use this first guess word S.')
    parser.add_argument('-r', action='store', type=int, choices=range(0, 5),
                        help='Guess type: Random(0),Rank Occurrence (1),Rank Position (2), Both (3) or Entropy (4)')
    parser.add_argument('-x', action='store', type=int,
                        help='Override the number of sampling runs to be this number X.')
    parser.add_argument('-v', action='store_true', help='For guessing, use the Wordle vocabulary that'
                                                        ' includes non-solution words.')
    parser.add_argument('-z', action='store_true', help='For word targets, use the Wordle vocabulary that'
                                                        ' includes non-solution words.')
    parser.add_argument('-w', action='store_true', help='Writes output to CSV file having a timestamp filename.')
    parser.add_argument('-a', action='store_true', help='Process every vocabulary word as a target word.')
    parser.add_argument('-q', action='store', type=int,
                        help='Show guesses that solve on the Qth guess.')
    parser.add_argument('-m', action='store', type=int,
                        help='Find the order M magic words for a target word.')
    parser.add_argument('-p', action='store', help='Pick-up, ie. restart, after seeing word P.')

    args = parser.parse_args()
    debug_mode = args.d  # prints out lists, guesses etc.
    reveal_mode = args.l  # lists each solution run data
    magic_mode = args.m  # Find the magic words for a target word.

    if args.m is not None:
        magic_order = args.m
        m_max = len(unranked_large_word_dict()) - 1
        if magic_order < 1:
            print(f'Aborting this run. The magic order -m argument must be larger than 0. It was {magic_order}.')
            exit()
        elif magic_order > m_max:
            print(f'Aborting this run. The magic order -m argument must be smaller than {m_max}. It was {magic_order}.')
            exit()
        ts_pmo = f'M{magic_order:03.0f}_'  # magic order timestamp element

    if args.q is not None:
        query_guess = args.q
        if query_guess > 0:
            reveal_mode = True  # ie as if -l argument is used
            query_mode = True
            ts_pqm = f'Q{query_guess}_'  # query guess timestamp element
        else:
            print(f'Aborting this run. The -q argument must be larger than 0. It was {query_guess}.')
            exit()

    if args.a:
        # Process every vocabulary word as a target word.
        do_every_wrd = True

    if args.w:
        # Writes output to CSV file having a timestamp filename.
        record_run = True

    if args.v:
        # For guessing, use the Wordle vocabulary that includes non-solution words
        vocab_standard_guess_filename = vocab_full_filename
        vocab_magic_guess_filename = vocab_full_filename
    else:
        vocab_standard_guess_filename = botadd_sol_filename
        vocab_magic_guess_filename = botadd_sol_filename

    if args.z:
        # For word targets, use the Wordle vocabulary that includes non-solution words.
        vocab_magic_target_filename = vocab_full_filename
        vocab_standard_target_filename = vocab_full_filename
    else:
        vocab_magic_target_filename = botadd_sol_filename
        vocab_standard_target_filename = botadd_sol_filename


    if args.n:
        # no starting word, skip asking about it
        use_starting_wrd = 0

    if args.t is not None:
        # use this target word
        target_wrd = args.t
        ts_ptw = f'T_{target_wrd}_'  # target word timestamp element

    if args.s is not None:
        use_starting_wrd = 1
        starting_wrd = args.s
        ts_psw = f'S_{starting_wrd}_'  # starting word timestamp element

    if args.p is not None:
        resume = True
        resume_after_wrd = args.p
        ts_ppw = f'P_{resume_after_wrd}_'  # resume_after_wrd timestamp element

    if args.r is not None:
        if args.r == 0:
            rand_mode = True
            run_type = 0
            rank_mode = -1
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
        if args.r == 4:
            # Rank by Entropy (4),
            rank_mode = 3

        set_context_msg(rand_mode, rank_mode)

    ts_prt = f'R{(rank_mode + 1)}_'  # rank mode timestamp element

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

    ts_psn = f'X{sample_number}_'  # sample number timestamp element


def unranked_word_dict() -> dict:
    """
    A ranked word list dictionary is now created to use for valid input word checking
    and other uses where ranking is not needed. For faster running, the optional
    no_rank argument is True.
    @return: dict
    """
    return helpers.ToolResults(data_path,
                               vocab_standard_guess_filename, letter_rank_file, True, 0, True).get_ranked_grep_result_wrd_lst(True)

def unranked_large_word_dict() -> dict:
    """
    A ranked word list dictionary is now created to use for valid input word checking
    and other uses where ranking is not needed. For faster running, the optional
    no_rank argument is True.
    @return: dict
    """
    return helpers.ToolResults(data_path,
                               vocab_full_filename, letter_rank_file, True, 0, True).get_ranked_grep_result_wrd_lst(True)


def clean_slate(loc_excl_l: list, loc_requ_l: list, loc_x_pos_dict: dict,
                loc_r_pos_dict: dict) -> None:
    """
    DECLARES and clears all the objects used to hold the letter filtering information
    @param loc_excl_l: List of letters to exclude.
    @param loc_requ_l: List of letters to require
    @param loc_x_pos_dict: Dictionary of letter at positions to exclude
    @param loc_r_pos_dict: Dictionary of letters at position to require
    """
    loc_x_pos_dict.clear()
    loc_r_pos_dict.clear()
    loc_excl_l.clear()
    loc_requ_l.clear()


def set_late_timestamp_elements() -> None:
    """
    Sometimes a .csv file is desired but not every run parameters is specified
    in the command line arguments. These parameters are set late outside the
    command line parser where the associated file name prefix clues are set. This
    function sets the prefixes again regardless of needing to do so.
    """
    global ts_ptw, ts_psw, ts_prt, ts_ppw
    if len(target_wrd) > 0:
        ts_ptw = f'T_{target_wrd}_'  # target word timestamp element
    if len(starting_wrd) > 0:
        ts_psw = f'S_{starting_wrd}_'  # starting word timestamp element
    if len(resume_after_wrd) > 0:
        ts_ppw = f'P_{resume_after_wrd}_'  # resume_after_wrd timestamp element
    ts_prt = f'R{(rank_mode + 1)}_'  # rank mode timestamp element


def confirm_resume_after_wrd() -> None:
    """
    If this is a resume run where process needs to resume after a certain word,
    that resume_after_wrd, which would have come in as a command line argument,
    needs to be confirmed to exist in the vocabulary.
    @return:
    """
    global resume_after_wrd, resume
    if not resume:
        return
    while resume_after_wrd not in unranked_large_word_dict():
        resume_after_wrd = input('Enter a valid Wordle word to resume after: ').lower()


def ask_for_target_word() -> None:
    """
    Establish and verify the target word.
    Any already set target word is verified to be in the_word_list.
    If not in list or not set, then ask for it.
    The_word_list is the selection pool. The target word has to be in the
    selection pool for solution guess verification to work properly.
    """
    global target_wrd
    if do_every_wrd:
        return
    while target_wrd not in unranked_large_word_dict():
        target_wrd = input('Enter a valid Wordle target word: ').lower()


def ask_for_starting_guess() -> None:
    """
    Ask for and set a given first guess word to be used in every session.
    """
    global starting_wrd, use_starting_wrd
    while use_starting_wrd == -1:
        response = input('Run using a given first guess? Enter y/n: ').lower()
        if response == 'y':
            while starting_wrd not in unranked_large_word_dict():
                starting_wrd = input('Enter a valid Wordle first guess word: ').lower()
                use_starting_wrd = 1
        if response == 'n':
            use_starting_wrd = 0


def ask_for_guess_mode() -> None:
    """
    Gets and sets the general run type: random guess or ranked guess.
    If ranked guess then get and set the ranking type.
    """
    global guess_mode, allow_dups, rank_mode, rand_mode, run_type
    if run_type != -1:
        return
    while run_type == -1:
        response: str = input(
            'Guess Type? Random(0), or Rank by Occurrence (1), Position (2) or Both (3), Best Entropy (4) Enter 0,1,2,3 or 4: ')
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
        if response == '4':
            rand_mode = False
            run_type = 1
            rank_mode = 3

    if rand_mode:
        guess_mode = 'random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        # For entropy mode, 4, random selection will occur for equal
        # entropy words.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = 'rank mode type ' + str(rank_mode + 1) + " guesses"
        # In ranked mode 1,2 & 3 the loc_allow_dups flag will not be forced
        # so that its influence on the first and second guess can be observed.
        # But not for entropy rank mode 3
        if rank_mode > 2:
            del allow_dups
            allow_dups = True


def set_context_msg(loc_rand_mode, loc_rank_mode):
    """
    Sets the loc_guess_mode string that is used to append a status message.
    """
    global guess_mode, allow_dups
    if loc_rand_mode:
        guess_mode = 'random guesses'
        # For random mode to represent a base condition, duplicate letter
        # words show be allowed regardless of its previous setting.
        # For entropy mode, 4, random selection will occur for equal
        # entropy words.
        del allow_dups
        allow_dups = True
    else:
        guess_mode = 'rank mode type ' + str(loc_rank_mode + 1) + " guesses"
        # In ranked mode the loc_allow_dups flag will not be forced
        # so that its influence on the first and second guess can be observed.
        # But not for entropy rank mode 3
        if rank_mode > 2:
            del allow_dups
            allow_dups = True


def fmwm_fname() -> str:
    """
    Returns a time timestamp like .csv filename
    Added to the actual timestamp are filename prefixes that correspond
    to many of the operation modes so that it is possible to know the
    .csv file purpose.
    @rtype: str
    """
    global ts_pmo, ts_pqm, ts_prt, ts_psn, ts_ptw, ts_psw, ts_ppw
    fx = '.csv'
    ts = str(datetime.datetime.now()).replace(' ', '_')
    ts = ts.replace(':', '_')

    if len(ts_pmo):
        ts_psn = ''
    ts = f'{ts_pmo}{ts_prt}{ts_pqm}{ts_psn}{ts_ptw}{ts_psw}{ts_ppw}{ts}{fx}'

    return ts


def output_msg(msg: any, also2file: bool, loc_fname: str) -> None:
    """
    Outputs content to console and to csv file.
    @param msg: The content to be output
    @param also2file: If true then save to csv file also.
    @param loc_fname: The filename for saving to csv file
    """
    fn_csv = loc_fname
    if also2file:
        try:
            with open(fn_csv, 'a') as f:
                if type(msg) is str:
                    f.write(str(msg) + '\n')
                if type(msg) is list:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(msg)
        except IOError:
            sys.stdout.write(f'\nIOError for file {fn_csv}\n')
            sys.stdout.write(f'trying to write {msg}\n')
            exit()
    else:
        sys.stdout.write('\033[K' + str(msg) + '\n')
    return


def prelude_output(loc_sample_number, loc_guess_mode, loc_allow_dups, loc_record_run, loc_run_fname,
                   loc_starting_wrd, loc_vocab_filename, loc_do_every_wrd, loc_sol_filename=None) -> None:
    """
    Reports the conditions for the impending sample run
    @param loc_sample_number: total overall number of guesses
    @param loc_guess_mode: guess mode description
    @param loc_allow_dups: allow duplicates bool
    @param loc_record_run: save to a file bool
    @param loc_run_fname: filename to save to
    @param loc_starting_wrd: the starting word for this run, could be blank
    @param loc_vocab_filename: the vocabulary being used for guesses (target list, strict hard mode)
    @param loc_do_every_wrd: bool indicates all words in vocabulary are being examined
    @param loc_sol_filename: the solutions vocabulary being used for magic words
    """
    global conditions, magic_mode, magic_order, first_run

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
        output_msg(f'Order {magic_order} magic words for: {target_wrd}.\nThe guesses are from {loc_vocab_filename}'
                   f' list for solutions in {loc_sol_filename} list.', False,
                   loc_run_fname)
        if loc_record_run:
            if first_run:
                output_msg(f'Order {magic_order} magic words from {loc_vocab_filename}',
                           loc_record_run, loc_run_fname)
            if reveal_mode:
                reveal_hdr = ['Index', 'Guesses', 'Target Wrd', 'Magic Wrd', 'G1R']
                output_msg(reveal_hdr, loc_record_run, loc_run_fname)


def reveal_output(x, guesses, run_stats, loc_record_run, loc_run_fname) -> None:
    """
    Reveal mode is the option to report the results for an xth sample run
    @param x: The xth sample attempt
    @param guesses: the number of guesses required
    @param run_stats: the guesses and their resulting pool sizes
    @param loc_record_run: save to file bool
    @param loc_run_fname: filename for recording
    """
    reveal_stat = [x, guesses]
    reveal_stat.extend(run_stats)
    output_msg(reveal_stat, False, loc_run_fname)
    if loc_record_run:
        output_msg(reveal_stat, loc_record_run, loc_run_fname)


def prologue_output(loc_sample_number, loc_guess_mode, loc_allow_dups, loc_record_run, loc_run_fname,
                    loc_target_wrd, loc_starting_wrd, tot, loc_vocab_filename, loc_dur_tw) -> None:
    """
    Reports the results of a sample run
    @param loc_sample_number: total overall number of guesses
    @param loc_guess_mode: guess mode description
    @param loc_allow_dups: allow duplicates bool
    @param loc_record_run: save to a file bool
    @param loc_run_fname: filename to save
    @param loc_target_wrd: the target word for this run
    @param loc_starting_wrd: the starting word for this run, could be blank
    @param tot: total overall number of guesses required to solve
    @param loc_vocab_filename: the vocabulary filename (target list, strict hard mode)
    @param loc_dur_tw: the time duration for this run
    """
    global first_run, conditions, query_set, magic_mode, query_mode
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
    if query_mode:
        query_output(target_wrd)


def query_output(loc_target_wrd):
    """
    Output query type summary to the console
    @param loc_target_wrd:
    """
    query_list = list(query_set)
    query_list.sort()
    if not magic_mode:
        stat_msg = f'Encountered {len(query_set)} #{query_guess - 1} guesses ' \
                   f'that eliminate all but the solution {loc_target_wrd} guess:\n{query_list}'
    else:
        stat_msg = f'Encountered {len(query_set)} order #{magic_order} magic word guesses ' \
                   f'that eliminate all but {magic_order} guesses:\n{query_list}'
    # print(stat_msg)
    sys.stdout.write(f'\033[K{stat_msg}\n')


def standard_monkey(loc_sample_number: int, loc_wrd_x: int):
    global dur_tw, guess_mode, allow_dups, rank_mode, rand_mode, run_type, query_set, run_fname, \
    vocab_standard_guess_filename, vocab_standard_target_filename

    if record_run:
        print('Output being written to ' + run_fname)

    base_str = f'{loc_wrd_x} word: {target_wrd} '
    if (use_starting_wrd == 1) and not (rank_mode > 2 or rank_mode == -1):
        print(f'{base_str} '
              f'Only one sample needed for guess type {rank_mode + 1} when a starting word is specified.')
    else:
        print(f'{base_str} '
              f'Average guesses to solve Wordle by sampling {loc_sample_number} tries.')
        if rank_mode > 2:
            print(f'-- The processing time duration varies exponentially with the starting word result size!')


    std_x_pos_dict = {}  # exclude position dictionary
    std_r_pos_dict = {}  # require position dictionary
    std_excl_l = []  # the exclude letters list
    std_requ_l = []  # the require letters list
    std_multi_code = ''  # multiple same letters accounting code

    # All samples are identical when there is a fixed starting word and
    # a fixed rank selection method. So run only one sample.
    # But not when using entropy. Entropy can return multiple choices.
    if rank_mode < 3:
        if use_starting_wrd == 1 and not rand_mode:
            loc_sample_number = 1

    tot: int = 0  # total number of guesses
    guess_word: str = ''  # the guess

    prelude_output(loc_sample_number, guess_mode, allow_dups, record_run, run_fname, starting_wrd,
                   vocab_standard_target_filename, do_every_wrd)
    start_mt = time.perf_counter()  # record monkey start time
    if debug_mode:
        print(f'Running the standard monkey {loc_sample_number} times.')

    # sample_number is the number of solving runs as controlled by the -x command line argument. It
    # is the number of times to solve the target word using the run mode.
    for x in range(loc_sample_number):
        # initialize a fresh targets_wordletool instance
        targets_wordletool = helpers.ToolResults(data_path, vocab_standard_target_filename, letter_rank_file, allow_dups,
                                                 rank_mode, True)
        # initialize a fresh guess_pool_wordletool instance
        guess_pool_wordletool = helpers.ToolResults(data_path, vocab_standard_guess_filename, letter_rank_file, allow_dups,
                                                    rank_mode, True)

        guesses = 0
        run_stats = list([])
        run_stats.append(target_wrd)

        # For some reason, td_excl_l, std_requ_l, std_x_pos_dict, std_r_pos_dict, are maintained outside
        # of ToolResults. So they must be cleared
        clean_slate(std_excl_l, std_requ_l, std_x_pos_dict, std_r_pos_dict)

        std_multi_code.replace(std_multi_code,'')

        # Get the guess word list using the optional no_rank argument with loc_rand_mode.
        # No ranking or sorting is needed when all guesses are random as per rand_mode
        loc_targets_word_list_dict = targets_wordletool.get_word_list(guesses + 1, '', debug_mode, rand_mode)
        loc_guess_pool_word_list_dict = guess_pool_wordletool.get_word_list(guesses + 1, '', debug_mode, rand_mode)

        # When using entropy mode, the guess list should not be revised after every guess.
        # Here a special guess list is made for use in entropy mode.
        if rank_mode > 2:
            loc_static_guess_pool_word_list_dict = guess_pool_wordletool.get_word_list(guesses + 1, '', debug_mode,
                                                                                       rand_mode)
            special_guess_list = list(loc_static_guess_pool_word_list_dict.keys())

        # This loop ends when the previous guess results in only one remaining target word that fits the
        # pattern.That word, being the target word will be the solving guess. The loop's previous
        # guess is therefore the actual second to last guess, except when it happens by a chance
        # to be the target word.
        while len(loc_targets_word_list_dict) > 1:
            if guesses == 0 and use_starting_wrd == 1:
                guess_word = starting_wrd
            else:
                # Recall, the guess pool dict would have been already ranked by now if ranking
                # was called for.
                # Note: Entropy ranking is not ranked by the wordletool.

                # The guess pool should be the dwindling targets pool.
                guess_pool_word_tuples_list = list(loc_targets_word_list_dict.items())

                # Use random choice if random mode (-r 0)
                if rand_mode:
                    guess_word, guess_rank = random.choice(guess_pool_word_tuples_list)
                else:
                    # If not entropy mode (-r 4), then random on first pick.
                    # Otherwise, make a ranked choice.
                    # Having a starting word does not reach here.
                    if rank_mode != 3:
                        if guesses == 0:
                            # the first pick has to be random in this sampling scheme
                            guess_word, guess_rank = random.choice(guess_pool_word_tuples_list)
                        else:
                            # all other picks are the top ranked word
                            guess_word, guess_rank = guess_pool_word_tuples_list[-1]
                    else:
                        # This for best (highest) entropy selection mode.
                        targets_list = list(loc_targets_word_list_dict.keys())
                        best_ent_wrds_list = list(helpers.best_entropy_outcomes_guess_dict(targets_list,
                                                                                       special_guess_list,
                                                                                       debug_mode))
                        # There could be multiple equal highest entropy words.
                        # Make a random choice.
                        guess_word = random.choice(best_ent_wrds_list)
                        if debug_mode:
                            print(f'- Selected {guess_word} for the next round.')

            # Adding just the guess to the stats.
            # The remaining words result of this guess have yet to be determined.
            run_stats.append(guess_word)

            # At this point, the guess word has been selected from the results of the prior guess.
            # Normal strategy for non loc_rand_mode, ie not picking anything random, is to not select
            # words having duplicate letters for at least the first two guesses. Allow_dups is
            # likely already false for the first selection pool, ie the first pick does not allow dups.
            # Dups should be allowed for the third guess and beyond.

            # Analyze this new guess word against the target word and update the filter criteria.
            # Note: This process does not apply the filter criteria.
            # It only updates it.
            [std_excl_l,
             std_x_pos_dict,
             std_r_pos_dict,
             std_multi_code] = helpers.analyze_pick_to_solution(target_wrd,
                                                                guess_word,
                                                                std_excl_l,
                                                                std_x_pos_dict,
                                                                std_r_pos_dict)

            # If needed, get a new targets_wordletool allowing dups before applying the new filter criteria.
            if (guesses > 0 and not allow_dups) or (rank_mode > 2):
                del targets_wordletool
                targets_wordletool = helpers.ToolResults(data_path, vocab_standard_target_filename, letter_rank_file,
                                                         True, rank_mode, True)
                allow_dups = True

            # Now load in the filter criteria
            helpers.load_grep_arguments(targets_wordletool,
                                        std_excl_l,
                                        std_requ_l,
                                        std_x_pos_dict,
                                        std_r_pos_dict,
                                        std_multi_code)

            # Get the revised remaining targets word list using the optional no_rank argument with loc_rand_mode
            # No ranking or sorting is needed when all guesses are random as per rand_mode argument.
            loc_targets_word_list_dict = targets_wordletool.get_word_list(guesses + 2, guess_word, debug_mode, rand_mode)
            # Because the target word is known to exist in the overall pool then loc_guess_pool_word_list_dict can
            # only be less than 1 when the target had duplicate letters and the pool was not
            # allowing duplicates. Here that condition is checked and the pool revised to allow
            # duplicates.
            if len(loc_targets_word_list_dict) < 1:
                del targets_wordletool
                targets_wordletool = helpers.ToolResults(data_path, vocab_standard_target_filename,
                                                         letter_rank_file, True,
                                                         rank_mode, True)
                helpers.load_grep_arguments(targets_wordletool,
                                            std_excl_l, std_requ_l,
                                            std_x_pos_dict, std_r_pos_dict,
                                            std_multi_code)
                loc_targets_word_list_dict = targets_wordletool.get_word_list(guesses + 2, guess_word,
                                                                              debug_mode, rand_mode)

            # this is reporting then new remaining solutions word count
            run_stats.append(len(loc_targets_word_list_dict))
            guesses += 1
        # end while at this point

        # The ending guess is the second to last guess, except when it happens by chance
        # to be the target word. The next guess being the target word can only happen if the
        # loc_allow_dups allows for that word to be in the list. Otherwise, we get a wrong count.
        # This is a tricky problem.
        # Reviewed a year later. This is still the way.
        if not guess_word == target_wrd:
            guesses += 1
            # reveal_mode output is very confusing without adding the target word to run_stats.
            # Otherwise, the word count does not appear to agree with the guess count.
            run_stats.append(target_wrd)
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

        del targets_wordletool
        average = tot / r
        # animated in progress showing
        sys.stdout.write('\033[K' + ">" + str(r) + '  avg: ' + f'{average:.2f}' + '\r')

    dur_tw = time.perf_counter() - start_mt  # this word's process time
    prologue_output(loc_sample_number, guess_mode, allow_dups, record_run, run_fname,
                    target_wrd, starting_wrd, tot, vocab_standard_target_filename, dur_tw)


    sys.stdout.write('\n')


def magic_word_monkey(loc_wrd_x: int) -> None:
    """
    Intended to find only the first guess words that reduce the vocabulary selection,
    pool to the magic_order word count. Magic_order 1 means the target word only. Magic_order
    1 means the target word and one other word. And so on.
    @param loc_wrd_x:
    """
    global dur_tw, guess_mode, allow_dups, rank_mode, rand_mode, run_type, query_set, \
        query_mode, target_wrd, magic_order, run_fname

    if record_run:
        print('Output being written to ' + run_fname)
    print(f'{loc_wrd_x}  Finding #{magic_order} order magic words for: {target_wrd}')

    guess_vocabulary = vocab_magic_guess_filename
    # Need to iterate through all unranked words in the specified vocabulary
    candidate_list = helpers.ToolResults(data_path, guess_vocabulary, letter_rank_file, True, 0, True) \
        .get_ranked_grep_result_wrd_lst(True)
    r = 0
    mw_qty = 0
    rand_mode = True
    guess_mode = 'iterate guesses'
    allow_dups = True
    query_mode = True
    query_set.clear()
    loc_n = len(candidate_list)

    mag_x_pos_dict = {}  # exclude position dictionary
    mag_r_pos_dict = {}  # require position dictionary
    mag_excl_l = []  # exclude letters list
    mag_requ_l = []  # require letters list
    mag_multi_code = ''  # multiple same letters accounting

    prelude_output(loc_wrd_x, guess_mode, allow_dups, record_run, run_fname, starting_wrd,
                   guess_vocabulary, do_every_wrd, vocab_magic_target_filename)
    # Iterate through each word in the candidates list
    start_mt = time.perf_counter()  # record monkey start time
    for loc_key in candidate_list:
        # initialize a fresh wordletool instance, loc_allow_dups must be true
        # wordletool = helpers.ToolResults(data_path, solutions_vocab_filename, letter_rank_file, True, 0)
        wordletool = helpers.ToolResults(data_path, vocab_magic_target_filename, letter_rank_file, True, 0, True)
        guesses = 1
        run_stats = list([])
        run_stats.append(target_wrd)
        # For some reason, mag_excl_l, mag_requ_l, mag_x_pos_dict, mag_r_pos_dict, are maintained outside
        # of ToolResults. So they must be cleared
        clean_slate(mag_excl_l, mag_requ_l, mag_x_pos_dict, mag_r_pos_dict)
        mag_multi_code.replace(mag_multi_code,'')

        # This loop ends when the last guess results in only one remaining word that fits the
        # pattern. That word, being the target word, will be the solving guess. The loop's last
        # guess is therefore the actual second to last guess, except when it happens by chance
        # to be the target word.
        word = loc_key
        run_stats.append(word)

        # At this point the guess word is selected.
        # Analyze this new word against the target word and update the filter criteria
        [mag_excl_l,
         mag_x_pos_dict,
         mag_r_pos_dict,
         mag_multi_code] = helpers.analyze_pick_to_solution(target_wrd,
                                                            word,
                                                            mag_excl_l,
                                                            mag_x_pos_dict,
                                                            mag_r_pos_dict)
        # Now load in the resulting filter criteria
        helpers.load_grep_arguments(wordletool, mag_excl_l, mag_requ_l, mag_x_pos_dict, mag_r_pos_dict, mag_multi_code)

        # Get the word list using the optional no_rank argument with loc_rand_mode
        # No ranking or sorting is needed when all guesses are random.
        loc_the_word_list = wordletool.get_word_list(guesses + 2, word, debug_mode, True)

        # Because the target word is known to exist in the overall pool then loc_the_word_list can
        # only be 1 when the filter criteria filters to only the target.

        run_stats.append(len(loc_the_word_list))

        if len(loc_the_word_list) == magic_order:
            # Word is the target or is a magic word.
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
        msg = f'\033[K> {r} Searching {loc_n} words in {vocab_magic_guess_filename} for {target_wrd} magic word ...  ' \
              f'finding: {mw_qty}\r '
        sys.stdout.write(msg)
        sys.stdout.flush()

    dur_tw = time.perf_counter() - start_mt  # this word's process time
    prologue_output(loc_wrd_x, guess_mode, allow_dups, record_run, run_fname,
                    target_wrd, starting_wrd, mw_qty, vocab_magic_target_filename, dur_tw)

    sys.stdout.write('\n')


# ==== setup ======= These variables can be overriden by command line argument. ================

# The number of times to run guessing sessions
sample_number: int = 100
debug_mode = False  # prints out lists, guesses etc.
reveal_mode = False  # reveals each solution run data
data_path = 'worddata/'  # path from what will be helpers.py folder to data folder
# letter_rank_file = 'letter_ranks.txt'
letter_rank_file = 'letter_ranks_bot.txt'
botadd_sol_filename = 'botadd_nyt_wordlist.txt'  # classic+ solutions vocabulary list only
# solutions_vocab_filename = 'botadd_nyt_wordlist.txt'  # classic+ solutions vocabulary list only
# vocab_pos_sol_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# solutions_vocab_filename = 'wo_nyt_wordlist.txt'  # solutions vocabulary list only
# loc_vocab_filename = 'nyt_wordlist.txt'     # total vocabulary list
vocab_full_filename = 'nyt_wordlist.txt'     # total vocabulary list
vocab_standard_target_filename = ''
vocab_standard_guess_filename = ''
vocab_magic_target_filename = ''
vocab_magic_guess_filename = ''

x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
excl_l = []  # exclude letters list
requ_l = []  # require letters list
multi_code = ''  # multiple same letters accounting
# rank mode:
# -1 = Random
# 0 = Occurrence
# 1 = Position
# 2 = Both
rank_mode = -1
# monkey type
rand_mode = True  # random monkeys
# loc_rand_mode = False  # smart monkeys
# Set loc_allow_dups to prevent letters from occurring more than once.
# This condition is used mainly for the first two guesses. Duplicate
# letter words are allowed after the second guess and due to the code
# is required to be able to correctly handle target words that have
# duplicate letters.
allow_dups = False
target_wrd = '' # the target solution word
guess_mode = '' # general guess mode description
starting_wrd = '' # a required first guess if any
use_starting_wrd = -1
run_type = -1 # seems to be a flag indicating pick strategy random or method or yet to be defined
first_run = True
run_fname = '' # filename when saving run data
do_every_wrd = False  # Process every vocabulary word as a target word.
conditions = ''
dur_tw = 0.0  # seconds to process word
dur_sf = 0.0  # seconds so far in list process
query_set = set()
query_guess = 1
query_mode = False
magic_order = 1
magic_mode = False
resume = False
resume_after_wrd = ''
ts_pmo = ''  # magic order timestamp element
ts_pqm = ''  # query guess timestamp element
ts_prt = ''  # rank type timestamp element
ts_psn = ''  # sample number timestamp element
ts_ptw = ''  # target word timestamp element
ts_psw = ''  # starting word timestamp element
ts_ppw = ''  # resume after word timestamp element
# Records output to a CSV file (run_fname) having a timestamp like filename
record_run = False


# ====================================== main ================================================
def main(_args=None):
    global run_fname, resume, dur_sf, target_wrd
    try:
        # These command line arguments processed next will override all previously set variables.
        process_any_arguments()
        if not magic_mode:
            # Confirm the target Wordle word the guessing sessions are trying to discover. Note: The monkey can
            # be started with the target word already set.
            ask_for_target_word()            # Set the first guess if desired.
            ask_for_starting_guess()
            # Set the guess mode and rank mode.
            ask_for_guess_mode()
        else:
            # Confirm the target Wordle word the guessing sessions are trying to discover. Note: The monkey can
            # be started with the target word already set.
            ask_for_target_word()
        confirm_resume_after_wrd()
        set_late_timestamp_elements()
        # Timestamp like filename used for loc_record_run
        run_fname = fmwm_fname()
        wrd_x = 1
        if do_every_wrd:
            # The targets are the words for which the monkey seeks guesses to solve.
            # By default, only the words that can be a solution will be considered a target word.
            # The -z sets the target pool to be all the allowed Wordle guess words.
            # The target pool is not the guess pool.
            # By default, only the words that can be a solution will be considered a guess word.
            # The -v argument sets the guess pool to be all the allowed Wordle guess words.
            vocab_target_filename = vocab_standard_target_filename
            targets = helpers.ToolResults(data_path, vocab_target_filename, letter_rank_file, True, 0, True) \
                .get_ranked_grep_result_wrd_lst(True)
            n = len(targets)
            dsf = datetime.timedelta(0)
            avg_t = 0
            skip_qty = 0
            for key in targets:
                target_wrd = key
                # Resume allows for resuming from after a target_wrd being the resume_after_wrd
                if not resume:
                    # Run the monkey. The monkey will notice this loc_target_wrd
                    if not magic_mode:
                        standard_monkey(sample_number, wrd_x)
                    else:
                        magic_word_monkey(wrd_x)
                    # dur_tw is measured by the monkey
                    dur_sf = dur_sf + dur_tw
                    avg_t = dur_sf / (wrd_x - skip_qty)
                    etf = datetime.timedelta(seconds=((n - wrd_x) * dur_tw))
                    dsf = datetime.timedelta(seconds=dur_sf)
                    wrd_x += 1
                    # Do targets remain?
                    if wrd_x < len(targets):
                        print(
                            f'Duration so far: {dsf}, avg. {avg_t:0.4f} s/wrd, last word {dur_tw:0.4f}'
                            f' s/wrd, ETF: {etf}')
                else:
                    if target_wrd == resume_after_wrd:
                        print(f'Seen {resume_after_wrd}, will start on the next word.')
                        resume = False
                    else:
                        sys.stdout.write(f'\033[KSkipping {target_wrd}, waiting for {resume_after_wrd}\r')
                    wrd_x += 1
                    skip_qty += 1
            # Finished all targets
            print(f'Process done. Duration: {dsf}, {avg_t:0.4f} seconds/word')
        else:
            # Not doing every word
            if not magic_mode:
                standard_monkey(sample_number, wrd_x)
            elif magic_mode:
                magic_word_monkey(wrd_x)

    except KeyboardInterrupt:
        sys.stdout.write(f'\033[K user canceled. \n')
        # Output any encountered query results.
        query_output(target_wrd)


# ====================================== main ================================================
if __name__ == "__main__":
    main()
