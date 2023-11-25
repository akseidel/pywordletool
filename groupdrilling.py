# ----------------------------------------------------------------
# groupdrilling akseidel 2/2023
# ----------------------------------------------------------------
import tkinter as tk  # assigns tkinter stuff to tk namespace so that
# it may be separate from ttk
import tkinter.messagebox
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk
# namespace so that tk is preserved
from typing import NoReturn
import customtkinter as ctk
import helpers
import re

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

data_path = 'worddata/'  # path from here to data folder
letter_rank_file = 'letter_ranks.txt'


def process_grp_list(self, g_word_lst: list) -> dict:
    # Flag to use various solutions as guesses instead of the current displayed word list.
    # This is allows the option to group rank from the entire guess list.
    grps_guess_source = self.grps_guess_source.get()
    optimal_group_guesses = {}
    context = 'Groups Drilling'
    match grps_guess_source:
        case 0:
            optimal_group_guesses = helpers.best_groups_guess_dict(g_word_lst,
                                                                   self.d_verbose_grps.get(),
                                                                   self.d_verbose_grps_cond.get(),
                                                                   context
                                                                   )

        case 1:
            # get the entire possible solutions list
            all_targets = helpers.ToolResults(data_path,
                                              'wo_nyt_wordlist.txt',
                                              letter_rank_file,
                                              True,
                                              0).get_ranked_results_wrd_lst(True)
            msg1 = 'Classic Vocabulary'
            optimal_group_guesses = helpers.extended_best_groups_guess_dict(g_word_lst,
                                                                            self.d_verbose_grps.get(),
                                                                            self.d_verbose_grps_cond.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context
                                                                            )
        case 2:
            # get the entire possible guess list
            all_targets = helpers.ToolResults(data_path,
                                              'botadd_nyt_wordlist.txt',
                                              letter_rank_file,
                                              True, 0).get_ranked_results_wrd_lst(True)
            msg1 = 'Classic+ Vocabulary'
            optimal_group_guesses = helpers.extended_best_groups_guess_dict(g_word_lst,
                                                                            self.d_verbose_grps.get(),
                                                                            self.d_verbose_grps_cond.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context
                                                                            )
        case 3:
            # get the entire possible guess list
            all_targets = helpers.ToolResults(data_path,
                                              'nyt_wordlist.txt',
                                              letter_rank_file,
                                              True, 0).get_ranked_results_wrd_lst(True)
            msg1 = 'Large Vocabulary'
            optimal_group_guesses = helpers.extended_best_groups_guess_dict(g_word_lst,
                                                                            self.d_verbose_grps.get(),
                                                                            self.d_verbose_grps_cond.get(),
                                                                            all_targets,
                                                                            msg1,
                                                                            context
                                                                            )
        case _:
            pass

    return optimal_group_guesses


