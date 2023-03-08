import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
from typing import NoReturn
import customtkinter as ctk
import helpers

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
                                                                    all_targets)
    return optimal_group_guesses


class GrpsDrillingMain(ctk.CTk):
    def close_rpt(self) -> NoReturn:
        self.destroy()

    def clean_grp_list(self):
        this_grp = self.grp_words_text.get()
        # A paste from a spreadsheet row will be tab deliniated.
        # Its newline character will be stripped later on.
        this_grp = this_grp.replace('\t', ',')
        # Strip unwanted characters that might be.
        this_lst = [x.strip(' ,\"\'\n:;0123456789()[]') for x in this_grp.split(',')]
        # Remove any empty strings from list.
        this_lst = [i for i in this_lst if i]
        self.grp_words_text.set(', '.join(this_lst))
        if len(this_lst) > 2:
            self.title("> > > ... Busy, Please Wait ... < < <")
            self.update()
            process_grp_list(this_lst)
            self.title("Groups Drilling")

    def clear_list(self):
        self.grp_words_text.set('')

    def __init__(self):
        super().__init__()
        self.title("Groups Drilling")
        w_width = 1120
        w_height = 100
        pos_x = int(self.winfo_screenwidth() / 2 - w_width / 2)
        pos_y = int(self.winfo_screenheight() / 3 - w_height / 2)
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))

        # set the Vars
        self.grp_words_text = tk.StringVar()

        # configure style
        style = ttk.Style()
        style.theme_use()

        # controls
        button_q = ctk.CTkButton(self, text="Close",
                                 width=80,
                                 command=self.destroy)
        button_q.pack(side="right", padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # assign to closing button [X]

        entry_find = ctk.CTkEntry(self,
                                  textvariable=self.grp_words_text,
                                  )
        entry_find.pack(side=tk.LEFT, padx=10, pady=10, expand=1, fill=tk.X)

        button_f = ctk.CTkButton(self, text="Process",
                                 width=80,
                                 command=self.clean_grp_list
                                 )
        button_f.pack(side="left", padx=0, pady=10)

        button_f = ctk.CTkButton(self, text="Clear",
                                 width=40,
                                 command=self.clear_list
                                 )
        button_f.pack(side="left", padx=6, pady=10)


# end GrpsDrillingMain class

def drilling():
    drill_app: GrpsDrillingMain = GrpsDrillingMain()
    drill_app.mainloop()


drill_app: GrpsDrillingMain = GrpsDrillingMain()
drill_app.mainloop()
