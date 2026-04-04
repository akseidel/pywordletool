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
import sys
import datetime
import time
import helpers
import random
import argparse
import csv
import os
from dataclasses import dataclass, field
from enum import IntEnum

MAX_SAMPLES = 1_000_000


class RankMode(IntEnum):
    """Guess-ranking strategy. Values map directly to helpers.ToolResults rank_mode."""
    RANDOM = -1
    OCCURRENCE = 0
    POSITION = 1
    BOTH = 2
    ENTROPY = 3


@dataclass
class Config:
    """All mutable program state in one place, eliminating bare globals."""

    # ── sample settings ───────────────────────────────────────────────────────
    sample_number: int = 100
    debug_mode: bool = False
    reveal_mode: bool = False
    record_run: bool = False

    # ── vocabulary files ──────────────────────────────────────────────────────
    data_path: str = 'worddata/'
    letter_rank_file: str = 'letter_ranks_bot.txt'
    botadd_sol_filename: str = 'botadd_nyt_wordlist.txt'
    vocab_full_filename: str = 'nyt_wordlist.txt'
    vocab_standard_target_filename: str = ''
    vocab_standard_guess_filename: str = ''
    vocab_magic_target_filename: str = ''
    vocab_magic_guess_filename: str = ''

    # ── guess strategy ────────────────────────────────────────────────────────
    rank_mode: RankMode = RankMode.RANDOM
    rand_mode: bool = True
    run_type: int = -1  # -1 = unset, 0 = random, 1 = ranked
    allow_dups: bool = False
    guess_mode: str = ''

    # ── words ─────────────────────────────────────────────────────────────────
    target_wrd: str = ''
    starting_wrd: str = ''
    use_starting_wrd: int = -1  # -1 = unset, 0 = no fixed start, 1 = given

    # ── run state ─────────────────────────────────────────────────────────────
    first_run: bool = True
    run_fname: str = ''
    do_every_wrd: bool = False
    conditions: str = ''
    dur_tw: float = 0.0
    dur_sf: float = 0.0

    # ── query / magic mode ────────────────────────────────────────────────────
    query_set: set = field(default_factory=set)
    query_guess: int = 1
    query_mode: bool = False
    magic_order: int = 1
    magic_mode: bool = False

    # ── resume ────────────────────────────────────────────────────────────────
    resume: bool = False
    resume_after_wrd: str = ''

    # ── timestamp filename fragments ──────────────────────────────────────────
    ts_pmo: str = ''  # magic order
    ts_pqm: str = ''  # query guess
    ts_prt: str = ''  # rank type
    ts_psn: str = ''  # sample number
    ts_ptw: str = ''  # target word
    ts_psw: str = ''  # starting word
    ts_ppw: str = ''  # resume-after word


cfg = Config()


# ── argparse helper ───────────────────────────────────────────────────────────

class BlankLinesHelpFormatter(argparse.HelpFormatter):
    """Adds a blank line after each argument's help text."""

    def _split_lines(self, text: str, width: int) -> list[str]:
        return super()._split_lines(text, width) + ['']


# ── word-list helpers ─────────────────────────────────────────────────────────

def _tool_results(vocab_filename: str) -> helpers.ToolResults:
    """Convenience constructor for an unranked helpers.ToolResults using cfg paths."""
    return helpers.ToolResults(
        cfg.data_path, vocab_filename, cfg.letter_rank_file, True, 0, True
    )


def unranked_large_word_dict() -> dict:
    """Return an unranked word dict built from the full (non-solution-only) vocabulary."""
    return _tool_results(cfg.vocab_full_filename).get_ranked_grep_result_wrd_lst(True)


# ── filter helpers ────────────────────────────────────────────────────────────

def clean_slate(excl_l: list, requ_l: list, x_pos_dict: dict, r_pos_dict: dict) -> None:
    """Clear all letter-filtering containers in place."""
    excl_l.clear()
    requ_l.clear()
    x_pos_dict.clear()
    r_pos_dict.clear()


# ── guess-mode helpers ────────────────────────────────────────────────────────