class GrpsDrillingMain(ctk.CTkToplevel):
    common_msg = '\n> >  Highlighted words are common to both the entry words and the optimal group guess words.'
    def_msg = 'Paste or write in the words list into the above entry field.' + \
              '\n\nRaw pastes from the This Wordle Helper will be automatically cleaned and converted to ' + \
              'a valid word list entry.'

    def close_rpt(self) -> NoReturn:
        self.destroy()

    def clean_the_grp_list(self) -> tuple[bool, list[str], list[str]]:
        """
        Processes what was pasted into the word list entry into a proper looking list of
        five letter words. The intent is to be able to paste raw text copied out of the Helper's
        list window, raw text copied from a Groups Driller output and other copied text sources like
        spreadsheet ranges. Numbers, spaces, punctuation, non-alphabet characters and line feeds
        are to be removed.
        @return: a tuple containing Status, the list of five letter words , the list of invalid words.
        """
        this_grp = self.grp_words_text.get()
        # First strip out numbers, like those that are rankings from
        # the wordle helper and other characters.
        this_grp = re.sub('[-:;.0123456789()~!@#$%^&*+_|?><`/{}]', '', this_grp).lower()
        # Let spaces comma separate the words. Commas will be used in a
        # later strip function that operates on section split by comma.
        # Empty words will be culled later on.
        this_grp = this_grp.replace(' ', ',')
        # A paste from a spreadsheet row will be tab deliniated.
        this_grp = this_grp.replace('\t', ',')
        # Handling the newline characters.
        this_grp = this_grp.replace('\n', ',')
        # Strip unwanted characters that might be.
        this_lst = [x.strip(' ,[]\"\'\n') for x in this_grp.split(',')]
        # Remove any empty strings from list.
        this_lst = [i for i in this_lst if i]
        self.grp_words_text.set(', '.join(this_lst))

        status = True
        bads = []
        for w in this_lst:
            if len(w) != 5:
                status = False
                bads.append(w)
        return status, this_lst, bads

    def process_entry_list(self):
        (entry_status, this_lst, bads) = self.clean_the_grp_list()
        if not entry_status:
            self.update()
            tkinter.messagebox.showerror(title='Will Not Proceed',
                                         message='Not proceeding.\nOnly five letter words allowed.'
                                         )
            return
        if len(this_lst) > 2:
            self.title("> > > ... Busy, Please Wait ... < < <")
            self.set_busy_status_msg()
            self.button_process.configure(state='disabled')
            self.update()
            optimal_group_guesses = process_grp_list(self, this_lst)
            # Report the results
            self.report_results(this_lst, optimal_group_guesses)
            self.title("Groups Drilling")
            self.button_process.configure(state='enabled')

            self.deiconify()

        else:
            tkinter.messagebox.showerror(title='Will Not Proceed',
                                         message='Finding groups requires at least three words.'
                                                 '\nFor group of 2, E(G) is 1.5 when the guess is from the list.'
                                                 '\nOtherwise E(G) is 2.'
                                         )
            return

    def report_results(self, this_lst: list, optimal_group_guesses: dict) -> NoReturn:
        # The words in common will be highlighted.
        words_in_common = list(set(this_lst) & set(optimal_group_guesses))
        regex: str = '|'.join(words_in_common)
        wrds = helpers.opt_wrds_for_reporting(optimal_group_guesses)
        self.tx_status.configure(state='normal')
        self.tx_status.delete("1.0", "end")
        self.tx_status.insert('end', '> >  {} submitted words'.format(len(this_lst)))
        if len(words_in_common) > 0:
            self.tx_status.insert('end', self.common_msg)
        self.tx_status.insert('end', helpers.groups_stats_summary_line(optimal_group_guesses))
        self.tx_status.insert('end', wrds)
        self.tx_status.see('1.0')
        self.tx_status.highlight_pattern(regex, 'grp', remove_priors=False, do_scroll=False)
        self.tx_status.configure(state='disabled')

    def clear_list(self):
        self.grp_words_text.set('')
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
                                                 '\nFirst copy a group. Then use this. The clipboard will '
                                                 'be empty afterwards.'
                                         )
            return
        finally:
            self.clipboard_clear()
            if ntext:
                self.grp_words_text.set(ntext)
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
        match self.grps_guess_source.get():
            case 0:
                self.title("Groups Drilling Using The Words Entered List For Guesses")
            case 1:
                self.title("Groups Drilling Using The Classic Vocabulary For Guesses")
            case 2:
                self.title("Groups Drilling Using The Classic+ Vocabulary For Guesses")
            case 3:
                self.title("Groups Drilling Using The Large Vocabulary For Guesses")
            case _:
                pass
        # Focus is most likely best at the entry field.
        self.entry_find.focus()

    def verbose_chk(self):
        if self.d_verbose_grps_cond.get() and not self.d_verbose_grps.get():
            self.d_verbose_grps_cond.set(False)

    def condensed_chk(self):
        if self.d_verbose_grps_cond.get():
            self.d_verbose_grps.set(True)

    def on_list_entry_return_release(self, _):
        self.just_clean_list()

    def just_clean_list(self):
        (entry_status, this_lst, bads) = self.clean_the_grp_list()
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
        self.title("Groups Drilling Using The Large Vocabulary")
        w_width = 1120
        w_height = 200
        pos_x = int(self.winfo_screenwidth() / 2 - w_width / 2)
        pos_y = int(self.winfo_screenheight() / 3 - w_height / 2)
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))

        # set the Vars
        self.grp_words_text = tk.StringVar()
        self.grps_guess_source = tk.IntVar(value=0)
        self.d_verbose_grps = tk.BooleanVar(value=True)
        self.d_verbose_grps_cond = tk.BooleanVar(value=False)

        # configure style
        style = ttk.Style()
        style.theme_use()
        font_tuple_n = ("CourierNew", 14, "normal")

        # controls frame
        self.cnt_frame = ctk.CTkFrame(self,
                                      corner_radius=10,
                                      borderwidth=0
                                      )
        self.cnt_frame.pack(fill=tk.X, padx=8, pady=2)

        # controls

        self.bts_frame = ctk.CTkFrame(self.cnt_frame,
                                      corner_radius=10,
                                      borderwidth=0
                                      )
        self.bts_frame.pack(fill=tk.X, padx=0, pady=2)

        self.entry_find = ctk.CTkEntry(self.bts_frame,
                                       textvariable=self.grp_words_text
                                       )
        self.entry_find.pack(side=tk.LEFT, padx=10, pady=6, expand=1, fill=tk.X)
        self.entry_find.bind("<KeyRelease-Return>", self.on_list_entry_return_release)

        self.button_close = ctk.CTkButton(self.bts_frame, text="Close",
                                          width=80,
                                          command=self.destroy)
        self.button_close.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # assign to closing button [X]

        self.button_process = ctk.CTkButton(self.bts_frame, text="Process",
                                            width=80,
                                            command=self.process_entry_list
                                            )
        self.button_process.pack(side="left", padx=10, pady=10)

        self.button_clear = ctk.CTkButton(self.bts_frame, text="Clear",
                                          width=40,
                                          command=self.clear_list
                                          )
        self.button_clear.pack(side="left", padx=6, pady=10)

        self.button_clear = ctk.CTkButton(self.bts_frame, text="Clear 'N Paste",
                                          width=40,
                                          command=self.clear_and_paste
                                          )
        self.button_clear.pack(side="left", padx=6, pady=10)

        # labelframe within groups frame for which list option
        self.grp_lst_ops_frame = ttk.LabelFrame(self,
                                                text='Vocabulary Source For Guess Group Words:',
                                                labelanchor='w',
                                                borderwidth=0
                                                )
        self.grp_lst_ops_frame.pack(side=tk.TOP, padx=10, pady=4, fill=tk.X)
        self.rbrA = ttk.Radiobutton(self.grp_lst_ops_frame, text="Words Entered",
                                    variable=self.grps_guess_source, value=0,
                                    command=self.title_status)
        self.rbrA.pack(side=tk.LEFT, fill=tk.X, padx=6, pady=2)
        self.rbrB = ttk.Radiobutton(self.grp_lst_ops_frame, text="Classic",
                                    variable=self.grps_guess_source, value=1,
                                    command=self.title_status)
        self.rbrB.pack(side=tk.LEFT, fill=tk.X, padx=6, pady=2)
        self.rbrBB = ttk.Radiobutton(self.grp_lst_ops_frame, text="Classic+",
                                     variable=self.grps_guess_source, value=2,
                                     command=self.title_status)
        self.rbrBB.pack(side=tk.LEFT, fill=tk.X, padx=6, pady=2)
        self.rbrC = ttk.Radiobutton(self.grp_lst_ops_frame, text="Large",
                                    variable=self.grps_guess_source, value=3,
                                    command=self.title_status)
        self.rbrC.pack(side=tk.LEFT, fill=tk.X, padx=6, pady=2)

        # Show Condensed Report checkbox
        self.chk_grp_disp_cond = ttk.Checkbutton(self.grp_lst_ops_frame,
                                                 text="Condensed",
                                                 variable=self.d_verbose_grps_cond,
                                                 onvalue=True,
                                                 offvalue=False,
                                                 command=self.condensed_chk
                                                 )
        self.chk_grp_disp_cond.pack(side=tk.RIGHT, padx=10, pady=2)

        # Show Verbose Report checkbox
        self.chk_grp_disp = ttk.Checkbutton(self.grp_lst_ops_frame,
                                            text="Show Verbose Report",
                                            variable=self.d_verbose_grps,
                                            onvalue=True,
                                            offvalue=False,
                                            command=self.verbose_chk
                                            )
        self.chk_grp_disp.pack(side=tk.RIGHT, padx=10, pady=2)

        # end labelframe within groups frame for which list option

        # status frame
        self.stat_frame = ctk.CTkFrame(self,
                                       corner_radius=10,
                                       borderwidth=0
                                       )
        self.stat_frame.pack(fill=tk.BOTH, padx=8, pady=2, expand=True)

        # status line
        self.tx_status = helpers.CustomText(self.stat_frame,
                                            wrap='word',
                                            background='#dedede',
                                            borderwidth=0,
                                            height=10,
                                            highlightthickness=0)
        self.tx_status.pack(side="left", anchor=tk.NW, padx=10, pady=4, expand=True, fill=tk.BOTH)
        self.tx_status.configure(font=font_tuple_n)
        # The CustomText class is a tk.Text extended to support a color for matched text.
        # #c6e2ff = red 198, green 226, blue 255 => a light blue,  www.color-hex.com
        # tag 'grp' is used to highlight group ranker
        self.tx_status.tag_configure('grp', background='#ffd700')
        self.tx_status.insert('1.0', self.def_msg)
        # scrollbar for tx_status
        self.tx_status_sb = ttk.Scrollbar(self.stat_frame, orient='vertical')
        self.tx_status_sb.pack(side="right", fill=tk.Y)
        self.tx_status.config(yscrollcommand=self.tx_status_sb.set)
        self.tx_status_sb.config(command=self.tx_status.yview)
        # Respond to initial state
        self.title_status()


# end GrpsDrillingMain class


def mainloop(args=None):
    drill_app: GrpsDrillingMain = GrpsDrillingMain()
    drill_app.mainloop()


# ====================================== main ================================================
if __name__ == '__main__':
    mainloop()
