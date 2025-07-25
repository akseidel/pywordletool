# ----------------------------------------------------------------
# pywt.py  akseidel 5/2022
# ----------------------------------------------------------------
# This program was created without any prior python programing knowledge
# nor classical training in programming. It must be chock-full of coding
# misuse. Do not think for a moment the code is "proper". It is likely
# very good for showing how something should not be done or how what
# results from not understanding some concepts.
#
# For someone who is looking closely at this and wondering why its
# structure is a bit odd, this program started without a GUI interface
# so to get the basic engine working first. Then the GUI was created,
# discarding the original command line interface.
#
# Get customtkinter -> pip3 install customtkinter
# if already present, you may need to upgrade it -> pip3 install customtkinter --upgrade
# Hopefully the upgrade does not break this code.
#
import random
import tkinter as tk  # assigns tkinter stuff to tk namespace so that
# it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk
# namespace so that tk is preserved
from tkinter import messagebox
from tkinter.ttk import Style

import customtkinter as ctk

import helpers as hlp
import outcomedrilling

# globals
data_path = 'worddata/'  # path from here to data folder
# letter_rank_file = 'letter_ranks.txt'
letter_rank_file = 'letter_ranks_bot.txt'
full_wordle_wrd_list = 'nyt_wordlist.txt'
bot_pos_sol_wrd_list = 'botadd_nyt_wordlist.txt'
classic_pos_sol_wrd_list = 'wo_nyt_wordlist.txt'
pu_sol_wrd_list = 'pu_wordlist.txt'
help_showing = False  # flag indicating help window is open
x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
exclude = []  # exclude list used by monkey sampler
# font_tuple_n = ("Courier", 12, "normal")
font_tuple_n = ("Helvetica", 10, "normal")

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


# return a reformatted string with word wrapping
def wrap_this(string: str, max_chars: int) -> str:
    """A helper that will return the string with word-break wrapping.
    @param str string: The text to be wrapped.
    @param int max_chars: The maximum number of characters on a line before wrapping.
    """
    string = string.replace('\n', '').replace('\r', '')  # strip confusing newlines
    words = string.split(' ')
    the_lines = []
    the_line = ""
    for w in words:
        if len(the_line + ' ' + w) <= max_chars:
            the_line += ' ' + w
        else:
            the_lines.append(the_line)
            the_line = w
    if the_line:
        the_lines.append(the_line)
    the_lines[0] = the_lines[0][1:]
    the_newline = ""
    for w in the_lines:
        the_newline += '\n' + w
    return the_newline


# Remove certain characters from loc_str string argument.
def scrub_text(loc_str: str, l_add: str, no_numbers: bool, no_letters5: bool) -> str:
    """
    Remove certain characters from loc_str string argument.
    @loc_str: str - The string that will be scrubbed
    @l_add: str - A string of characters to include to default exclude characters.
    For example the default exclude characters omits '.'
    @no_numbers: bool - If true then also exclude numbers 0-9
    @no_letters5: bool - If true then exclude letters AND numbers 0,6-9
    @rtype: str
    """
    excludes = '\'\"!@#$%^&*(){}_+-=?\\|[]:;<>,/`~ '
    if no_numbers:
        excludes = excludes + '1234567890'
    if no_letters5:
        excludes = excludes + 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM67890'
    excludes = excludes + l_add
    for char in excludes:
        loc_str = loc_str.replace(char, '')
    return loc_str