def _apply_guess_mode_settings() -> None:
    """Set cfg.guess_mode and cfg.allow_dups from the current rand_mode / rank_mode."""
    if cfg.rand_mode:
        cfg.guess_mode = 'random guesses'
        cfg.allow_dups = True
    else:
        cfg.guess_mode = f'rank mode type {cfg.rank_mode + 1} guesses'
        # Entropy mode selects randomly among equal-entropy words, so dups must be allowed.
        # For occurrence/position/both modes the allow_dups flag is left at its current value
        # so its influence on the first two guesses can be observed.
        if cfg.rank_mode == RankMode.ENTROPY:
            cfg.allow_dups = True


def _set_rank_mode_from_cli(r: int) -> None:
    """Translate the CLI -r value (0–4) into cfg.rand_mode / cfg.rank_mode / cfg.run_type."""
    if r == 0:
        cfg.rand_mode = True
        cfg.run_type = 0
        cfg.rank_mode = RankMode.RANDOM
    else:
        cfg.rand_mode = False
        cfg.run_type = 1
        cfg.rank_mode = RankMode(r - 1)  # CLI is 1-indexed; RankMode is 0-indexed


# ── timestamp / filename helpers ──────────────────────────────────────────────

def set_late_timestamp_elements() -> None:
    """
    Refresh filename-prefix fragments that depend on parameters set after the
    argument parser runs (e.g. after interactive prompts).
    """
    if cfg.target_wrd:
        cfg.ts_ptw = f'T_{cfg.target_wrd}_'
    if cfg.starting_wrd:
        cfg.ts_psw = f'S_{cfg.starting_wrd}_'
    if cfg.resume_after_wrd:
        cfg.ts_ppw = f'P_{cfg.resume_after_wrd}_'
    cfg.ts_prt = f'R{cfg.rank_mode + 1}_'


def fmwm_fname() -> str:
    """Return a timestamp-based CSV filename annotated with key run parameters."""
    ts = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')
    # Magic-mode runs omit the sample-number fragment since it isn't meaningful there.
    sample_fragment = '' if cfg.ts_pmo else cfg.ts_psn
    return f'{cfg.ts_pmo}{cfg.ts_prt}{cfg.ts_pqm}{sample_fragment}{cfg.ts_ptw}{cfg.ts_psw}{cfg.ts_ppw}{ts}.csv'


# ── terminal helper ───────────────────────────────────────────────────────────

def _maybe_widen_terminal(required_width: int) -> None:
    """Attempt to widen the terminal if the message would exceed its current width."""
    try:
        size = os.get_terminal_size()
        if required_width > size.columns:
            os.system(f"printf '\\033[8;{size.lines};{required_width}t'")
    except OSError:
        pass


# ── argument processing ───────────────────────────────────────────────────────

