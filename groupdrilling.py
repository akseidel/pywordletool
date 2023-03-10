import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.messagebox
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
from typing import NoReturn
import customtkinter as ctk
import helpers
import re

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

data_path = 'worddata/'  # path from here to data folder
letter_rank_file = 'letter_ranks.txt'


def process_grp_list(g_word_lst: list) -> dict:
    all_targets = helpers.ToolResults(data_path,
                                      'nyt_wordlist.txt',
                                      letter_rank_file,
                                      True,
                                      0).get_ranked_results_wrd_lst(True)

    optimal_group_guesses = helpers.extended_best_groups_guess_dict(g_word_lst,
                                                                    True,
                                                                    all_targets,
                                                                    'Large Vocabulary')
    return optimal_group_guesses


class GrpsDrillingMain(ctk.CTk):
    common_msg = '> >  Highlighted words are common to both the entry words and the optimal group guess words.'
    def_msg = 'Paste or write in the words list into the above entry field.' + \
              '\n\nRaw pastes from the This Wordle Helper will be automatically cleaned and converted to ' + \
              'a valid word list entry.'

    def close_rpt(self) -> NoReturn:
        self.destroy()

    def clean_the_grp_list(self) -> tuple:
        this_grp = self.grp_words_text.get()
        # First strip out numbers, like those that are rankings from
        # the wordle helper.
        this_grp = re.sub('[-:;.0123456789()]', '', this_grp).lower()
        # Let spaces comma separate the words. Commas will be used in a
        # later strip function that operates on section split by comma.
        # Empty words will be culled later on.
        this_grp = this_grp.replace(' ', ',')
        # A paste from a spreadsheet row will be tab deliniated.
        # Its newline character will be stripped later on.
        this_grp = this_grp.replace('\t', ',')
        # Strip unwanted characters that might be.
        this_lst = [x.strip(' ,[]\"\'\n') for x in this_grp.split(',')]
        # Remove any empty strings from list.
        this_lst = [i for i in this_lst if i]
        self.grp_words_text.set(', '.join(this_lst))

        status = True
        for w in this_lst:
            if len(w) != 5:
                status = False
        return status, this_lst

    def process_entry_list(self):
        entry_status = self.clean_the_grp_list()
        if not entry_status[0]:
            self.update()
            tkinter.messagebox.showerror(title='Will Not Proceed', message='Not proceeding.\nOnly five letter words '
                                                                           'allowed.')
            return
        this_lst = entry_status[1]
        if len(this_lst) > 2:
            self.title("> > > ... Busy, Please Wait ... < < <")
            self.set_busy_status_msg()
            self.update()
            optimal_group_guesses = process_grp_list(this_lst)
            self.title("Groups Drilling")
        else:
            tkinter.messagebox.showerror(title='Will Not Proceed', message='Three or more words are needed for finding'
                                                                           ' groups.')
            return
        # Common words will be highlighted.
        words_in_common = list(set(this_lst) & set(optimal_group_guesses))
        regex: str = '|'.join(words_in_common)
        wrds = helpers.opt_wrds_for_reporting(optimal_group_guesses)
        self.tx_status.delete("1.0", "end")
        if len(words_in_common) > 0:
            self.tx_status.insert('end', self.common_msg)
        self.tx_status.insert('end', wrds)
        self.tx_status.see('1.0')
        self.tx_status.highlight_pattern(regex, 'grp', remove_priors=False)

    def clear_list(self):
        self.grp_words_text.set('')
        self.set_default_status_msg()

    def set_default_status_msg(self):
        self.tx_status.replace('1.0', 'end', self.def_msg)

    def set_busy_status_msg(self):
        self.tx_status.replace('1.0', 'end', 'Busy, please wait ...')

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

        # configure style
        style = ttk.Style()
        style.theme_use()
        font_tuple_n = ("Courier", 14, "normal")

        # controls frame
        self.cnt_frame = ctk.CTkFrame(self,
                                      corner_radius=10,
                                      borderwidth=0
                                      )
        self.cnt_frame.pack(fill=tk.X, padx=8, pady=2)

        # controls
        self.button_q = ctk.CTkButton(self.cnt_frame, text="Close",
                                      width=80,
                                      command=self.destroy)
        self.button_q.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # assign to closing button [X]

        self.entry_find = ctk.CTkEntry(self.cnt_frame,
                                       textvariable=self.grp_words_text,
                                       )
        self.entry_find.pack(side=tk.LEFT, padx=10, pady=10, expand=1, fill=tk.X)

        self.button_f = ctk.CTkButton(self.cnt_frame, text="Process",
                                      width=80,
                                      command=self.process_entry_list
                                      )
        self.button_f.pack(side="left", padx=0, pady=10)

        self.button_f = ctk.CTkButton(self.cnt_frame, text="Clear",
                                      width=40,
                                      command=self.clear_list
                                      )
        self.button_f.pack(side="left", padx=6, pady=10)

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


# end GrpsDrillingMain class

def drilling():
    drill_app: GrpsDrillingMain = GrpsDrillingMain()
    drill_app.mainloop()


drill_app: GrpsDrillingMain = GrpsDrillingMain()
drill_app.mainloop()
