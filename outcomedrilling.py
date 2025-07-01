# ----------------------------------------------------------------
# outcomerilling akseidel 2/2023
# ----------------------------------------------------------------
import tkinter as tk  # assigns tkinter stuff to tk namespace so that
# it may be separate from ttk
import tkinter.messagebox
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk
# namespace so that tk is preserved
import customtkinter as ctk
import helpers as hlp
import re

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

data_path = 'worddata/'  # path from here to data folder
letter_rank_file = 'letter_ranks.txt'


def process_outcms_list(self, o_word_lst: list, d_meta_l=False) -> dict:
    """
    Processes the words list for its outcomes. Uses the method options in the outcomes
    driller for the processing arguments.
    @param self:
    @param o_word_lst: The words list to be examined for outcomes
    @return: dictionary of the optimal words
    """
    # Flag to use various solutions as guesses instead of the current displayed word list.
    # This allows the option to outcome rank from the entire guess list.
    outcms_guess_source = self.outcms_guess_source.get()
    optimal_outcome_guesses = {}
    context = 'Outcome Drilling'
    match outcms_guess_source:
        case 0:
            # using the showing words (remaining solutions) for guess candidates
            optimal_outcome_guesses = hlp.best_outcomes_from_showing_as_guess_dict(o_word_lst,
                                                                                   self.d_verbose_outcms.get(),
                                                                                   self.d_ent_outcms.get(),
                                                                                   self.d_verbose_outcms_cond.get(),
                                                                                   self.d_keyed_verbose_outcms.get(),
                                                                                   context
                                                                                   )

        case 1:
            # using the classic (original possible solutions) words for guess candidates
            all_targets = hlp.ToolResults(data_path,
                                              'wo_nyt_wordlist.txt',
                                              letter_rank_file,
                                              True,
                                              0,
                                              True).get_ranked_grep_result_wrd_lst(True)
            msg1 = 'Classic Vocabulary'
            optimal_outcome_guesses = hlp.extended_best_outcomes_guess_dict(o_word_lst,
                                                                            self.d_verbose_outcms.get(),
                                                                            self.d_ent_outcms.get(),
                                                                            self.d_verbose_outcms_cond.get(),
                                                                            self.d_keyed_verbose_outcms.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context,
                                                                            d_meta_l
                                                                            )
        case 2:
            # using the classic+ (entire possible solutions) for guess candidates
            all_targets = hlp.ToolResults(data_path,
                                              'botadd_nyt_wordlist.txt',
                                              letter_rank_file,
                                              True,
                                              0,
                                              True).get_ranked_grep_result_wrd_lst(True)
            msg1 = 'Classic+ Vocabulary'
            optimal_outcome_guesses = hlp.extended_best_outcomes_guess_dict(o_word_lst,
                                                                            self.d_verbose_outcms.get(),
                                                                            self.d_ent_outcms.get(),
                                                                            self.d_verbose_outcms_cond.get(),
                                                                            self.d_keyed_verbose_outcms.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context,
                                                                            d_meta_l
                                                                            )
        case 3:
            # using the entire allowed guess list for guess candidates
            all_targets = hlp.ToolResults(data_path,
                                              'nyt_wordlist.txt',
                                              letter_rank_file,
                                              True,
                                              0,
                                              True).get_ranked_grep_result_wrd_lst(True)
            msg1 = 'Large Vocabulary'
            optimal_outcome_guesses = hlp.extended_best_outcomes_guess_dict(o_word_lst,
                                                                            self.d_verbose_outcms.get(),
                                                                            self.d_ent_outcms.get(),
                                                                            self.d_verbose_outcms_cond.get(),
                                                                            self.d_keyed_verbose_outcms.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context,
                                                                            d_meta_l
                                                                            )
        case _:
            pass

    return optimal_outcome_guesses