def process_any_arguments(args_override: list[str] | None = None) -> None:
    """Parse command-line arguments and update cfg accordingly."""

    parser = argparse.ArgumentParser(
        description='Process command line settings.',
        formatter_class=BlankLinesHelpFormatter,
    )

    parser.add_argument('-d', action='store_true', help='Prints out lists, guesses etc.')
    parser.add_argument('-l', action='store_true', help='Lists each solution run data.')
    parser.add_argument('-n', action='store_true', help='Random first guess word, i.e. skip asking about it.')
    parser.add_argument('-t', action='store', help='Use this target word T.')
    parser.add_argument('-s', action='store', help='Use this first guess word S.')
    parser.add_argument(
        '-r', action='store', type=int, choices=range(0, 5),
        help='Guess type: Random(0), Rank Occurrence(1), Rank Position(2), Both(3), or Entropy(4).',
    )
    parser.add_argument('-x', action='store', type=int,
                        help=f'Override the number of sampling runs to X (max {MAX_SAMPLES:,}).')
    parser.add_argument('-v', action='store_true',
                        help='For guessing, use the full Wordle vocabulary including non-solution words.')
    parser.add_argument('-z', action='store_true',
                        help='For word targets, use the full Wordle vocabulary including non-solution words.')
    parser.add_argument('-w', action='store_true',
                        help='Write output to a CSV file with a timestamp filename.')
    parser.add_argument('-a', action='store_true',
                        help='Process every vocabulary word as a target word.')
    parser.add_argument('-q', action='store', type=int,
                        help='Show guesses that solve on the Qth guess.')
    parser.add_argument('-m', action='store', type=int,
                        help='Find order-M magic words for a target word.')
    parser.add_argument('-p', action='store', help='Pick-up (restart) after seeing word P.')

    # With args_override, a test can call main(['--target', 'crane', '--samples', '10'])
    # and have those arguments take effect instead of whatever is in sys.argv.
    args = parser.parse_args(args_override)  # None means "read sys.argv", a list means "use this"

    cfg.debug_mode = args.d
    cfg.reveal_mode = args.l
    cfg.magic_mode = args.m is not None
    cfg.do_every_wrd = args.a
    cfg.record_run = args.w

    if args.m is not None:
        cfg.magic_order = args.m
        m_max = len(unranked_large_word_dict()) - 1
        if cfg.magic_order < 1:
            print(f'Aborting. The -m argument must be > 0 (got {cfg.magic_order}).')
            sys.exit(1)
        if cfg.magic_order > m_max:
            print(f'Aborting. The -m argument must be < {m_max} (got {cfg.magic_order}).')
            sys.exit(1)
        cfg.ts_pmo = f'M{cfg.magic_order:03.0f}_'

    if args.q is not None:
        cfg.query_guess = args.q
        if cfg.query_guess < 1:
            print(f'Aborting. The -q argument must be > 0 (got {cfg.query_guess}).')
            sys.exit(1)
        cfg.reveal_mode = True
        cfg.query_mode = True
        cfg.ts_pqm = f'Q{cfg.query_guess}_'

    cfg.vocab_standard_guess_filename = cfg.vocab_full_filename if args.v else cfg.botadd_sol_filename
    cfg.vocab_magic_guess_filename = cfg.vocab_full_filename if args.v else cfg.botadd_sol_filename
    cfg.vocab_standard_target_filename = cfg.vocab_full_filename if args.z else cfg.botadd_sol_filename
    cfg.vocab_magic_target_filename = cfg.vocab_full_filename if args.z else cfg.botadd_sol_filename

    if args.n:
        cfg.use_starting_wrd = 0

    if args.t is not None:
        cfg.target_wrd = args.t
        cfg.ts_ptw = f'T_{cfg.target_wrd}_'

    if args.s is not None:
        cfg.use_starting_wrd = 1
        cfg.starting_wrd = args.s
        cfg.ts_psw = f'S_{cfg.starting_wrd}_'

    if args.p is not None:
        cfg.resume = True
        cfg.resume_after_wrd = args.p
        cfg.ts_ppw = f'P_{cfg.resume_after_wrd}_'

    if args.r is not None:
        _set_rank_mode_from_cli(args.r)
        _apply_guess_mode_settings()

    cfg.ts_prt = f'R{cfg.rank_mode + 1}_'

    if args.x is not None:
        if args.x < 1:
            cfg.sample_number = 1
            print(f'===> Negative value not allowed. Runs number set to {cfg.sample_number}.')
        elif args.x > MAX_SAMPLES:
            cfg.sample_number = MAX_SAMPLES
            print(f'===> {MAX_SAMPLES:,} is the maximum. Runs number set to {cfg.sample_number:,}.')
            print('===> Control + C will stop the program.')
        else:
            cfg.sample_number = args.x

    cfg.ts_psn = f'X{cfg.sample_number}_'


# ── interactive prompts ───────────────────────────────────────────────────────

def confirm_resume_after_wrd() -> None:
    """Validate cfg.resume_after_wrd exists in the full vocabulary; prompt until it does."""
    if not cfg.resume:
        return
    while cfg.resume_after_wrd not in unranked_large_word_dict():
        cfg.resume_after_wrd = input('Enter a valid Wordle word to resume after: ').lower()