class Pywordlemainwindow(ctk.CTk):
    """The pywordletool application GUI window
    """
    global x_pos_dict
    global r_pos_dict

    def set_n_col(self):
        sw = self.result_frame.winfo_width()
        if sw >= 1280:
            return 12
        elif sw >= 1174:
            return 11
        elif sw >= 1068:
            return 10
        elif sw >= 966:
            return 9
        else:
            return 8

    def show_help(self) -> None:
        if self.wnd_help is None or not self.wnd_help.winfo_exists():
            self.wnd_help = hlp.HelpWindow(data_path, letter_rank_file)  # create window if its None or destroyed
        else:
            self.wnd_help.deiconify()  # unhide possible hidden window
            self.wnd_help.focus()  # if window exists focus it

    # ======== set exclude cboxes to treeview selection
    def x_pos_tree_view_click(self, _event) -> None:
        cur_item = self.treeview_px.focus()
        val_tup = self.treeview_px.item(cur_item).get('values')
        if val_tup != '':
            self.pos_px_l.set(val_tup[0])
            self.pos_px_p.set(val_tup[1])

    # ======== set require cboxes to treeview selection
    def r_pos_tree_view_click(self, _event) -> None:
        cur_item = self.treeview_pr.focus()
        val_tup = self.treeview_pr.item(cur_item).get('values')
        if val_tup != '':
            self.pos_pr_l.set(val_tup[0])
            # Only the letter combobox is matched to the selection letter.

    def enable_optimal_controls(self, look: str) -> None:
        self.set_optimal_options_look(look)
        self.set_opt_vocab_ckb_look(look)

    def set_optimal_options_look(self, look: str) -> None:
        self.bt_groups.configure(state=look)
        self.chk_grp_disp.configure(state=look)
        self.chk_ent_disp.configure(state=look)
        self.chk_cond_disp.configure(state=look)
        self.chk_keyed_disp.configure(state=look)

    def set_opt_vocab_ckb_look(self, look: str) -> None:
        self.rbrA.configure(state=look)
        self.rbrB.configure(state=look)
        self.rbrBB.configure(state=look)
        self.rbrC.configure(state=look)

    def close_subs(self):
        for sub in self.winfo_children():
            if isinstance(sub, tk.Toplevel):
                sub.destroy()

    def __init__(self):
        super().__init__()
        self.wnd_help = None
        self.title("This Wordle Helper")

        self.option_add("*Font", font_tuple_n)

        # Screen height and width.
        w_width = 1150
        w_height = 726

        hlp.size_and_position_this_window(self, w_width, w_height, 0, 0)

        # set the Vars
        self.outcms_guess_source = tk.IntVar(value=0)
        self.allow_dup_state = tk.BooleanVar(value=False)
        self.use_classic_frequency = tk.BooleanVar(value=False)
        self.use_hard_mode = tk.BooleanVar(value=False)
        self.ordr_by_rank = tk.BooleanVar(value=True)
        self.verbose_outcms = tk.BooleanVar(value=False)
        self.ent_outcms = tk.BooleanVar(value=False)
        self.cond_outcms = tk.BooleanVar(value=False)
        self.keyed_verbose_outcms = tk.BooleanVar(value=False)
        self.vocab_var = tk.IntVar(value=1)
        self.cull_the_pu = tk.BooleanVar(value=False)
        self.status = tk.StringVar()
        self.rank_mode = tk.IntVar()
        self.rank_mode.set(0)
        self.suppress_grep = False
        self.pos5 = ['1', '2', '3', '4', '5']
        # pos_r to be a mutable list of unassigned letter positions
        self.pos_r = self.pos5.copy()
        self.pos_x = self.pos5.copy()
        self.sel_not_classic = False
        self.sel_rando = False
        self.sel_outcm_optimal = False
        self.sel_genetic = False
        self.outcms_driller_window = None
        self.meta_lr = False

        # configure style
        style = ttk.Style()
        # Sets the font used for label in labelframe
        style.configure('TLabelframe.Label', font=('helvetica', 10, 'normal'))
        style.theme_use()

        # Set meta left pressed flag used for clue type tally count
        # in condensed output.
        def key_handler_meta_lr(e):
            self.meta_lr = True

        self.bind('<Meta_L>', key_handler_meta_lr)
        self.bind('<Meta_R>', key_handler_meta_lr)

        def str_wrd_list_hrd() -> None:
            """Creates the word list header line.
            @param ln_col: number of columns in header
            @return: column header string
            """
            ln_col = self.set_n_col()
            h_txt = " Word : Rank "
            left_pad = ""
            mid_pad = "  "
            h_line = left_pad + h_txt
            for i in range(1, ln_col):
                h_line = h_line + mid_pad + h_txt
            lb_result_hd.configure(text=h_line)

        def show_outcome_driller() -> None:
            if self.outcms_driller_window is None or not self.outcms_driller_window.winfo_exists():
                self.outcms_driller_window = outcomedrilling.OutcmsDrillingMain()  # create window if its None or destroyed
            else:
                self.outcms_driller_window.focus()  # if window exists focus it

        def do_freq_type() -> None:
            global letter_rank_file
            if self.use_classic_frequency.get():
                letter_rank_file = 'letter_ranks.txt'
            else:
                letter_rank_file = 'letter_ranks_bot.txt'
            do_grep()
            if self.wnd_help is not None:
                # This seems to be the only way to avoid an exception if the
                # wnd_help had already been visible but also destroyed. It remains
                # existing, i.e., not None even after being destroyed. In this condition
                # it has no children (parts) that would error if an update tries to
                # change.
                if len(self.wnd_help.children) > 0:
                    update_help_wind(letter_rank_file)

        def do_list_by() -> None:
            do_grep()

        def update_help_wind(letter_rank_file) -> None:
            self.wnd_help.letter_rank_file = letter_rank_file
            self.wnd_help.show_rank_info()
            self.wnd_help.deiconify()

        def do_grep() -> None:
            """Runs a wordletool helper grep instance
            """
            # used to suppress multiple greps when clearing all settings
            if self.suppress_grep:
                return

            global data_path
            # a set to manage the letter requirements
            rq_ltrs = get_rq_ltrs(self)

            allow_dups = self.allow_dup_state.get()

            if self.vocab_var.get() == 0:
                vocab_filename = classic_pos_sol_wrd_list
            elif self.vocab_var.get() == 1:
                vocab_filename = bot_pos_sol_wrd_list
            else:
                vocab_filename = full_wordle_wrd_list

            # create the wordletool instance
            wordletool = hlp.ToolResults(data_path,  # relative path to worddata
                                         vocab_filename,  # the vocabulary considered for solutions or guesses
                                         letter_rank_file,  # file that cointains letter rank data
                                         allow_dups,  # allow duplicate multiple letters
                                         self.rank_mode.get(),  # return ranked data
                                         self.ordr_by_rank.get(),  # return data ordered by rank
                                         self.cull_the_pu.get(),  # cull the previously used words from the solutions
                                         pu_sol_wrd_list  # filename for the previously used words
                                         )

            # The filter builders. Each of these adds to the grep command argument list
            wordletool.tool_command_list.add_cmd(build_exclude_grep(self.ex_btn_vars))
            wordletool.tool_command_list.add_cmd(build_require_these_grep(rq_ltrs))
            hlp.build_x_pos_grep(wordletool, x_pos_dict, rq_ltrs)
            req_pat = hlp.build_r_pos_grep(wordletool, r_pos_dict)

            # needed to show the last user entry in title_context with the sanity question.
            self.update()
            if hlp.wrd_has_duplicates(req_pat) and (not self.allow_dup_state.get()):
                sanity_question(self.entry_spec_pattern)

            if self.sp_pat_mode_var.get() == 1:
                wordletool.tool_command_list.add_type_cmd(self.spec_pattern.get().lower(), True)
            else:
                wordletool.tool_command_list.add_type_cmd(self.spec_pattern.get().lower(), False)

            if len(self.mult_ltr_definition.get()) > 1 and (not self.allow_dup_state.get()):
                sanity_question(self.entry_mult_ltr_def)

            if len(self.mult_ltr_definition.get()) > 1:
                wordletool.tool_command_list.add_type_mult_ltr_cmd(self.mult_ltr_definition.get().lower(),
                                                                   self.mult_ltr_mode_var.get()
                                                                   )

            # Allow duplicates could have been changed by this point and also by this next
            # special pattern check. Thus, the wordletool.loc_allow_dups is reset accordingly before
            # the final word list is generated.
            coordinate_special_pattern_dups()
            allow_dups = self.allow_dup_state.get()
            wordletool.allow_dups = allow_dups

            tx_result.configure(state='normal')
            tx_result.delete(1.0, tk.END)

            # Wordletool is now ready to filter the list and return the list ranked
            # according to the rank arguments.
            the_word_list = wordletool.get_ranked_grep_result_wrd_lst()

            n_items = len(the_word_list)
            left_pad = ""
            mid_pad = "  "
            mid_div = " : "
            c = 0
            i = 0
            l_msg = ""
            for key, value in the_word_list.items():
                msg = key + mid_div + str(value)
                i = i + 1
                if c == 0:
                    l_msg = left_pad + msg
                else:
                    l_msg = l_msg + mid_pad + msg
                c = c + 1
                if c == self.set_n_col():
                    tx_result.insert(tk.END, l_msg + '\n')
                    c = 0
                    l_msg = ""
                if i == n_items:
                    tx_result.insert(tk.END, l_msg + '\n')

            # configure header line for thge result text
            str_wrd_list_hrd()

            comment = ""
            # Pick a random word
            if self.sel_rando and (n_items > 0):
                word, rank = random.choice(list(the_word_list.items()))
                rand_pick = word + mid_div + rank
                # highlight the rand_pick, which also scrolls the widget
                # to the rand_pick's line.
                tx_result.highlight_pattern(rand_pick, 'ran', remove_priors=False)
                comment = " (1 random pick selected)"

            # Not classic marking
            if self.sel_not_classic and (n_items > 0):
                wrds_showing: list = list(the_word_list.keys())
                classic_wrds = hlp.get_classic_wordlist(
                    hlp.get_word_list_path_name(data_path + classic_pos_sol_wrd_list, False))
                bot_added_wrds = list(set(wrds_showing) - set(classic_wrds))
                regex: str = hlp.regex_maxgenrankers(bot_added_wrds, the_word_list)
                tx_result.highlight_pattern(regex, 'add', remove_priors=False)
                comment = " (" + str(len(bot_added_wrds)) + " non originals selected)"

            # Genetic ranking
            if self.sel_genetic and (n_items > 0):
                gendict: dict[str, list] = {}
                for w in the_word_list.keys():
                    gencode = hlp.get_gencode(w)
                    gendict.update({w: gencode})
                gen_tally: list = hlp.get_gendict_tally(gendict)
                maxrank: int = hlp.assign_genrank(gendict, gen_tally)
                max_rankers: list = hlp.get_maxgenrankers(gendict, maxrank)
                regex: str = hlp.regex_maxgenrankers(max_rankers, the_word_list)
                tx_result.highlight_pattern(regex, 'gen', remove_priors=False)
                comment = " (" + str(len(max_rankers)) + " highest genetic rank selected)"
                if self.meta_lr:
                    hlp.rpt_ltr_use(gen_tally, list(the_word_list.keys()))
                    self.meta_lr = False

            # group optimals ranking
            if self.sel_outcm_optimal and (n_items > 0):
                self.enable_optimal_controls('disabled')
                # Clear any highlighting prior to what could be a long wait.
                tx_result.remove_tag('opt')
                # This requires forcing TK to update the display now instead of later.
                self.update()
                # current displayed word list
                remaining_word_list = list(the_word_list.keys())
                # Flag to use various solutions as guesses instead of the current displayed word list.
                # This allows the option to group rank from the entire guess list.
                grps_guess_source = self.outcms_guess_source.get()
                optimal_group_guesses = {}
                context = "Wordle Helper"

                hm_grn_pat = ''
                hm_yel_ltrs = []
                if self.use_hard_mode.get():
                    # req_pat is the raw required letter pattern less the ^
                    # hard mode hm_grn_pat to pass to hard mode guess filter
                    hm_grn_pat = ''.join(('^', req_pat))
                    # hard mode hm_yel_ltrs letters to pass to hard mode guess filter
                    for key in x_pos_dict:
                        hm_yel_ltrs.append(key[0].lower())

                match grps_guess_source:
                    case 0:
                        # using the showing words (remaining solutions) for guess candidates
                        optimal_group_guesses = hlp.best_outcomes_from_showing_as_guess_dict(remaining_word_list,
                                                                                             self.verbose_outcms.get(),
                                                                                             self.ent_outcms.get(),
                                                                                             self.cond_outcms.get(),
                                                                                             self.keyed_verbose_outcms.get(),
                                                                                             context)

                    case 1:
                        # using the classic (original possible solutions) words for guess candidates
                        guess_targets = hlp.ToolResults(data_path,
                                                        classic_pos_sol_wrd_list,
                                                        letter_rank_file,
                                                        True,
                                                        0,
                                                        True).get_ranked_grep_result_wrd_lst(True)
                        if self.use_hard_mode.get():
                            guess_targets = hlp.hard_mode_guesses(guess_targets, hm_grn_pat, hm_yel_ltrs)
                            report_msg1 = 'Classic Vocabulary-HM'
                        else:
                            report_msg1 = 'Classic Vocabulary-DF'
                        optimal_group_guesses = hlp.extended_best_outcomes_guess_dict(remaining_word_list,
                                                                                      self.verbose_outcms.get(),
                                                                                      self.ent_outcms.get(),
                                                                                      self.cond_outcms.get(),
                                                                                      self.keyed_verbose_outcms.get(),
                                                                                      guess_targets,
                                                                                      report_msg1,
                                                                                      context,
                                                                                      self.meta_lr)
                    case 2:
                        # using the classic+ (entire possible solutions) for guess candidates
                        guess_targets = hlp.ToolResults(data_path,
                                                        bot_pos_sol_wrd_list,
                                                        letter_rank_file,
                                                        True,
                                                        0,
                                                        True).get_ranked_grep_result_wrd_lst(True)
                        if self.use_hard_mode.get():
                            guess_targets = hlp.hard_mode_guesses(guess_targets, hm_grn_pat, hm_yel_ltrs)
                            report_msg1 = 'Classic+ Vocabulary-HM'
                        else:
                            report_msg1 = 'Classic+ Vocabulary-DF'
                        optimal_group_guesses = hlp.extended_best_outcomes_guess_dict(remaining_word_list,
                                                                                      self.verbose_outcms.get(),
                                                                                      self.ent_outcms.get(),
                                                                                      self.cond_outcms.get(),
                                                                                      self.keyed_verbose_outcms.get(),
                                                                                      guess_targets,
                                                                                      report_msg1,
                                                                                      context,
                                                                                      self.meta_lr)
                    case 3:
                        # using the entire allowed guess list for guess candidates
                        guess_targets = hlp.ToolResults(data_path,
                                                        full_wordle_wrd_list,
                                                        letter_rank_file,
                                                        True,
                                                        0,
                                                        True).get_ranked_grep_result_wrd_lst(True)
                        if self.use_hard_mode.get():
                            guess_targets = hlp.hard_mode_guesses(guess_targets, hm_grn_pat, hm_yel_ltrs)
                            report_msg1 = 'Large Vocabulary-HM'
                        else:
                            report_msg1 = 'Large Vocabulary-DF'
                        optimal_group_guesses = hlp.extended_best_outcomes_guess_dict(remaining_word_list,
                                                                                      self.verbose_outcms.get(),
                                                                                      self.ent_outcms.get(),
                                                                                      self.cond_outcms.get(),
                                                                                      self.keyed_verbose_outcms.get(),
                                                                                      guess_targets,
                                                                                      report_msg1,
                                                                                      context,
                                                                                      self.meta_lr)
                    case _:
                        pass

                self.meta_lr=False
                opt_group_guesses_as_list = list(optimal_group_guesses.keys())
                (g_qty, g_min, g_max, g_ave, g_p2, g_e, g_xa) = hlp.outcomes_stat_summary(optimal_group_guesses)
                match grps_guess_source:
                    case 0:
                        regex: str = hlp.regex_maxgenrankers(opt_group_guesses_as_list, the_word_list)
                    case _:
                        # The displayed list may not have the words to highlight when the outcms_guess_source
                        # uses more words than what is in the current displayed list. Instead, any common
                        # words will be highlighted.
                        displayed_as_list = list(the_word_list.keys())
                        words_in_common = list(set(displayed_as_list) & set(opt_group_guesses_as_list))
                        regex: str = hlp.regex_maxgenrankers(words_in_common, the_word_list)

                if self.ent_outcms.get():
                    tx_result.highlight_pattern(regex, 'ent', remove_priors=False)
                else:
                    tx_result.highlight_pattern(regex, 'opt', remove_priors=False)
                comment = " (" + str(len(opt_group_guesses_as_list)) + " optimal" + \
                          ", grp qty " + '{0:.0f}'.format(g_qty) + \
                          ", ent " + "{0:.2f}".format(g_e) + \
                          ", sizes: min " + '{0:.0f}'.format(g_min) + \
                          ", min-max " + '{0:.0f}'.format(g_max) + \
                          ", ave " + '{0:.2f}'.format(g_ave) + \
                          ", exp " + '{0:.2f}'.format(g_xa) + \
                          ", p2 " + "{0:.2f}".format(g_p2) + ")"
                self.enable_optimal_controls('active')

            tx_result.configure(state='disabled')
            if not self.sel_rando and not self.sel_outcm_optimal and not self.sel_genetic:
                # Do not scroll to end when a rando pick, genetic or optimal group is highlighted
                tx_result.see('end')
            self.status.set(wordletool.get_status() + comment)
            tx_gr.configure(state='normal')
            tx_gr.delete(1.0, tk.END)
            tx_gr.insert(tk.END, wordletool.get_grep_cmd_less_filepath())
            tx_gr.configure(state='disabled')

        def get_rq_ltrs(self) -> str:
            rq_l = ''
            for b in self.re_btn_vars:
                ltr = b.get()
                if ltr != '-':
                    rq_l += ltr
            return rq_l

        def add_x_pos() -> None:
            x_ltr = self.pos_px_l.get().upper()
            x_pos = self.pos_px_p.get()
            if not x_pos.isnumeric() or int(x_pos) < 1 or int(x_pos) > 5:
                self.pos_px_p.set('1')
                return
            if x_ltr == '' or len(x_ltr) > 1 or x_ltr.isnumeric():
                self.pos_px_l.set('')
                return
            self.pos_px_l.set(x_ltr)
            key = x_ltr + ',' + x_pos
            value = key
            x_pos_dict[key] = value
            fill_treeview_per_dictionary(self.treeview_px, x_pos_dict, 0)
            remove_already_from_cbox_px(self.pos_px_l.get())
            reset_cbox_focus(self.cbox_px_l)

        def add_r_pos() -> None:
            x_ltr = self.pos_pr_l.get().upper()
            x_pos = self.pos_pr_p.get()
            # toss out of range position numbers
            if not x_pos.isnumeric() or int(x_pos) < 1 or int(x_pos) > 5:
                self.pos_pr_p.set('1')
                return
            # toss any invalid entries in the letter cbox
            if x_ltr == '' or len(x_ltr) > 1 or x_ltr.isnumeric():
                self.pos_pr_l.set('')
                return
            self.pos_pr_l.set(x_ltr)
            # continue if pos is available
            if x_pos in self.pos_r:
                # update loc_r_pos_dict and update treeview
                key = x_ltr + ',' + x_pos
                value = key
                r_pos_dict[key] = value
                fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)
                # remove position from rpos and in turn the combobox
                self.pos_r.remove(x_pos)
                conform_cbox(self.cbox_pr_p, self.pos_r, self.pos_pr_p)
                reset_cbox_focus(self.cbox_pr_l)

        def reset_cbox_focus(entrywidget) -> None:
            # now set focus back to the letter cbox for use next assignment convenience
            entrywidget.focus()
            # and make the letter look selected even though it makes no difference
            entrywidget.selection_range(0, 1)

        def remove_x_pos() -> None:
            x_ltr = self.pos_px_l.get().upper()
            x_pos = self.pos_px_p.get()
            if x_ltr == '' or len(x_ltr) > 1 or x_ltr.isnumeric():
                self.pos_px_l.set('')
                return
            self.pos_px_l.set(x_ltr)
            key = x_ltr + ',' + x_pos
            if key in x_pos_dict:
                del x_pos_dict[key]
                fill_treeview_per_dictionary(self.treeview_px, x_pos_dict, 0)
            remove_already_from_cbox_px(self.pos_px_l.get())

        def clear_all_x_pos() -> None:
            x_pos_dict.clear()
            fill_treeview_per_dictionary(self.treeview_px, x_pos_dict, 0)
            self.cbox_px_l.current(0)
            self.cbox_px_p.current(0)
            exclude.clear()

        def remove_r_pos() -> None:
            # Note - This differs radically from remove_x_pos because in the
            # requirement gui the position number combobox value is prevented from
            # showing a position that is present in the treeview.
            cur_item = self.treeview_pr.focus()
            val_tup = self.treeview_pr.item(cur_item).get('values')
            if val_tup != '':
                x_ltr = (val_tup[0]).upper()
                x_pos = str(val_tup[1])
            else:
                return
            key = x_ltr + ',' + x_pos
            if key in r_pos_dict:
                del r_pos_dict[key]
                fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)
                # add back position to rpos and the combobox
                self.pos_r.append(x_pos)
                self.pos_r.sort()
                conform_cbox(self.cbox_pr_p, self.pos_r, self.pos_pr_p)

        def conform_cbox(cbox: ttk.Combobox, vals: list, bindvar: tk.StringVar) -> None:
            cbox.configure(values=vals)
            if vals:
                cbox.current(0)
            else:
                # no more positions, index cannot be set to 0
                bindvar.set('')
            self.update()

        def clear_all_r_pos() -> None:
            r_pos_dict.clear()
            fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)
            self.pos_r = self.pos5.copy()
            conform_cbox(self.cbox_pr_p, self.pos_r, self.pos_pr_p)
            self.cbox_pr_l.current(0)

        # clears all settings
        def clear_all() -> None:
            self.suppress_grep = True
            clear_all_r_pos()
            clear_all_x_pos()
            clear_excl_chkbs()
            clear_reqr_ckbs()
            self.suppress_grep = False
            clear_specials()

        # select all not classic words
        def not_classic() -> None:
            self.sel_not_classic = True
            self.title("> > > ... Busy Finding Not Classics ... < < <")
            do_grep()
            self.title("This Wordle Helper")
            self.sel_not_classic = False

        # selected a random word in the result
        def pick_rando() -> None:
            self.sel_rando = True
            do_grep()
            self.sel_rando = False

        # selected genetic ranking in the result
        def pick_genetic() -> None:
            self.sel_genetic = True
            do_grep()
            self.sel_genetic = False

        # selected optimal group ranking in the result
        def pick_optimals() -> None:
            self.sel_outcm_optimal = True
            self.title("> > > ... Busy Finding Optimals ... < < <")
            do_grep()
            self.title("This Wordle Helper")
            self.sel_outcm_optimal = False

        def cond_outcms_chk() -> None:
            if not self.verbose_outcms.get():
                self.verbose_outcms.set(self.cond_outcms.get())

        # Clears and fills a treeview with dictionary contents
        # Results are sorted by the dictionary keys.
        # By_what indicated by key 0 or by value 1 so that the required position
        # list sorts by the position while the excluded position list sorts by
        # the letter.
        def fill_treeview_per_dictionary(this_treeview, this_pos_dict: dict, by_what: int) -> None:
            for i in this_treeview.get_children():
                this_treeview.delete(i)
            i = 0
            sort_by_what_dict = {}
            if by_what == 0:  # the letter
                for j in sorted(this_pos_dict):
                    sort_by_what_dict[j] = this_pos_dict[j]
            if by_what == 1:  # the position number
                tlist = sorted(this_pos_dict.items(), key=lambda lx: lx[1].split(',')[1])
                sort_by_what_dict = dict(tlist)
            for x in sort_by_what_dict:
                parts = this_pos_dict[x].split(',')
                this_treeview.insert(parent='', index=i, id=i, values=parts)
                i += 1
            do_grep()

        def build_exclude_grep(ex_btn_var_list: list) -> str:
            """Builds the grep line for excluding letters
            """
            # example 'grep -vE \'b|f|k|w\''
            grep_exclude = ""
            pipe = "|"
            lts = []
            for b in ex_btn_var_list:
                ltr = b.get()
                if ltr != '-':
                    lts.append(ltr)
            args = pipe.join(lts)
            if len(lts) > 0:
                grep_exclude = "grep -vE \'" + args + "\'"
            return grep_exclude

        def build_require_these_grep(rq_lts: str) -> str:
            """Builds the grep line for requiring letters
            """
            # example 'grep -E \'b|f|k|w\''
            grep_require_these = ""
            pipe = "| "
            itms = []
            for ltr in rq_lts:
                itms.append("grep -E \'" + ltr + "\'")
            args = pipe.join(itms)
            if len(itms) > 0:
                grep_require_these = args
            return grep_require_these

        # def on_window_resize(event):
        #     width = event.width
        #     height = event.height
        #     print(f"Window resized to {width}x{height}")
        #     sw = self.result_frame.winfo_width()
        #     print(f"result_frame.winfo_width {sw}")
        #     sw = self.winfo_screenwidth()
        #     print(f"winfo_screenwidth {sw}")

        # upper frame showing the words
        self.result_frame = ctk.CTkFrame(self,
                                         corner_radius=10
                                         )
        self.result_frame.pack(anchor="n", padx=10, pady=2, fill="both", expand=1)
        self.result_frame.grid_columnconfigure(0, weight=1)  # non-zero weight allows grid to expand
        self.result_frame.grid_rowconfigure(1, weight=100)  # allows row 1 to expand (with sticky)
        self.result_frame.grid_rowconfigure(2, weight=1)
        self.result_frame.grid_rowconfigure(3, weight=1)

        # self.pw.add(self.result_frame)

        # the header line above the word list
        lb_result_hd = tk.Label(self.result_frame,
                                font=('Courier', 12, 'bold'),
                                relief='sunken',
                                background='#dedede',
                                anchor='w',
                                borderwidth=0,
                                highlightthickness=0)
        lb_result_hd.grid(row=0, column=0, columnspan=4, sticky='enw', padx=6, pady=2)
        lb_result_hd.bind("<Configure>", str_wrd_list_hrd())
        # The word list resulting from grep on the main wordlist
        # The CustomText class is a tk.Text extended to support a color for matched text.
        tx_result = hlp.CustomText(self.result_frame,
                                   font=('Courier', 12, 'normal'),
                                   wrap='word',
                                   background='#dedede',
                                   borderwidth=0,
                                   highlightthickness=0)
        tx_result.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=2)
        # tx_result.bind("<Configure>", on_window_resize)
        # The CustomText class is a tk.Text extended to support a color for matched text.
        # #c6e2ff = red 198, green 226, blue 255 => a light blue, www.color-hex.com
        # tag 'opt' is used to highlight group ranker
        tx_result.tag_configure('opt', background='#fff69a')
        # tag 'ran' is used to highlight random pick
        tx_result.tag_configure('ran', background='#7cfc00')
        # tag 'gen' is used to highlight genetic pick
        tx_result.tag_configure('gen', background='#ffb8f2')
        # tag 'ent' is used to highlight entropy pick
        tx_result.tag_configure('ent', background='#ffd700')
        # tag 'add' is used to highlight non classic words
        tx_result.tag_configure('add', background='#b6df00')

        # scrollbar for wordlist
        tx_results_sb = ttk.Scrollbar(self.result_frame, orient='vertical')
        tx_results_sb.grid(row=1, column=5, sticky='ens')
        tx_result.config(yscrollcommand=tx_results_sb.set)
        tx_results_sb.config(command=tx_result.yview)
        # status line
        lb_status = tk.Label(self.result_frame,
                             textvariable=self.status,
                             font=('Courier', 12, 'normal'),
                             background='#dedede',
                             borderwidth=0,
                             highlightthickness=0)
        lb_status.grid(row=2, rowspan=1, column=0, columnspan=4, sticky='nsew', padx=6, pady=4)
        self.status.set('No status yet.')

        # grep line being used
        tx_gr = tk.Text(self.result_frame,
                        wrap='word',
                        font=('Courier', 12, 'normal'),
                        height=2,
                        background='#dedede',
                        borderwidth=0,
                        highlightthickness=0)
        tx_gr.grid(row=4, column=0, columnspan=4, sticky='nsew', padx=6, pady=4)
        tx_gr.delete(1.0, tk.END)
        # scrollbar for grep line
        tx_gr_sb = ttk.Scrollbar(self.result_frame, orient='vertical')
        tx_gr_sb.grid(row=4, column=5, sticky='ens', pady=4)
        tx_gr.config(yscrollcommand=tx_gr_sb.set)
        tx_gr_sb.config(command=tx_gr.yview)

        # Divide results from controls
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.bottomhalf_frame = ctk.CTkFrame(self,
                                             corner_radius=10
                                             )
        self.bottomhalf_frame.pack(anchor="s", padx=10, pady=2, fill=tk.X, expand=0)
        # self.pw.add(self.bottomhalf_frame)

        # grep criteria outer frame holding:
        # letter require frame
        # letter exclusion frame
        # letter position frame
        self.criteria_frame = ctk.CTkFrame(self.bottomhalf_frame,
                                           corner_radius=10
                                           )
        self.criteria_frame.pack(fill=tk.X, padx=0, pady=0, expand=1)

        # letter checkbox exclusion frame - uses pack
        self.criteria_frame_x = ttk.LabelFrame(self.criteria_frame,
                                               text='Letters To Be Excluded',
                                               border=0,
                                               borderwidth=0
                                               )
        self.criteria_frame_x.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0, expand=1)

        # letter checkbox require frame - uses pack
        self.criteria_frame_r = ttk.LabelFrame(self.criteria_frame,
                                               text='Letters To Be Required',
                                               border=0,
                                               borderwidth=0
                                               )
        self.criteria_frame_r.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0, expand=1)

        # letter position frame overall - uses pack
        self.criteria_frame_p = ttk.LabelFrame(self.criteria_frame,
                                               text='Letter Positioning',
                                               labelanchor='n',
                                               border=0,
                                               borderwidth=0
                                               )
        self.criteria_frame_p.pack(side=tk.LEFT, fill=tk.BOTH, padx=0, pady=0, expand=1)

        # letter position frame exclude - uses pack
        self.criteria_frame_px = ttk.LabelFrame(self.criteria_frame_p,
                                                text='Exclude From Position',
                                                labelanchor='n',
                                                border=0,
                                                borderwidth=0
                                                )
        self.criteria_frame_px.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0, expand=1)

        # letter position frame require- uses pack
        self.criteria_frame_pr = ttk.LabelFrame(self.criteria_frame_p,
                                                text='Require At Position',
                                                labelanchor='n',
                                                border=0,
                                                borderwidth=0
                                                )
        self.criteria_frame_pr.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0, expand=1)

        # outer frame for multiple actions frame require- uses pack
        self.actions_outer_frame = ctk.CTkFrame(self.criteria_frame,
                                                corner_radius=10
                                                )
        self.actions_outer_frame.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=0, expand=1)

        # =======  START OF ============ include special patterns control
        # frame for special pattern regex - uses pack
        self.specialpatt_frame = ttk.LabelFrame(self.actions_outer_frame,
                                                text='Special Patterns and Multiple Same Letters',
                                                labelanchor='n',
                                                border=0,
                                                borderwidth=0
                                                )
        self.specialpatt_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0, expand=1)

        self.specialpatt_subframeA = ctk.CTkFrame(self.specialpatt_frame, corner_radius=4)
        self.specialpatt_subframeA.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0, expand=1)

        self.specialpatt_subframeB = ctk.CTkFrame(self.specialpatt_frame, corner_radius=4)
        self.specialpatt_subframeB.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0, expand=1)

        # special pattern control variables
        self.spec_pattern = tk.StringVar()
        self.sp_pat_mode_var = tk.IntVar(value=1)

        # multiple letter control variables
        self.mult_ltr_definition = tk.StringVar()
        self.mult_ltr_mode_var = tk.IntVar(value=2)

        # Coordinate duplicates in special pattern with no dup setting
        def coordinate_special_pattern_dups() -> None:
            self.update()
            if hlp.wrd_has_duplicates(self.spec_pattern.get()) and (not self.allow_dup_state.get()):
                sanity_question(self.entry_spec_pattern)

        def sanity_question(entry: ttk.Entry) -> None:
            res = tk.messagebox.askyesno(title='Sanity Check',
                                         message='Duplicate letters are being required but that option is not set. Do '
                                                 'you want duplicate letters allowed? Otherwise no words will show.')
            if res:
                self.allow_dup_state.set(True)
            self.after(200, lambda: self.focus_set())

        def do_spec_pat(*args) -> None:
            # In this ui all text is shown in uppercase and there can be only five letters
            self.spec_pattern.set('%.5s' % scrub_text(self.spec_pattern.get(), '', True, False).upper())
            do_grep()

        def do_mult_ltr_def(*args) -> None:
            # In this ui all text is shown in uppercase and the format must conform to:
            # <number><letter>,<number><letter>
            self.mult_ltr_definition.set(hlp.validate_mult_ltr_sets(self.mult_ltr_definition.get()))
            do_grep()

        # label for Pattern Special
        self.lb_sp_pat = ctk.CTkLabel(self.specialpatt_subframeA,
                                      text='Pattern'
                                      )
        self.lb_sp_pat.pack(side=tk.LEFT, fill=tk.X, padx=4, pady=4, expand=True)

        # special pattern entry clear
        def clear_specials():
            self.spec_pattern.set('')
            self.mult_ltr_definition.set('')

        # The special pattern controls are in a sub frame and all but the text label are RIGHT positioned.
        # Therefore, they are defined from last to first.
        # Special pattern mode radio buttons
        rb_px = ttk.Radiobutton(self.specialpatt_subframeA, text="Exclude", variable=self.sp_pat_mode_var, value=2,
                                command=do_spec_pat)
        rb_px.pack(side=tk.RIGHT, padx=2, pady=0)
        rb_pi = ttk.Radiobutton(self.specialpatt_subframeA, text="Require", variable=self.sp_pat_mode_var, value=1,
                                command=do_spec_pat)
        rb_pi.pack(side=tk.RIGHT, padx=2, pady=0)
        # special pattern clear button
        self.bt_pat_clr = ctk.CTkButton(self.specialpatt_subframeA,
                                        text="Clear",
                                        width=20,
                                        text_color="black",
                                        command=clear_specials
                                        )
        self.bt_pat_clr.pack(side=tk.RIGHT, padx=2, pady=0)

        # binding a special pattern entry validator
        try:
            # python 3.6
            self.spec_pattern.trace_add('write', do_spec_pat)
        except AttributeError:
            # python < 3.6
            self.spec_pattern.trace('w', do_spec_pat)
        # special pattern entry field
        self.entry_spec_pattern = ttk.Entry(self.specialpatt_subframeA,
                                            textvariable=self.spec_pattern,
                                            width=8,
                                            justify='center')
        self.entry_spec_pattern.pack(side=tk.RIGHT, padx=0, pady=4)
        # ............ end special pattern

        # ............ multiple same letters section
        # The multiple same letters controls are in a sub frame and all but the text label are RIGHT positioned.
        # Therefore, they are defined from last to first.
        self.lb_mult_ltrs = ctk.CTkLabel(self.specialpatt_subframeB,
                                         text='Multiples',
                                         )
        self.lb_mult_ltrs.pack(side=tk.LEFT, fill=tk.X, padx=4, pady=4, expand=True)

        # multiple same letters clear
        def clear_mult_ltr_def() -> None:
            self.mult_ltr_definition.set('')

        # multiple same letter radio buttons
        rb_mult_x = ttk.Radiobutton(self.specialpatt_subframeB, text="Exclude", variable=self.mult_ltr_mode_var,
                                    value=2,
                                    command=do_mult_ltr_def)
        rb_mult_x.pack(side=tk.RIGHT, padx=2, pady=0)
        rb_mult_i = ttk.Radiobutton(self.specialpatt_subframeB, text="Require", variable=self.mult_ltr_mode_var,
                                    value=1,
                                    command=do_mult_ltr_def)
        rb_mult_i.pack(side=tk.RIGHT, padx=2, pady=0)
        # multiple same letter clear button
        self.bt_mult_ltr_clr = ctk.CTkButton(self.specialpatt_subframeB,
                                             text="Clear",
                                             width=20,
                                             text_color="black",
                                             command=clear_mult_ltr_def
                                             )
        self.bt_mult_ltr_clr.pack(side=tk.RIGHT, padx=2, pady=0)
        # multiple same letters entry validator
        try:
            # python 3.6
            self.mult_ltr_definition.trace_add('write', do_mult_ltr_def)
        except AttributeError:
            # python < 3.6
            self.mult_ltr_definition.trace('w', do_mult_ltr_def)
        # multiple same letters entry field
        self.entry_mult_ltr_def = ttk.Entry(self.specialpatt_subframeB,
                                            textvariable=self.mult_ltr_definition,
                                            width=8,
                                            justify='center')
        self.entry_mult_ltr_def.pack(side=tk.RIGHT, padx=0, pady=4)

        # ............ end multiple same letter
        # =======  END OF ======== include special pattern and mulitple letters control

        # actions frame general - uses pack
        self.actions_frame = ttk.LabelFrame(self.actions_outer_frame,
                                            text='General Settings',
                                            labelanchor='n',
                                            border=0,
                                            borderwidth=0
                                            )
        self.actions_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=0, pady=2, expand=True)

        # =======  START OF ============ exclude from position controls
        # === position exclude letter
        # conform the position exclude letter
        def pos_px_ltr_conform(*args) -> None:
            cbox_entry_conform(self.pos_px_l, True, False)
            # Once the letter is set, it would be nice to have the position
            # cbox reset to have only the positions not already assigned to
            # the letter.
            remove_already_from_cbox_px(self.pos_px_l.get())

        def remove_already_from_cbox_px(new_ltr: str):
            cur_pos_cbox = self.pos5.copy()
            for x in x_pos_dict:
                parts = x_pos_dict[x].split(',')
                ltr = parts[0]
                p = parts[1]
                if ltr == new_ltr:
                    # remove existing position option
                    cur_pos_cbox.remove(str(p))
            conform_cbox(self.cbox_px_p, cur_pos_cbox, self.pos_px_p)

        self.pos_px_l = tk.StringVar(name='pos_px_l')
        self.cbox_px_l = ttk.Combobox(self.criteria_frame_px,
                                      values=('', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                                              'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                                              'X', 'Y', 'Z'),
                                      width=4,
                                      justify=tk.CENTER,
                                      textvariable=self.pos_px_l,
                                      font=("Helvetica", 10, "normal")
                                      )
        self.cbox_px_l.grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.cbox_px_l.current(0)
        try:
            # python 3.6
            self.pos_px_l.trace_add('write', pos_px_ltr_conform)
        except AttributeError:
            # python < 3.6
            self.pos_px_l.trace('w', pos_px_ltr_conform)

        # === position exclude letter's position
        # conform the position exclude position
        def pos_px_p_conform(*args) -> None:
            cbox_entry_conform(self.pos_px_p, False, True)

        self.pos_px_p = tk.StringVar(name='pos_px_p')
        self.cbox_px_p = ttk.Combobox(self.criteria_frame_px,
                                      values=('1', '2', '3', '4', '5'),
                                      width=4,
                                      justify=tk.CENTER,
                                      textvariable=self.pos_px_p,
                                      font=("Helvetica", 10, "normal")
                                      )
        self.cbox_px_p.grid(row=0, column=1, padx=1, pady=2, sticky='w')
        self.cbox_px_p.current(0)
        try:
            # python 3.6
            self.pos_px_p.trace_add('write', pos_px_p_conform)
        except AttributeError:
            # python < 3.6
            self.pos_px_p.trace('w', pos_px_p_conform)

        self.bt_px_add = ctk.CTkButton(self.criteria_frame_px,
                                       text="+", width=20,
                                       text_color="black",
                                       command=add_x_pos
                                       )
        self.bt_px_add.grid(row=0, column=2, padx=1, pady=2, sticky='ew')

        self.bt_px_rem = ctk.CTkButton(self.criteria_frame_px,
                                       text="-", width=20,
                                       text_color="black",
                                       command=remove_x_pos
                                       )
        self.bt_px_rem.grid(row=0, column=3, padx=1, pady=2, sticky='ew')
        self.bt_px_clr = ctk.CTkButton(self.criteria_frame_px,
                                       text="z", width=20,
                                       text_color="black",
                                       command=clear_all_x_pos
                                       )
        self.bt_px_clr.grid(row=0, column=4, padx=1, pady=2, sticky='ew')

        # ======  exclude position treeview
        self.treeview_px = ttk.Treeview(self.criteria_frame_px, style='position.ttk.Treeview')
        self.treeview_px.configure(columns=('1', '2'),
                                   show='headings',
                                   height=7)
        self.treeview_px.grid(row=1, column=0, columnspan=5, padx=4, pady=2, sticky='ew')
        ttk.Style().configure('Treeview', relief='raised')
        self.treeview_px.heading(1, text='Letter')
        self.treeview_px.heading(2, text='Position')
        for column in self.treeview_px["columns"]:
            self.treeview_px.column(column, anchor=tk.CENTER)  # This will center text in rows
            self.treeview_px.column(column, width=80)
        # selection callback
        self.treeview_px.bind('<ButtonRelease-1>', self.x_pos_tree_view_click)
        # scrollbar for treeview
        sb = ttk.Scrollbar(self.criteria_frame_px, orient=tk.VERTICAL)
        sb.grid(row=1, column=4, padx=1, pady=2, sticky='ens')
        self.treeview_px.config(yscrollcommand=sb.set)
        sb.config(command=self.treeview_px.yview)

        # =======  END OF ============ exclude from position controls

        def cbox_entry_conform(string_var: tk.StringVar, no_nmbrs: bool, no_ltrs5: bool) -> None:
            """
            Make a combobox control accept and show only one letter or number
            @string_var: tk.StringVar - The string var for the combobox
            @no_nmbrs: bool - Passed to scrub_text, If true then also exclude numbers 0-9
            @no_ltrs5: bool - Passed to scrub_text, If true then exclude letters AND numbers 0,6-9
            """
            if len(string_var.get()) > 0:
                string_var.set(scrub_text(string_var.get().upper(), '.', no_nmbrs, no_ltrs5))
            if len(string_var.get()) > 0:
                string_var.set(string_var.get()[-1])

        # =======  START OF ============ require from position controls
        def pr_to_uppercase(*args) -> None:
            cbox_entry_conform(self.pos_pr_l, True, False)

        self.pos_pr_l = tk.StringVar()
        self.cbox_pr_l = ttk.Combobox(self.criteria_frame_pr,
                                      values=('', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                                              'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                                              'X', 'Y', 'Z'),
                                      width=4,
                                      justify=tk.CENTER,
                                      textvariable=self.pos_pr_l,
                                      font=("Helvetica", 10, "normal")
                                      )
        self.cbox_pr_l.grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.cbox_pr_l.current(0)
        try:
            # python 3.6
            self.pos_pr_l.trace_add('write', pr_to_uppercase)
        except AttributeError:
            # python < 3.6
            self.pos_pr_l.trace('w', pr_to_uppercase)

        def cbox_pos_conform(*args) -> None:
            cbox_entry_conform(self.pos_pr_p, False, True)

        self.pos_pr_p = tk.StringVar()
        self.cbox_pr_p = ttk.Combobox(self.criteria_frame_pr,
                                      values=self.pos5,
                                      width=4,
                                      justify=tk.CENTER,
                                      textvariable=self.pos_pr_p,
                                      font=("Helvetica", 10, "normal")
                                      )
        self.cbox_pr_p.grid(row=0, column=1, padx=1, pady=2, sticky='w')
        self.cbox_pr_p.current(0)
        try:
            # python 3.6
            self.pos_pr_p.trace_add('write', cbox_pos_conform)
        except AttributeError:
            # python < 3.6
            self.pos_pr_p.trace('w', cbox_pos_conform)

        self.bt_pr_add = ctk.CTkButton(self.criteria_frame_pr,
                                       text="+", width=20,
                                       text_color="black",
                                       command=add_r_pos
                                       )
        self.bt_pr_add.grid(row=0, column=2, padx=1, pady=2, sticky='ew')

        self.bt_pr_rem = ctk.CTkButton(self.criteria_frame_pr,
                                       text="-", width=20,
                                       text_color="black",
                                       command=remove_r_pos
                                       )
        self.bt_pr_rem.grid(row=0, column=3, padx=1, pady=2, sticky='ew')

        self.bt_pr_clr = ctk.CTkButton(self.criteria_frame_pr,
                                       text="z", width=20,
                                       text_color="black",
                                       command=clear_all_r_pos
                                       )
        self.bt_pr_clr.grid(row=0, column=4, padx=1, pady=2, sticky='ew')

        self.treeview_pr = ttk.Treeview(self.criteria_frame_pr, style='position.ttk.Treeview')
        self.treeview_pr.configure(columns=('1', '2'),
                                   show='headings',
                                   height=7
                                   )
        self.treeview_pr.grid(row=1, column=0, columnspan=5, padx=4, pady=2, sticky='ew')
        ttk.Style().configure('Treeview', relief='raised')
        self.treeview_pr.heading(1, text='Letter')
        self.treeview_pr.heading(2, text='Position')
        for column in self.treeview_pr["columns"]:
            self.treeview_pr.column(column, anchor=tk.CENTER)  # This will center text in rows
            self.treeview_pr.column(column, width=80)
        # selection callback
        self.treeview_pr.bind('<ButtonRelease-1>', self.r_pos_tree_view_click)
        # scrollbar for treeview
        sb = ttk.Scrollbar(self.criteria_frame_pr, orient=tk.VERTICAL)
        sb.grid(row=1, column=4, padx=1, pady=2, sticky='ens')
        self.treeview_pr.config(yscrollcommand=sb.set)
        sb.config(command=self.treeview_pr.yview)

        # =======  END OF ============ require from position controls

        # clears the checkbox vars for vars in the var_list
        def clear_these_chk_vars(var_list: list) -> None:
            for chk_var in var_list:
                chk_var.set('-')

        # ======= START OF ======== Exclude Letters =============
        self.v_xE = tk.StringVar()
        self.v_xE.set('-')
        bt_x_e = ttk.Checkbutton(self.criteria_frame_x, text="E", variable=self.v_xE, onvalue='e', offvalue='-',
                                 command=do_grep)
        bt_x_e.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xA = tk.StringVar()
        self.v_xA.set('-')
        bt_x_a = ttk.Checkbutton(self.criteria_frame_x, text="A", variable=self.v_xA, onvalue='a', offvalue='-',
                                 command=do_grep)
        bt_x_a.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_1 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_1.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_xR = tk.StringVar()
        self.v_xR.set('-')
        bt_xR = ttk.Checkbutton(self.criteria_frame_x, text="R", variable=self.v_xR, onvalue='r', offvalue='-',
                                command=do_grep)
        bt_xR.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xO = tk.StringVar()
        self.v_xO.set('-')
        bt_xO = ttk.Checkbutton(self.criteria_frame_x, text="O", variable=self.v_xO, onvalue='o', offvalue='-',
                                command=do_grep)
        bt_xO.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xT = tk.StringVar()
        self.v_xT.set('-')
        bt_xT = ttk.Checkbutton(self.criteria_frame_x, text="T", variable=self.v_xT, onvalue='t', offvalue='-',
                                command=do_grep)
        bt_xT.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xI = tk.StringVar()
        self.v_xI.set('-')
        bt_xI = ttk.Checkbutton(self.criteria_frame_x, text="I", variable=self.v_xI, onvalue='i', offvalue='-',
                                command=do_grep)
        bt_xI.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xL = tk.StringVar()
        self.v_xL.set('-')
        bt_xL = ttk.Checkbutton(self.criteria_frame_x, text="L", variable=self.v_xL, onvalue='l', offvalue='-',
                                command=do_grep)
        bt_xL.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xS = tk.StringVar()
        self.v_xS.set('-')
        bt_xS = ttk.Checkbutton(self.criteria_frame_x, text="S", variable=self.v_xS, onvalue='s', offvalue='-',
                                command=do_grep)
        bt_xS.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xN = tk.StringVar()
        self.v_xN.set('-')
        bt_xN = ttk.Checkbutton(self.criteria_frame_x, text="N", variable=self.v_xN, onvalue='n', offvalue='-',
                                command=do_grep)
        bt_xN.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_2 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_2.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_xU = tk.StringVar()
        self.v_xU.set('-')
        bt_xU = ttk.Checkbutton(self.criteria_frame_x, text="U", variable=self.v_xU, onvalue='u', offvalue='-',
                                command=do_grep)
        bt_xU.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xC = tk.StringVar()
        self.v_xC.set('-')
        bt_xC = ttk.Checkbutton(self.criteria_frame_x, text="C", variable=self.v_xC, onvalue='c', offvalue='-',
                                command=do_grep)
        bt_xC.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xY = tk.StringVar()
        self.v_xY.set('-')
        bt_xY = ttk.Checkbutton(self.criteria_frame_x, text="Y", variable=self.v_xY, onvalue='y', offvalue='-',
                                command=do_grep)
        bt_xY.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xH = tk.StringVar()
        self.v_xH.set('-')
        bt_xH = ttk.Checkbutton(self.criteria_frame_x, text="H", variable=self.v_xH, onvalue='h', offvalue='-',
                                command=do_grep)
        bt_xH.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xD = tk.StringVar()
        self.v_xD.set('-')
        bt_xD = ttk.Checkbutton(self.criteria_frame_x, text="D", variable=self.v_xD, onvalue='d', offvalue='-',
                                command=do_grep)
        bt_xD.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xP = tk.StringVar()
        self.v_xP.set('-')
        bt_xP = ttk.Checkbutton(self.criteria_frame_x, text="P", variable=self.v_xP, onvalue='p', offvalue='-',
                                command=do_grep)
        bt_xP.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xG = tk.StringVar()
        self.v_xG.set('-')
        bt_xG = ttk.Checkbutton(self.criteria_frame_x, text="G", variable=self.v_xG, onvalue='g', offvalue='-',
                                command=do_grep)
        bt_xG.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xM = tk.StringVar()
        self.v_xM.set('-')
        bt_xM = ttk.Checkbutton(self.criteria_frame_x, text="M", variable=self.v_xM, onvalue='m', offvalue='-',
                                command=do_grep)
        bt_xM.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_3 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_3.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_xB = tk.StringVar()
        self.v_xB.set('-')
        bt_xB = ttk.Checkbutton(self.criteria_frame_x, text="B", variable=self.v_xB, onvalue='b', offvalue='-',
                                command=do_grep)
        bt_xB.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xF = tk.StringVar()
        self.v_xF.set('-')
        bt_xF = ttk.Checkbutton(self.criteria_frame_x, text="F", variable=self.v_xF, onvalue='f', offvalue='-',
                                command=do_grep)
        bt_xF.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xK = tk.StringVar()
        self.v_xK.set('-')
        bt_xK = ttk.Checkbutton(self.criteria_frame_x, text="K", variable=self.v_xK, onvalue='k', offvalue='-',
                                command=do_grep)
        bt_xK.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xW = tk.StringVar()
        self.v_xW.set('-')
        bt_xW = ttk.Checkbutton(self.criteria_frame_x, text="W", variable=self.v_xW, onvalue='w', offvalue='-',
                                command=do_grep)
        bt_xW.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xV = tk.StringVar()
        self.v_xV.set('-')
        bt_xV = ttk.Checkbutton(self.criteria_frame_x, text="V", variable=self.v_xV, onvalue='v', offvalue='-',
                                command=do_grep)
        bt_xV.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_4 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_4.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_xX = tk.StringVar()
        self.v_xX.set('-')
        bt_xX = ttk.Checkbutton(self.criteria_frame_x, text="X", variable=self.v_xX, onvalue='x', offvalue='-',
                                command=do_grep)
        bt_xX.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xZ = tk.StringVar()
        self.v_xZ.set('-')
        bt_xZ = ttk.Checkbutton(self.criteria_frame_x, text="Z", variable=self.v_xZ, onvalue='z', offvalue='-',
                                command=do_grep)
        bt_xZ.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xQ = tk.StringVar()
        self.v_xQ.set('-')
        bt_xQ = ttk.Checkbutton(self.criteria_frame_x, text="Q", variable=self.v_xQ, onvalue='q', offvalue='-',
                                command=do_grep)
        bt_xQ.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_xJ = tk.StringVar()
        self.v_xJ.set('-')
        bt_xJ = ttk.Checkbutton(self.criteria_frame_x, text="J", variable=self.v_xJ, onvalue='j', offvalue='-',
                                command=do_grep)
        bt_xJ.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.ex_btn_vars = [self.v_xA, self.v_xB, self.v_xC, self.v_xD, self.v_xE, self.v_xF,
                            self.v_xG, self.v_xH, self.v_xI, self.v_xJ, self.v_xK, self.v_xL,
                            self.v_xM, self.v_xN, self.v_xO, self.v_xP, self.v_xQ, self.v_xR,
                            self.v_xS, self.v_xT, self.v_xU, self.v_xV, self.v_xW, self.v_xX,
                            self.v_xY, self.v_xZ]

        def clear_excl_chkbs() -> None:
            clear_these_chk_vars(self.ex_btn_vars)
            do_grep()

        self.bt_x_clr = ctk.CTkButton(self.criteria_frame_x,
                                      text='Clear All', width=100,
                                      text_color="black",
                                      command=clear_excl_chkbs
                                      )
        self.bt_x_clr.pack(side=tk.TOP, padx=2, pady=2, fill=tk.X, expand=True)
        # == END OF ========== Exclude Letters =============

        # ==== START OF =========== Require Letters =============
        self.v_rE = tk.StringVar()
        self.v_rE.set('-')
        bt_r_E = ttk.Checkbutton(self.criteria_frame_r, text="E", variable=self.v_rE, onvalue='e', offvalue='-',
                                 command=do_grep)
        bt_r_E.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rA = tk.StringVar()
        self.v_rA.set('-')
        bt_r_A = ttk.Checkbutton(self.criteria_frame_r, text="A", variable=self.v_rA, onvalue='a', offvalue='-',
                                 command=do_grep)
        bt_r_A.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_1 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_1.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_rR = tk.StringVar()
        self.v_rR.set('-')
        bt_r_R = ttk.Checkbutton(self.criteria_frame_r, text="R", variable=self.v_rR, onvalue='r', offvalue='-',
                                 command=do_grep)
        bt_r_R.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rO = tk.StringVar()
        self.v_rO.set('-')
        bt_r_O = ttk.Checkbutton(self.criteria_frame_r, text="O", variable=self.v_rO, onvalue='o', offvalue='-',
                                 command=do_grep)
        bt_r_O.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rT = tk.StringVar()
        self.v_rT.set('-')
        bt_r_T = ttk.Checkbutton(self.criteria_frame_r, text="T", variable=self.v_rT, onvalue='t', offvalue='-',
                                 command=do_grep)
        bt_r_T.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rI = tk.StringVar()
        self.v_rI.set('-')
        bt_r_I = ttk.Checkbutton(self.criteria_frame_r, text="I", variable=self.v_rI, onvalue='i', offvalue='-',
                                 command=do_grep)
        bt_r_I.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rL = tk.StringVar()
        self.v_rL.set('-')
        bt_r_L = ttk.Checkbutton(self.criteria_frame_r, text="L", variable=self.v_rL, onvalue='l', offvalue='-',
                                 command=do_grep)
        bt_r_L.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rS = tk.StringVar()
        self.v_rS.set('-')
        bt_r_S = ttk.Checkbutton(self.criteria_frame_r, text="S", variable=self.v_rS, onvalue='s', offvalue='-',
                                 command=do_grep)
        bt_r_S.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rN = tk.StringVar()
        self.v_rN.set('-')
        bt_r_N = ttk.Checkbutton(self.criteria_frame_r, text="N", variable=self.v_rN, onvalue='n', offvalue='-',
                                 command=do_grep)
        bt_r_N.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_2 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_2.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_rU = tk.StringVar()
        self.v_rU.set('-')
        bt_r_U = ttk.Checkbutton(self.criteria_frame_r, text="U", variable=self.v_rU, onvalue='u', offvalue='-',
                                 command=do_grep)
        bt_r_U.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rC = tk.StringVar()
        self.v_rC.set('-')
        bt_r_C = ttk.Checkbutton(self.criteria_frame_r, text="C", variable=self.v_rC, onvalue='c', offvalue='-',
                                 command=do_grep)
        bt_r_C.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rY = tk.StringVar()
        self.v_rY.set('-')
        bt_r_Y = ttk.Checkbutton(self.criteria_frame_r, text="Y", variable=self.v_rY, onvalue='y', offvalue='-',
                                 command=do_grep)
        bt_r_Y.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rH = tk.StringVar()
        self.v_rH.set('-')
        bt_r_H = ttk.Checkbutton(self.criteria_frame_r, text="H", variable=self.v_rH, onvalue='h', offvalue='-',
                                 command=do_grep)
        bt_r_H.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rD = tk.StringVar()
        self.v_rD.set('-')
        bt_r_D = ttk.Checkbutton(self.criteria_frame_r, text="D", variable=self.v_rD, onvalue='d', offvalue='-',
                                 command=do_grep)
        bt_r_D.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rP = tk.StringVar()
        self.v_rP.set('-')
        bt_r_P = ttk.Checkbutton(self.criteria_frame_r, text="P", variable=self.v_rP, onvalue='p', offvalue='-',
                                 command=do_grep)
        bt_r_P.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rG = tk.StringVar()
        self.v_rG.set('-')
        bt_r_G = ttk.Checkbutton(self.criteria_frame_r, text="G", variable=self.v_rG, onvalue='g', offvalue='-',
                                 command=do_grep)
        bt_r_G.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rM = tk.StringVar()
        self.v_rM.set('-')
        bt_r_M = ttk.Checkbutton(self.criteria_frame_r, text="M", variable=self.v_rM, onvalue='m', offvalue='-',
                                 command=do_grep)
        bt_r_M.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        sep_3 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_3.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        self.v_rB = tk.StringVar()
        self.v_rB.set('-')
        bt_r_B = ttk.Checkbutton(self.criteria_frame_r, text="B", variable=self.v_rB, onvalue='b', offvalue='-',
                                 command=do_grep)
        bt_r_B.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rF = tk.StringVar()
        self.v_rF.set('-')
        bt_r_F = ttk.Checkbutton(self.criteria_frame_r, text="F", variable=self.v_rF, onvalue='f', offvalue='-',
                                 command=do_grep)
        bt_r_F.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rK = tk.StringVar()
        self.v_rK.set('-')
        bt_r_K = ttk.Checkbutton(self.criteria_frame_r, text="K", variable=self.v_rK, onvalue='k', offvalue='-',
                                 command=do_grep)
        bt_r_K.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rW = tk.StringVar()
        self.v_rW.set('-')
        bt_r_W = ttk.Checkbutton(self.criteria_frame_r, text="W", variable=self.v_rW, onvalue='w', offvalue='-',
                                 command=do_grep)
        bt_r_W.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rV = tk.StringVar()
        self.v_rV.set('-')
        bt_r_V = ttk.Checkbutton(self.criteria_frame_r, text="V", variable=self.v_rV, onvalue='v', offvalue='-',
                                 command=do_grep)
        bt_r_V.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rX = tk.StringVar()
        self.v_rX.set('-')
        sep_4 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_4.pack(side=tk.LEFT, padx=8, fill=tk.Y, expand=True)
        bt_r_X = ttk.Checkbutton(self.criteria_frame_r, text="X", variable=self.v_rX, onvalue='x', offvalue='-',
                                 command=do_grep)
        bt_r_X.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rZ = tk.StringVar()
        self.v_rZ.set('-')
        bt_r_Z = ttk.Checkbutton(self.criteria_frame_r, text="Z", variable=self.v_rZ, onvalue='z', offvalue='-',
                                 command=do_grep)
        bt_r_Z.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rQ = tk.StringVar()
        self.v_rQ.set('-')
        bt_r_Q = ttk.Checkbutton(self.criteria_frame_r, text="Q", variable=self.v_rQ, onvalue='q', offvalue='-',
                                 command=do_grep)
        bt_r_Q.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        self.v_rJ = tk.StringVar()
        self.v_rJ.set('-')
        bt_r_J = ttk.Checkbutton(self.criteria_frame_r, text="J", variable=self.v_rJ, onvalue='j', offvalue='-',
                                 command=do_grep)
        bt_r_J.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.re_btn_vars = [self.v_rA, self.v_rB, self.v_rC, self.v_rD, self.v_rE, self.v_rF,
                            self.v_rG, self.v_rH, self.v_rI, self.v_rJ, self.v_rK, self.v_rL,
                            self.v_rM, self.v_rN, self.v_rO, self.v_rP, self.v_rQ, self.v_rR,
                            self.v_rS, self.v_rT, self.v_rU, self.v_rV, self.v_rW, self.v_rX,
                            self.v_rY, self.v_rZ]

        def clear_reqr_ckbs() -> None:
            clear_these_chk_vars(self.re_btn_vars)
            do_grep()

        self.bt_r_clr = ctk.CTkButton(self.criteria_frame_r,
                                      text='Clear All', width=100,
                                      text_color="black",
                                      command=clear_reqr_ckbs
                                      )
        self.bt_r_clr.pack(side=tk.TOP, padx=2, pady=2, fill=tk.X, expand=True)
        # === END OF ========= Require Letters =============

        # === START OF ====== General Controls ==========
        # the_top_frame
        the_top_frame = ctk.CTkFrame(self.actions_frame,
                                     border_width=0
                                     )
        the_top_frame.pack(padx=6, fill=tk.X, expand=True)

        chk_allow_dups = ttk.Checkbutton(the_top_frame,
                                         text="Allow Duplicate Letters",
                                         variable=self.allow_dup_state,
                                         onvalue=True,
                                         offvalue=False,
                                         padding=0,
                                         command=do_grep)
        chk_allow_dups.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)

        chk_hard_mode = ttk.Checkbutton(the_top_frame,
                                        text="Hard Mode",
                                        variable=self.use_hard_mode,
                                        onvalue=True,
                                        offvalue=False,
                                        padding=0)
        chk_hard_mode.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)

        chk_ordr_by_rank = ttk.Checkbutton(the_top_frame,
                                           text="List By Rank",
                                           variable=self.ordr_by_rank,
                                           onvalue=True,
                                           offvalue=False,
                                           padding=0,
                                           command=do_list_by)
        chk_ordr_by_rank.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)

        # Ranking selection frame
        rank_frame = ttk.LabelFrame(self.actions_frame,
                                    text='Word Ranking By Letter Method',
                                    labelanchor='n',
                                    border=0
                                    )
        rank_frame.pack(padx=6, fill=tk.X, expand=True)
        # Vocabulary radio buttons
        rbr1 = ttk.Radiobutton(rank_frame, text="Occurrence", variable=self.rank_mode, value=0, command=do_grep)
        rbr1.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)
        rbr2 = ttk.Radiobutton(rank_frame, text="Position", variable=self.rank_mode, value=1, command=do_grep)
        rbr2.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)
        rbr3 = ttk.Radiobutton(rank_frame, text="Both", variable=self.rank_mode, value=2, command=do_grep)
        rbr3.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)
        chk_ltr_freq_typ = ttk.Checkbutton(rank_frame,
                                           text="Classic Ranking",
                                           variable=self.use_classic_frequency,
                                           onvalue=True,
                                           offvalue=False,
                                           padding=0,
                                           command=do_freq_type)
        chk_ltr_freq_typ.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)

        # Vocabulary selection frame
        vocab_frame = ttk.LabelFrame(self.actions_frame,
                                     text='Word Vocabulary',
                                     labelanchor='n',
                                     border=0
                                     )
        vocab_frame.pack(padx=6, fill=tk.X, expand=True)
        # Vocabulary radio buttons
        rbv1 = ttk.Radiobutton(vocab_frame, text="Classic", variable=self.vocab_var, value=0, command=do_grep)
        rbv1.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=6, expand=True)
        rbv1B = ttk.Radiobutton(vocab_frame, text="Classic+", variable=self.vocab_var, value=1, command=do_grep)
        rbv1B.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=6, expand=True)
        rbv2 = ttk.Radiobutton(vocab_frame, text="Large", variable=self.vocab_var, value=2, command=do_grep)
        rbv2.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=6, expand=True)
        chk_cull_the_pu = ttk.Checkbutton(vocab_frame,
                                          text="Remove PU Wrds",
                                          variable=self.cull_the_pu,
                                          onvalue=True,
                                          offvalue=False,
                                          command=do_grep)
        chk_cull_the_pu.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=6, expand=True)
        # === END OF ====== General Controls ==========

        # === START OF ====== Application Controls ==========
        # admin (Application) frame - uses pack
        self.admin_frame = ttk.LabelFrame(self.criteria_frame,
                                          text='Application',
                                          labelanchor='n',
                                          border=0
                                          )
        self.admin_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=0, pady=0, expand=True)

        self.close_frame = ctk.CTkFrame(self.admin_frame)
        self.close_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.bt_Q = ctk.CTkButton(self.close_frame, text="Quit",
                                  width=100,
                                  text_color="black", command=self.destroy)
        self.bt_Q.pack(side=tk.RIGHT, padx=4, pady=2)

        self.bt_S = ctk.CTkButton(self.close_frame, text="Close Aux. Windows",
                                  text_color="black",
                                  command=self.close_subs)
        self.bt_S.pack(side=tk.LEFT, padx=4, pady=2, fill=tk.X, expand=True)

        # frame for Information and Grp drill buttons
        self.bt_grpB_frame = ctk.CTkFrame(self.admin_frame)
        self.bt_grpB_frame.pack(side=tk.BOTTOM, padx=0, pady=3, fill=tk.X)

        self.bt_help = ctk.CTkButton(self.bt_grpB_frame, text="Information", width=40, text_color="black",
                                     command=self.show_help)
        self.bt_help.pack(side=tk.LEFT, padx=4, pady=3, fill=tk.X, expand=True)

        self.bt_drill = ctk.CTkButton(self.bt_grpB_frame, text="Outcome Driller",
                                      width=40, text_color="black", command=show_outcome_driller)
        self.bt_drill.pack(side=tk.RIGHT, padx=4, pady=3, fill=tk.X, expand=True)

        # frame for Clear, Random, Genetic buttons
        self.bt_grpA_frame = ctk.CTkFrame(self.admin_frame)
        self.bt_grpA_frame.pack(side=tk.TOP, padx=0, pady=3, fill=tk.X)

        self.bt_zap = ctk.CTkButton(self.bt_grpA_frame, text="Clear Settings", width=40, text_color="black",
                                    command=clear_all)
        self.bt_zap.pack(side=tk.RIGHT, padx=4, pady=1, fill=tk.X, expand=True)

        self.bt_rando = ctk.CTkButton(self.bt_grpA_frame, text="Genetic", width=40, text_color="black",
                                      command=pick_genetic)
        self.bt_rando.pack(side=tk.LEFT, padx=4, pady=1, fill=tk.X, expand=True)

        self.bt_rando = ctk.CTkButton(self.bt_grpA_frame, text="! Classic", width=40, text_color="black",
                                      command=not_classic)
        self.bt_rando.pack(side=tk.LEFT, padx=4, pady=1, fill=tk.X, expand=True)

        self.bt_rando = ctk.CTkButton(self.bt_grpA_frame, text="Random", width=40, text_color="black",
                                      command=pick_rando)
        self.bt_rando.pack(side=tk.LEFT, padx=4, pady=1, fill=tk.X, expand=True)
        # end frame for Clear, Random, Genetic buttons

        # frame for groups outcome options
        self.grp_frame = ctk.CTkFrame(self.admin_frame)
        self.grp_frame.pack(side=tk.TOP, padx=0, pady=3, fill=tk.X, expand=True)

        self.bt_groups = ctk.CTkButton(self.grp_frame,
                                       text="Optimals",
                                       text_color="black",
                                       width=20,
                                       command=pick_optimals)
        self.bt_groups.pack(side=tk.LEFT, padx=4, pady=0, fill=tk.X)
        self.chk_grp_disp = ttk.Checkbutton(self.grp_frame,
                                            text="Verbose",
                                            variable=self.verbose_outcms,
                                            onvalue=True,
                                            offvalue=False
                                            )
        self.chk_grp_disp.pack(side=tk.LEFT, padx=0, pady=0, expand=True)
        self.chk_ent_disp = ttk.Checkbutton(self.grp_frame,
                                            text="Entropy",
                                            variable=self.ent_outcms,
                                            onvalue=True,
                                            offvalue=False
                                            )
        self.chk_ent_disp.pack(side=tk.LEFT, padx=2, pady=0, expand=True)
        self.chk_cond_disp = ttk.Checkbutton(self.grp_frame,
                                             text="Cond",
                                             variable=self.cond_outcms,
                                             onvalue=True,
                                             offvalue=False,
                                             command=cond_outcms_chk
                                             )
        self.chk_cond_disp.pack(side=tk.LEFT, padx=2, pady=0, expand=True)
        self.chk_keyed_disp = ttk.Checkbutton(self.grp_frame,
                                              text="Keyed",
                                              variable=self.keyed_verbose_outcms,
                                              onvalue=True,
                                              offvalue=False
                                              )
        self.chk_keyed_disp.pack(side=tk.LEFT, padx=2, pady=0, expand=True)
        # labelframe within groups frame for which list option
        self.grp_lst_ops_frame = ttk.LabelFrame(self.admin_frame,
                                                text='Vocabulary Source For Guess Word Outcome',
                                                labelanchor='n',
                                                border=0
                                                )
        self.grp_lst_ops_frame.pack(side=tk.TOP, padx=0, pady=4, fill=tk.X)
        self.rbrA = ttk.Radiobutton(self.grp_lst_ops_frame, text="Showing", variable=self.outcms_guess_source,
                                    value=0)
        self.rbrA.pack(side=tk.LEFT, fill=tk.X, padx=6, pady=2, expand=True)
        self.rbrB = ttk.Radiobutton(self.grp_lst_ops_frame, text="Classic", variable=self.outcms_guess_source, value=1)
        self.rbrB.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)
        self.rbrBB = ttk.Radiobutton(self.grp_lst_ops_frame, text="Classic+", variable=self.outcms_guess_source,
                                     value=2)
        self.rbrBB.pack(side=tk.LEFT, fill=tk.X, padx=0, pady=2, expand=True)
        self.rbrC = ttk.Radiobutton(self.grp_lst_ops_frame, text="Large", variable=self.outcms_guess_source, value=3)
        self.rbrC.pack(side=tk.RIGHT, fill=tk.X, padx=0, pady=2, expand=True)
        # end labelframe within groups frame for which list option

        # end groups frame

        # === END OF ====== Application Controls ==========

        # run the initial grep
        do_grep()


# end Pywordlemainwindow class

# def key_handler(event):
#     print(event.char, event.keysym, event.keycode)

def main(args=None):
    this_app = Pywordlemainwindow()
    # this_app.bind("<Key>", key_handler)
    this_app.mainloop()


# ====================================== main ================================================
if __name__ == '__main__':
    main()