class OutcmsDrillingMain(ctk.CTkToplevel):
    common_msg = '\n> >  Highlighted words are common to both the entry words and the optimal outcome guess words.'
    def_msg = 'Paste or write in the words list into the above entry field.' + \
              '\n\nRaw pastes from the This Wordle Helper will be automatically cleaned and converted to ' + \
              'a valid word list entry.'

    def close_rpt(self) -> None:
        self.destroy()

    def clean_the_outcm_list(self) -> tuple[bool, list[str], list[str]]:
        """
        Processes what was pasted into the word list entry into a proper looking list of
        five-letter words. The intent is to be able to paste raw text copied out of the Helper's
        list window, raw text copied from an Outcome Driller output, and other copied text sources like
        spreadsheet ranges. Numbers, spaces, punctuation, non-alphabet characters and line feeds
        are to be removed.
        @return: a tuple containing Status, the list of five-letter words, the list of invalid words.
        """
        this_outcome = self.outcms_words_text.get()
        # First, strip out numbers, like those that are rankings from
        # the wordle helper and other characters.
        this_outcome = re.sub('[-:;.0123456789()~!@#$%^&*+_|?><`/{}]', '', this_outcome).lower()
        # Let spaces comma separate the words. Commas will be used in a
        # later strip function that operates on section split by comma.
        # Empty words will be culled later on.
        this_outcome = this_outcome.replace(' ', ',')
        # A paste from a spreadsheet row will be tab delineated.
        this_outcome = this_outcome.replace('\t', ',')
        # Handling the newline characters.
        this_outcome = this_outcome.replace('\n', ',')
        # Strip unwanted characters that might be.
        this_lst = [x.strip(' ,[]\"\'\n') for x in this_outcome.split(',')]
        # Remove any empty strings from the list.
        this_lst = [i for i in this_lst if i]
        self.outcms_words_text.set(', '.join(this_lst))

        status = True
        bads = []
        for w in this_lst:
            if len(w) != 5:
                status = False
                bads.append(w)
        return status, this_lst, bads

    def process_entry_list(self):
        (entry_status, this_lst, bads) = self.clean_the_outcm_list()
        if not entry_status:
            self.update()
            tkinter.messagebox.showerror(title='Will Not Proceed',
                                         message='Not proceeding.\nOnly five letter words allowed.'
                                         )
            return
        if self.d_meta_lr:
            if len(this_lst):
                gendict: dict[str, list] = {}
                for w in this_lst:
                    gencode = hlp.get_gencode(w)
                    gendict.update({w: gencode})
                gen_tally: list = hlp.get_gendict_tally(gendict)
                hlp.rpt_ltr_use(gen_tally, this_lst)
            self.d_meta_lr = False
            return
        if len(this_lst) > 2:
            self.title("> > > ... Busy, Please Wait ... < < <")
            self.set_busy_status_msg()
            self.enable_controls('disabled')
            self.update()
            optimal_outcome_guesses = process_outcms_list(self, this_lst, self.d_meta_lr)
            self.d_meta_lr=False

            # Report the results
            self.report_results(this_lst, optimal_outcome_guesses, self.d_verbose_outcms_cond.get())
            self.title("Outcome Drilling")
            self.enable_controls('enabled')

            self.deiconify()

        else:
            tkinter.messagebox.showerror(title='Will Not Proceed',
                                         message='Finding outcomes requires at least three words.'
                                                 '\nFor outcome of 2, E(G) is 1.5 when the guess is from the list.'
                                                 '\nOtherwise E(G) is 2.'
                                         )
            return

    def enable_controls(self, look: str) -> None:
        self.button_process.configure(look)
        self.set_optimal_options_look(look)
        self.set_vocab_look(look)

    def set_optimal_options_look(self, look: str) -> None:
        self.chk_outcms_disp.configure(state=look)
        self.chk_ent_disp.configure(state=look)
        self.chk_outcms_disp_cond.configure(state=look)
        self.chk_keyed_outcms_disp.configure(state=look)

    def set_vocab_look(self, look: str) -> None:
        self.rbrA.configure(state=look)
        self.rbrB.configure(state=look)
        self.rbrBB.configure(state=look)
        self.rbrC.configure(state=look)

    def report_results(self, this_lst: list, optimal_outcome_guesses: dict, cond_mode=False) -> None:
        """
        Fills the results status CustomText with the results. And highlights the
        words in the to-be-examined words list if they are optimal.
        @param this_lst: The list of words that will be drilled for guess outcomes
        @param optimal_outcome_guesses: The dictionary of optimal words.
        """
        # The words in common will be highlighted.
        words_in_common = list(set(this_lst) & set(optimal_outcome_guesses))
        regex: str = '|'.join(words_in_common)
        wrds = hlp.opt_wrds_for_reporting(optimal_outcome_guesses, cond_mode)
        self.tx_status.configure(state='normal')
        self.tx_status.delete("1.0", "end")
        self.tx_status.insert('end', '> >  {} submitted words'.format(len(this_lst)))
        if len(words_in_common) > 0:
            self.tx_status.insert('end', self.common_msg)
        self.tx_status.insert('end', hlp.outcomes_stats_summary_line(optimal_outcome_guesses))
        self.tx_status.insert('end', wrds)
        self.tx_status.see('1.0')
        if self.d_ent_outcms.get():
            self.tx_status.highlight_pattern(regex, 'ent', remove_priors=False, do_scroll=False)
        else:
            self.tx_status.highlight_pattern(regex, 'out', remove_priors=False, do_scroll=False)
        self.tx_status.configure(state='disabled')

    def clear_list(self):
        self.outcms_words_text.set('')
        self.set_default_status_msg()
        self.entry_find.focus()

    def clear_and_paste(self):
        self.set_default_status_msg()
        self.entry_find.focus()
        ntext = ''
        try:
            ntext = self.clipboard_get()
        except tkinter.TclError:
            tkinter.messagebox.showerror(title='Clipboard Is Empty',
                                         message='\nThere is nothing to paste.'
                                                 '\nFirst copy an outcome. Then use this. The clipboard will '
                                                 'be empty afterwards.'
                                         )
            return
        finally:
            self.clipboard_clear()
            if ntext:
                self.outcms_words_text.set(ntext)
                self.just_clean_list()

    def set_default_status_msg(self):
        self.tx_status.configure(state='normal')
        self.tx_status.replace('1.0', 'end', self.def_msg)
        self.tx_status.configure(state='disabled')

    def set_busy_status_msg(self):
        self.tx_status.configure(state='normal')
        self.tx_status.replace('1.0', 'end', 'Busy, please wait ...')
        self.tx_status.configure(state='disabled')

    def set_clean_status_msg(self, this_lst: list[str]):
        self.tx_status.configure(state='normal')
        self.tx_status.delete("1.0", "end")
        self.tx_status.insert('end', '> >  {} words ready'.format(len(this_lst)))
        self.tx_status.configure(state='disabled')

    def title_status(self):
        match self.outcms_guess_source.get():
            case 0:
                self.title("Outcome Drilling Using The Words Entered List For Guesses")
            case 1:
                self.title("Outcome Drilling Using The Classic Vocabulary For Guesses")
            case 2:
                self.title("Outcome Drilling Using The Classic+ Vocabulary For Guesses")
            case 3:
                self.title("Outcome Drilling Using The Large Vocabulary For Guesses")
            case _:
                pass
        # Focus is most likely best at the entry field.
        self.entry_find.focus()

    def verbose_chk(self):
        if not self.d_verbose_outcms.get():
            self.d_verbose_outcms_cond.set(False)
            self.d_keyed_verbose_outcms.set(False)

    def condensed_chk(self):
        if not self.d_verbose_outcms.get():
            self.d_verbose_outcms.set(self.d_verbose_outcms_cond.get())

    def keyed_chk(self):
        self.d_verbose_outcms.set(self.d_keyed_verbose_outcms.get())

    def on_list_entry_return_release(self, _):
        self.just_clean_list()

    def just_clean_list(self):
        (entry_status, this_lst, bads) = self.clean_the_outcm_list()
        if not entry_status:
            self.update()
            tkinter.messagebox.showerror(title='Entry Will Not Be Processed',
                                         message='\nOnly five letter words allowed.'
                                                 '\nCheck the entry for:'
                                                 '\n{}'.format(str(bads)[1:-1])
                                         )
        else:
            self.set_clean_status_msg(this_lst)
            pass
        self.focus()
        self.entry_find.focus()

    def __init__(self):
        super().__init__()
        self.title("Outcome Drilling Using The Large Vocabulary")
        w_width = 1120
        w_height = 200
        pos_x = int(self.winfo_screenwidth() / 2 - w_width / 2)
        pos_y = int(self.winfo_screenheight() / 3 - w_height / 2)
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))

        # set the Vars
        self.outcms_words_text = tk.StringVar()
        self.outcms_guess_source = tk.IntVar(value=0)
        self.d_verbose_outcms = tk.BooleanVar(value=False)
        self.d_ent_outcms = tk.BooleanVar(value=False)
        self.d_keyed_verbose_outcms = tk.BooleanVar(value=False)
        self.d_verbose_outcms_cond = tk.BooleanVar(value=False)
        self.d_letter_use_disp = tk.BooleanVar(value=False)
        self.d_meta_lr = False

        # configure style
        style = ttk.Style()
        style.theme_use()
        font_tuple_n = ("Courier", 12, "normal")
        self.option_add("*Font", font_tuple_n)

        # Set meta left pressed flag used for clue type tally count
        # in condensed output.
        def key_handler_meta_lr(e):
            self.d_meta_lr = True

        self.bind('<Meta_L>', key_handler_meta_lr)
        self.bind('<Meta_R>', key_handler_meta_lr)

        # controls frame
        self.cnt_frame = ctk.CTkFrame(self,
                                      corner_radius=10
                                      )
        self.cnt_frame.pack(fill="x", padx=8, pady=2)

        # controls

        self.bts_frame = ctk.CTkFrame(self.cnt_frame,
                                      corner_radius=10
                                      )
        self.bts_frame.pack(fill="x", padx=0, pady=2)

        self.entry_find = ctk.CTkEntry(self.bts_frame,
                                       textvariable=self.outcms_words_text
                                       )
        self.entry_find.pack(side="left", padx=10, pady=6, expand=1, fill="x")
        self.entry_find.bind("<KeyRelease-Return>", self.on_list_entry_return_release)

        self.button_close = ctk.CTkButton(self.bts_frame, text="Close",
                                          width=80, text_color="black",
                                          command=self.destroy)
        self.button_close.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # assign to closing button [X]

        self.button_process = ctk.CTkButton(self.bts_frame, text="Process",
                                            width=80, text_color="black",
                                            command=self.process_entry_list
                                            )
        self.button_process.pack(side="left", padx=10, pady=10)

        self.button_clear = ctk.CTkButton(self.bts_frame, text="Clear",
                                          width=40, text_color="black",
                                          command=self.clear_list
                                          )
        self.button_clear.pack(side="left", padx=6, pady=10)

        self.button_clear = ctk.CTkButton(self.bts_frame, text="Clear 'N Paste",
                                          width=40, text_color="black",
                                          command=self.clear_and_paste
                                          )
        self.button_clear.pack(side="left", padx=6, pady=10)

        # labelframe within outcomes frame for which list option
        self.outcm_lst_ops_frame = ttk.LabelFrame(self,
                                                  text='Vocabulary Source For Guess Outcome Words:',
                                                  labelanchor='w',
                                                  borderwidth=0
                                                  )
        self.outcm_lst_ops_frame.pack(side="top", padx=10, pady=4, fill="x")
        self.rbrA = ttk.Radiobutton(self.outcm_lst_ops_frame, text="Words Entered",
                                    variable=self.outcms_guess_source, value=0,
                                    command=self.title_status)
        self.rbrA.pack(side="left", fill="x", padx=6, pady=2)
        self.rbrB = ttk.Radiobutton(self.outcm_lst_ops_frame, text="Classic",
                                    variable=self.outcms_guess_source, value=1,
                                    command=self.title_status)
        self.rbrB.pack(side="left", fill="x", padx=6, pady=2)
        self.rbrBB = ttk.Radiobutton(self.outcm_lst_ops_frame, text="Classic+",
                                     variable=self.outcms_guess_source, value=2,
                                     command=self.title_status)
        self.rbrBB.pack(side="left", fill="x", padx=6, pady=2)
        self.rbrC = ttk.Radiobutton(self.outcm_lst_ops_frame, text="Large",
                                    variable=self.outcms_guess_source, value=3,
                                    command=self.title_status)
        self.rbrC.pack(side="left", fill="x", padx=6, pady=2)

        # Show Keyed Report checkbox
        self.chk_keyed_outcms_disp = ttk.Checkbutton(self.outcm_lst_ops_frame,
                                                     text="Keyed",
                                                     variable=self.d_keyed_verbose_outcms,
                                                     onvalue=True,
                                                     offvalue=False,
                                                     command=self.keyed_chk
                                                     )
        self.chk_keyed_outcms_disp.pack(side="right", padx=10, pady=2)

        # Show Condensed Report checkbox
        self.chk_outcms_disp_cond = ttk.Checkbutton(self.outcm_lst_ops_frame,
                                                    text="Cond",
                                                    variable=self.d_verbose_outcms_cond,
                                                    onvalue=True,
                                                    offvalue=False,
                                                    command=self.condensed_chk
                                                    )
        self.chk_outcms_disp_cond.pack(side="right", padx=10, pady=2)

        # Show Entropy Report checkbox
        self.chk_ent_disp = ttk.Checkbutton(self.outcm_lst_ops_frame,
                                            text="Entropy",
                                            variable=self.d_ent_outcms,
                                            onvalue=True,
                                            offvalue=False
                                            )
        self.chk_ent_disp.pack(side="right", padx=10, pady=2)

        # Show Verbose Report checkbox
        self.chk_outcms_disp = ttk.Checkbutton(self.outcm_lst_ops_frame,
                                               text="Verbose",
                                               variable=self.d_verbose_outcms,
                                               onvalue=True,
                                               offvalue=False,
                                               command=self.verbose_chk
                                               )
        self.chk_outcms_disp.pack(side="right", padx=10, pady=2)

        # end labelframe within outcomes frame for which list option

        # status frame
        self.stat_frame = ctk.CTkFrame(self,
                                       corner_radius=10
                                       )
        self.stat_frame.pack(fill="both", padx=8, pady=2, expand=True)

        # status line
        self.tx_status = hlp.CustomText(self.stat_frame,
                                            wrap='word',
                                            background='#dedede',
                                            borderwidth=0,
                                            height=10,
                                            highlightthickness=0)
        self.tx_status.pack(side="left", anchor="nw", padx=10, pady=4, expand=True, fill="both")
        # The CustomText class is a tk.Text extended to support a color for matched text.
        # #c6e2ff = red 198, green 226, blue 255 => a light blue, www.color-hex.com
        # tag 'out' is used to highlight outcome ranker
        self.tx_status.tag_configure('out', background='#fff69a')
        # tag 'ent' is used to highlight entropy pick
        self.tx_status.tag_configure('ent', background='#ffd700')

        self.tx_status.insert('1.0', self.def_msg)
        # scrollbar for tx_status
        self.tx_status_sb = ttk.Scrollbar(self.stat_frame, orient='vertical')
        self.tx_status_sb.pack(side="right", fill="y")
        self.tx_status.config(yscrollcommand=self.tx_status_sb.set)
        self.tx_status_sb.config(command=self.tx_status.yview)
        # Respond to initial state
        self.title_status()

# end OutcmsDrillingMain class


def mainloop(_args=None):
    drill_app: OutcmsDrillingMain = OutcmsDrillingMain()
    drill_app.mainloop()


# ====================================== main ================================================
if __name__ == '__main__':
    mainloop()