def ask_for_target_word() -> None:
    """Ensure cfg.target_wrd is a valid word in the full vocabulary; prompt until it is."""
    if cfg.do_every_wrd:
        return
    while cfg.target_wrd not in unranked_large_word_dict():
        cfg.target_wrd = input('Enter a valid Wordle target word: ').lower()


def ask_for_starting_guess() -> None:
    """Interactively decide whether to use a fixed first-guess word."""
    while cfg.use_starting_wrd == -1:
        response = input('Run using a given first guess? Enter y/n: ').lower()
        if response == 'y':
            while cfg.starting_wrd not in unranked_large_word_dict():
                cfg.starting_wrd = input('Enter a valid Wordle first guess word: ').lower()
            cfg.use_starting_wrd = 1
        elif response == 'n':
            cfg.use_starting_wrd = 0


def ask_for_guess_mode() -> None:
    """Interactively set the guess strategy, then apply the resulting settings."""
    if cfg.run_type != -1:
        return
    prompt = (
        'Guess Type? Random(0), Rank by Occurrence(1), Position(2), '
        'Both(3), Best Entropy(4) — enter 0–4: '
    )
    while cfg.run_type == -1:
        response = input(prompt)
        if response in {'0', '1', '2', '3', '4'}:
            _set_rank_mode_from_cli(int(response))
    _apply_guess_mode_settings()


# ── output ────────────────────────────────────────────────────────────────────

def output_msg(msg: str | list, also_to_file: bool, loc_fname: str) -> None:
    """Write msg to stdout, or append it to a CSV file when also_to_file is True."""
    if also_to_file:
        try:
            with open(loc_fname, 'a') as f:
                if isinstance(msg, list):
                    csv.writer(f).writerow([str(w).replace("'", '') for w in msg])
                else:
                    f.write(str(msg) + '\n')
        except IOError:
            sys.stdout.write(f'\nIOError writing to {loc_fname}\n')
            sys.stdout.write(f'Tried to write: {msg}\n')
            sys.exit(1)
    else:
        sys.stdout.write('\033[K' + str(msg).replace("'", '') + '\n')


def prelude_output(loc_sample_number: int,
                   loc_vocab_filename: str,
                   loc_sol_filename: str | None = None) -> None:
    """Print/record the conditions for the upcoming sample run."""
    if not cfg.magic_mode:
        cfg.conditions = (
            f'{cfg.sample_number} samples, {cfg.guess_mode}, '
            f'initial duplicates:{cfg.allow_dups}'
        )
        if len(cfg.starting_wrd) == 5:
            cfg.conditions += f', first guess:{cfg.starting_wrd}'
        output_msg(
            f'target wrd: {cfg.target_wrd}, {cfg.conditions}, {loc_vocab_filename}',
            False, cfg.run_fname,
        )
        if cfg.record_run:
            if not cfg.do_every_wrd:
                output_msg(
                    ['target wrd', 'samples', 'guess mode', 'initial duplicates',
                     'first guess', 'vocabulary'],
                    cfg.record_run, cfg.run_fname,
                )
                output_msg(
                    [cfg.target_wrd, loc_sample_number, cfg.guess_mode,
                     str(cfg.allow_dups), cfg.starting_wrd, loc_vocab_filename],
                    cfg.record_run, cfg.run_fname,
                )
            if cfg.reveal_mode:
                reveal_hdr = ['Run', 'guesses', 'target wrd',
                              'G1', 'G1R', 'G2', 'G2R', 'G3', 'G3R', 'G4', 'G4R', 'G5', 'G5R',
                              'G6', 'G6R', 'G7', 'G7R', 'G8', 'G8R', 'G9', 'G9R', 'G10', 'G10R']
                output_msg(reveal_hdr, cfg.record_run, cfg.run_fname)
    else:
        output_msg(
            f'Order {cfg.magic_order} magic words for: {cfg.target_wrd}.\n'
            f'Guesses from {loc_vocab_filename}, solutions from {loc_sol_filename}.',
            False, cfg.run_fname,
        )
        if cfg.record_run:
            if cfg.first_run:
                output_msg(
                    f'Order {cfg.magic_order} magic words from {loc_vocab_filename}',
                    cfg.record_run, cfg.run_fname,
                )
            if cfg.reveal_mode:
                output_msg(
                    ['Index', 'Guesses', 'Target Wrd', 'Magic Wrd', 'G1R'],
                    cfg.record_run, cfg.run_fname,
                )


def reveal_output(x: int, guesses: int, run_stats: list,
                  run_word_dict: dict | None = None) -> None:
    """Output the result row for sample run x."""
    reveal_stat = [x, guesses, *run_stats]
    if run_word_dict:
        reveal_stat.append(list(run_word_dict.keys()))
    output_msg(reveal_stat, False, cfg.run_fname)
    if cfg.record_run:
        output_msg(reveal_stat, cfg.record_run, cfg.run_fname)


def epilogue_output(loc_sample_number: int,
                    tot: int, loc_vocab_filename: str) -> None:
    """Print/record the summary results of a completed sample run."""
    if not cfg.magic_mode:
        average = tot / loc_sample_number
        stat_msg = (
            f'target wrd: {cfg.target_wrd}, averaged {average:.3f} guesses to solve, '
            f'{cfg.conditions}, {loc_vocab_filename}, {cfg.dur_tw:0.4f} seconds'
        )
        output_msg(stat_msg, False, cfg.run_fname)

        if cfg.record_run:
            if not cfg.do_every_wrd or cfg.first_run:
                output_msg(
                    ['target wrd', 'average', 'guess mode', 'initial duplicates',
                     'first guess', 'vocabulary', 'samples', 'seconds'],
                    cfg.record_run, cfg.run_fname,
                )
            output_msg(
                [cfg.target_wrd, average, cfg.guess_mode, str(cfg.allow_dups),
                 cfg.starting_wrd, loc_vocab_filename, loc_sample_number, cfg.dur_tw],
                cfg.record_run, cfg.run_fname,
            )
    else:
        if cfg.record_run:
            if not cfg.do_every_wrd or cfg.first_run:
                output_msg(['Target', 'Qty', 'Sec', 'Magic Wrds =>'],
                           cfg.record_run, cfg.run_fname)
            query_list = sorted(cfg.query_set)
            output_msg(
                [cfg.target_wrd, len(cfg.query_set), f'{cfg.dur_tw:0.4f}', *query_list],
                cfg.record_run, cfg.run_fname,
            )

    cfg.first_run = False
    if cfg.query_mode:
        query_output(cfg.target_wrd)


def query_output(loc_target_wrd: str) -> None:
    """Print the query-mode word-set summary to the console."""
    query_list = sorted(cfg.query_set)
    if not cfg.magic_mode:
        stat_msg = (
            f'Encountered {len(cfg.query_set)} #{cfg.query_guess - 1} guesses '
            f'that eliminate all but the solution {loc_target_wrd} guess:\n{query_list}'
        )
    else:
        stat_msg = (
            f'Encountered {len(cfg.query_set)} order #{cfg.magic_order} magic word guesses '
            f'that eliminate all but {cfg.magic_order} guesses:\n{query_list}'
        )
    clean_msg = stat_msg.replace("'", '')
    sys.stdout.write(f'\033[K{clean_msg}\n')


# ── monkey runners ────────────────────────────────────────────────────────────

def standard_monkey(loc_sample_number: int, loc_wrd_x: int) -> None:
    """Run the standard sampling monkey for cfg.target_wrd."""
    if cfg.record_run:
        print('Output being written to ' + cfg.run_fname)

    base_str = f'{loc_wrd_x} word: {cfg.target_wrd}'
    if cfg.use_starting_wrd == 1 and cfg.rank_mode not in (RankMode.ENTROPY, RankMode.RANDOM):
        print(f'{base_str}  Only one sample needed for guess type {cfg.rank_mode + 1} '
              f'when a starting word is specified.')
    else:
        print(f'{base_str}  Average guesses to solve Wordle by sampling {loc_sample_number} tries.')
        if cfg.rank_mode == RankMode.ENTROPY:
            print('-- Processing time varies exponentially with the starting-word result size!')

    std_x_pos_dict: dict = {}
    std_r_pos_dict: dict = {}
    std_excl_l: list = []
    std_requ_l: list = []
    std_multi_dict: dict = {}

    # All samples are identical when there is a fixed starting word and a non-entropy ranked
    # strategy, so only one sample is needed.
    if cfg.rank_mode != RankMode.ENTROPY and cfg.use_starting_wrd == 1 and not cfg.rand_mode:
        loc_sample_number = 1

    tot: int = 0
    guess_word: str = ''

    prelude_output(loc_sample_number,
                   cfg.vocab_standard_target_filename)
    start_mt = time.perf_counter()

    if cfg.debug_mode:
        print(f'Running the standard monkey {loc_sample_number} times.')

    for x in range(loc_sample_number):
        targets_wordletool = helpers.ToolResults(
            cfg.data_path, cfg.vocab_standard_target_filename, cfg.letter_rank_file,
            cfg.allow_dups, cfg.rank_mode, True,
        )

        guesses = 0
        run_stats: list = [cfg.target_wrd]

        clean_slate(std_excl_l, std_requ_l, std_x_pos_dict, std_r_pos_dict)
        std_multi_dict.clear()

        loc_targets_word_list_dict = targets_wordletool.get_word_list(
            guesses + 1, '', cfg.debug_mode, cfg.rand_mode)

        # For entropy mode a static guess pool is computed once and reused every round.
        special_guess_list: list = []
        if cfg.rank_mode == RankMode.ENTROPY:
            guess_pool_wordletool = helpers.ToolResults(
                cfg.data_path, cfg.vocab_standard_guess_filename, cfg.letter_rank_file,
                cfg.allow_dups, cfg.rank_mode, True,
            )
            special_guess_list = list(
                guess_pool_wordletool.get_word_list(
                    guesses + 1, '', cfg.debug_mode, cfg.rand_mode).keys()
            )

        # Loop ends when only one candidate remains (the target word itself).
        while len(loc_targets_word_list_dict) > 1:
            if guesses == 0 and cfg.use_starting_wrd == 1:
                guess_word = cfg.starting_wrd
            else:
                # The dwindling targets pool doubles as the guess pool.
                guess_pool_tuples = list(loc_targets_word_list_dict.items())

                if cfg.rand_mode:
                    guess_word, _ = random.choice(guess_pool_tuples)
                elif cfg.rank_mode != RankMode.ENTROPY:
                    # First pick is random; all subsequent picks take the top-ranked word.
                    if guesses == 0:
                        guess_word, _ = random.choice(guess_pool_tuples)
                    else:
                        guess_word, _ = guess_pool_tuples[-1]
                else:
                    best_ent_words = list(
                        helpers.best_entropy_outcomes_guess_dict(
                            loc_targets_word_list_dict, special_guess_list, cfg.debug_mode)
                    )
                    # Multiple words can share the highest entropy; choose randomly.
                    guess_word = random.choice(best_ent_words)
                    if cfg.debug_mode:
                        print(f'- Selected {guess_word} for the next round.')

            run_stats.append(guess_word)

            [std_excl_l,
             std_x_pos_dict,
             std_r_pos_dict,
             std_multi_dict] = helpers.analyze_pick_to_solution(
                cfg.target_wrd, guess_word,
                std_excl_l, std_x_pos_dict, std_r_pos_dict,
            )

            # From the second guess onward, re-create the wordletool allowing duplicates.
            if (guesses > 0 and not cfg.allow_dups) or cfg.rank_mode == RankMode.ENTROPY:
                del targets_wordletool
                targets_wordletool = helpers.ToolResults(
                    cfg.data_path, cfg.vocab_standard_target_filename, cfg.letter_rank_file,
                    True, cfg.rank_mode, True,
                )
                cfg.allow_dups = True

            helpers.load_grep_arguments(
                targets_wordletool,
                std_excl_l, std_requ_l, std_x_pos_dict, std_r_pos_dict, std_multi_dict,
            )

            loc_targets_word_list_dict = targets_wordletool.get_word_list(
                guesses + 2, guess_word, cfg.debug_mode, cfg.rand_mode)

            # Target words with duplicate letters can fall out of a no-dups pool.
            # Recover by rebuilding the wordletool with dups allowed.
            if len(loc_targets_word_list_dict) < 1:
                del targets_wordletool
                targets_wordletool = helpers.ToolResults(
                    cfg.data_path, cfg.vocab_standard_target_filename, cfg.letter_rank_file,
                    True, cfg.rank_mode, True,
                )
                helpers.load_grep_arguments(
                    targets_wordletool,
                    std_excl_l, std_requ_l, std_x_pos_dict, std_r_pos_dict, std_multi_dict,
                )
                loc_targets_word_list_dict = targets_wordletool.get_word_list(
                    guesses + 2, guess_word, cfg.debug_mode, cfg.rand_mode)

            run_stats.append(len(loc_targets_word_list_dict))
            guesses += 1

        # The final guess is the word that was left in the pool, except when the loop's
        # last guess happened to land on the target itself.
        if guess_word != cfg.target_wrd:
            guesses += 1
            run_stats.append(cfg.target_wrd)

        tot += guesses
        r = x + 1

        if cfg.reveal_mode:
            if not cfg.query_mode:
                reveal_output(r, guesses, run_stats)
            elif guesses == cfg.query_guess and run_stats[(cfg.query_guess - 1) * 2] == 1:
                reveal_output(r, guesses, run_stats)
                cfg.query_set.add(run_stats[(cfg.query_guess - 1) * 2 - 1])

        del targets_wordletool
        sys.stdout.write(f'\033[K>{r}  avg: {tot / r:.2f}\r')

    cfg.dur_tw = time.perf_counter() - start_mt
    epilogue_output(loc_sample_number,
                    tot, cfg.vocab_standard_target_filename)
    sys.stdout.write('\n')


def magic_word_monkey(loc_wrd_x: int, target_qty: int) -> None:
    """
    Find all single-guess words that reduce the target vocabulary to exactly
    cfg.magic_order candidates. Order 1 means only the target word remains;
    order 2 means the target plus one other word, and so on.
    """
    if cfg.record_run:
        print('Output being written to ' + cfg.run_fname)
    print(f'\nTarget {loc_wrd_x} of {target_qty}  '
          f'Finding #{cfg.magic_order} order magic words for: {cfg.target_wrd}')

    guess_vocabulary = cfg.vocab_magic_guess_filename
    candidate_list = _tool_results(guess_vocabulary).get_ranked_grep_result_wrd_lst(True)

    cfg.rand_mode = True
    cfg.guess_mode = 'iterate guesses'
    cfg.allow_dups = True
    cfg.query_mode = True
    cfg.query_set.clear()

    loc_n = len(candidate_list)
    mw_qty = 0
    mag_x_pos_dict: dict = {}
    mag_r_pos_dict: dict = {}
    mag_excl_l: list = []
    mag_requ_l: list = []
    mag_multi_code: dict = {}

    prelude_output(loc_wrd_x,
                   guess_vocabulary, cfg.vocab_magic_target_filename)
    start_mt = time.perf_counter()

    for r, loc_key in enumerate(candidate_list, start=1):
        wordletool = helpers.ToolResults(
            cfg.data_path, cfg.vocab_magic_target_filename, cfg.letter_rank_file,
            True, 0, True,
        )
        guesses = 1
        run_stats: list = [cfg.target_wrd, loc_key]

        clean_slate(mag_excl_l, mag_requ_l, mag_x_pos_dict, mag_r_pos_dict)
        mag_multi_code.clear()

        [mag_excl_l,
         mag_x_pos_dict,
         mag_r_pos_dict,
         mag_multi_code] = helpers.analyze_pick_to_solution(
            cfg.target_wrd, loc_key,
            mag_excl_l, mag_x_pos_dict, mag_r_pos_dict,
        )
        helpers.load_grep_arguments(
            wordletool, mag_excl_l, mag_requ_l,
            mag_x_pos_dict, mag_r_pos_dict, mag_multi_code,
        )
        loc_the_word_list = wordletool.get_word_list(guesses + 2, loc_key, cfg.debug_mode, True)
        pool_size = len(loc_the_word_list)
        run_stats.append(pool_size)

        if pool_size == cfg.magic_order:
            if loc_key != cfg.target_wrd:
                guesses += 1
            # Only first-guess words that achieve the target pool size are of interest.
            if guesses == 2 and run_stats[2] == cfg.magic_order:
                cfg.query_set.add(run_stats[1])
                if cfg.reveal_mode:
                    reveal_output(r, guesses, run_stats, loc_the_word_list)

        del wordletool

        mw_qty = len(cfg.query_set)
        msg = (f'\033[K=> {r} scanning {loc_n} wrds in {cfg.vocab_magic_guess_filename}'
               f' for order {cfg.magic_order} magic wrds. Found: {mw_qty}\r')
        _maybe_widen_terminal(len(msg))
        sys.stdout.write(msg)
        sys.stdout.flush()

    cfg.dur_tw = time.perf_counter() - start_mt
    epilogue_output(loc_wrd_x,
                    mw_qty, cfg.vocab_magic_target_filename)
    sys.stdout.write(f"\n{cfg.target_wrd}'s duration: {cfg.dur_tw:0.4f} sec.\n\n")


# ── main ──────────────────────────────────────────────────────────────────────

def main(_args: list[str] | None = None) -> None:
    try:
        process_any_arguments(_args)

        if not cfg.magic_mode:
            ask_for_target_word()
            ask_for_starting_guess()
            ask_for_guess_mode()
        else:
            ask_for_target_word()

        confirm_resume_after_wrd()
        set_late_timestamp_elements()
        cfg.run_fname = fmwm_fname()

        wrd_x = 1

        if cfg.do_every_wrd:
            targets = _tool_results(cfg.vocab_standard_target_filename).get_ranked_grep_result_wrd_lst(True)
            n = len(targets)
            dsf = datetime.timedelta(0)
            avg_t = 0.0
            skip_qty = 0

            for key in targets:
                cfg.target_wrd = key

                if not cfg.resume:
                    if not cfg.magic_mode:
                        standard_monkey(cfg.sample_number, wrd_x)
                    else:
                        magic_word_monkey(wrd_x, n)

                    cfg.dur_sf += cfg.dur_tw
                    avg_t = cfg.dur_sf / (wrd_x - skip_qty)
                    etf = datetime.timedelta(seconds=(n - wrd_x) * cfg.dur_tw)
                    dsf = datetime.timedelta(seconds=cfg.dur_sf)
                    wrd_x += 1
                    if wrd_x <= n:
                        print(f'Elapsed: {dsf}, avg {avg_t:0.4f} s/wrd, '
                              f'last {cfg.dur_tw:0.4f} s/wrd, ETF: {etf}')
                else:
                    if cfg.target_wrd == cfg.resume_after_wrd:
                        print(f'Seen {cfg.resume_after_wrd}, will start on the next word.')
                        cfg.resume = False
                    else:
                        sys.stdout.write(
                            f'\033[KSkipping {cfg.target_wrd}, waiting for {cfg.resume_after_wrd}\r')
                    wrd_x += 1
                    skip_qty += 1

            print(f'Process done. Duration: {dsf}, {avg_t:0.4f} seconds/word')

        else:
            if not cfg.magic_mode:
                standard_monkey(cfg.sample_number, wrd_x)
            else:
                magic_word_monkey(wrd_x, 1)


    except KeyboardInterrupt:
        sys.stdout.write('\033[K user canceled.\n')
        if cfg.query_set:
            query_output(cfg.target_wrd)


if __name__ == '__main__':
    main()
