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
# get customtkinter  -> pip3 install customtkinter
# if already  present, you may need to upgrade it -> pip3 install customtkinter --upgrade
# Hopefully the upgrade does not break this code.
#
import os
import helpers

import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
import customtkinter as ctk

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

# globals
data_path = 'worddata/'  # path from here to data folder
help_showing = False  # flag indicating help window is open
x_pos_dict = {}  # exclude position dictionary
r_pos_dict = {}  # require position dictionary
font_tuple = ("Courier", 14, "normal")


def set_n_col(self):
    if self.winfo_screenwidth() > 1280:  # to do
        return 9
    else:
        return 6


def str_wrd_list_hrd(ln_col):
    """Creates the word list header line.
    """
    h_txt = " Word : Rank "
    left_pad = ""
    mid_pad = "  "
    h_line = left_pad + h_txt
    for i in range(1, ln_col):
        h_line = h_line + mid_pad + h_txt
    return h_line


# return a reformatted string with wordwrapping
# @staticmethod
def wrap_this(string, max_chars):
    """A helper that will return the string with word-break wrapping.
            :param str string: The text to be wrapped.
            :param int max_chars: The maximum number of characters on a line before wrapping.
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


class Pywordlemainwindow(ctk.CTk):
    """The pywordletool application GUI window
    """
    global x_pos_dict
    global r_pos_dict

    def close_help(self):
        global help_showing
        self.wnd_help.destroy()
        help_showing = False

    def show_help(self):
        global help_showing
        global this_app
        if help_showing is False:
            self.create_wnd_help()
            help_showing = True
        else:
            self.wnd_help.destroy()
            self.create_wnd_help()

    # ======== set exclude combos to treeview selection
    def x_pos_tree_view_click(self, event):
        cur_item = self.treeview_px.focus()
        val_tup = self.treeview_px.item(cur_item).get('values')
        if val_tup != '':
            self.pos_px_l.set(val_tup[0])
            self.pos_px_p.set(val_tup[1])

    # ======== set require combos to treeview selection
    def r_pos_tree_view_click(self, event):
        cur_item = self.treeview_pr.focus()
        val_tup = self.treeview_pr.item(cur_item).get('values')
        if val_tup != '':
            self.pos_pr_l.set(val_tup[0])
            self.pos_pr_p.set(val_tup[1])

    def __init__(self):
        super().__init__()
        self.wnd_help = None
        self.title("This Wordle Helper")
        # print(self.winfo_screenheight())
        # print(self.winfo_screenwidth())
        w_width = 1120  # 1036
        w_height = 664  # to do, set according to screen height
        pos_x = int(self.winfo_screenwidth() / 2 - w_width / 2)
        pos_y = int(self.winfo_screenheight() / 3 - w_height / 2)
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))
        # self.resizable(width=False,height=False)

        ln_col = set_n_col(self)
        # set the Vars
        self.no_dups = tk.BooleanVar()
        self.no_dupe_state = tk.StringVar()
        self.no_dupe_state.set("on")
        self.vocabulary = tk.StringVar()
        self.status = tk.StringVar()

        # configure style
        style = ttk.Style()
        style.theme_use('aqua')

        def do_grep():
            """Runs a wordletool helper grep instance
            """
            global data_path

            if sw_no_dups.get() == "on":
                no_dups = False
            else:
                no_dups = True

            if self.vocabulary.get() == "Use Small Vocabulary":
                vocab_filename = 'wo_nyt_wordlist.txt'
            else:
                vocab_filename = 'nyt_wordlist.txt'

            wordletool = helpers.ToolResults(data_path, vocab_filename, 'letter_ranks.txt', no_dups)

            wordletool.tool_command_list.add_cmd(build_exclude_grep(self.ex_btn_vars))
            wordletool.tool_command_list.add_cmd(build_requireall_grep(self.re_btn_vars))
            build_x_pos_grep(wordletool, x_pos_dict)
            build_r_pos_grep(wordletool, r_pos_dict)

            tx_result.delete(1.0, tk.END)

            the_word_list = wordletool.get_ranked_results_wrd_lst()

            n_items = len(the_word_list)
            left_pad = ""
            mid_pad = "  "
            c = 0
            i = 0
            l_msg = ""
            for key, value in the_word_list.items():
                msg = key + " : " + str(value)
                i = i + 1
                if c == 0:
                    l_msg = left_pad + msg
                else:
                    l_msg = l_msg + mid_pad + msg
                c = c + 1
                if c == ln_col:
                    tx_result.insert(tk.END, l_msg + '\n')
                    c = 0
                    l_msg = ""
                if i == n_items:
                    tx_result.insert(tk.END, l_msg + '\n')

            tx_result.see('end')
            self.status.set(wordletool.show_status())
            tx_gr.delete(1.0, tk.END)
            tx_gr.insert(tk.END, wordletool.show_cmd())

        # obviously do not have a clue why I had to resort to this.
        def callback_do_grep(def_self):
            do_grep()

        def add_x_pos():
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

        def add_r_pos():
            x_ltr = self.pos_pr_l.get().upper()
            x_pos = self.pos_pr_p.get()
            if not x_pos.isnumeric() or int(x_pos) < 1 or int(x_pos) > 5:
                self.pos_pr_p.set('1')
                return
            if x_ltr == '' or len(x_ltr) > 1 or x_ltr.isnumeric():
                self.pos_pr_l.set('')
                return
            self.pos_pr_l.set(x_ltr)
            key = x_ltr + ',' + x_pos
            value = key
            r_pos_dict[key] = value
            fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)

        def remove_x_pos():
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

        def clearall_x_pos():
            x_pos_dict.clear()
            fill_treeview_per_dictionary(self.treeview_px, x_pos_dict, 0)
            self.combo_px_l.current(0)
            self.combo_px_p.current(0)

        def remove_r_pos():
            x_ltr = self.pos_pr_l.get().upper()
            x_pos = self.pos_pr_p.get()
            if x_ltr == '' or len(x_ltr) > 1 or x_ltr.isnumeric():
                self.pos_pr_l.set('')
                return
            self.pos_pr_l.set(x_ltr)
            key = x_ltr + ',' + x_pos
            if key in r_pos_dict:
                del r_pos_dict[key]
                fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)

        def clearall_r_pos():
            r_pos_dict.clear()
            fill_treeview_per_dictionary(self.treeview_pr, r_pos_dict, 1)
            self.combo_pr_l.current(0)
            self.combo_pr_p.current(0)

        # clears all settings
        def clear_all():
            clearall_r_pos()
            clearall_x_pos()
            clear_excl_ckbs()
            clear_reqr_ckbs()

        # Clears and fills a treeview with dictionary contents
        # Results are sorted by the dictionary keys.
        # bywhat indicated by key 0 or by value 1 so that the required position
        # list sorts by the position while the excluded position list sorts by
        # the letter.
        def fill_treeview_per_dictionary(this_treeview, this_pos_dict, bywhat):
            for i in this_treeview.get_children():
                this_treeview.delete(i)
            i = 0
            sort_by_what_dict = {}
            if bywhat == 0:
                for j in sorted(this_pos_dict):
                    sort_by_what_dict[j] = this_pos_dict[j]
            if bywhat == 1:
                tlist = sorted(this_pos_dict.items(), key=lambda lx: lx[1].split(',')[1])
                sort_by_what_dict = dict(tlist)
            for x in sort_by_what_dict:
                parts = this_pos_dict[x].split(',')
                this_treeview.insert(parent='', index=i, id=i, values=parts)
                i += 1
            do_grep()

        def build_exclude_grep(ex_btn_var_list):
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

        def build_x_pos_grep(lself, this_pos_dict):
            """Builds the grep line for excluding positions
            """
            # example 'grep -vE \'..b..\'' for b,3
            sort_by_key_dict = {}
            for j in sorted(this_pos_dict):
                sort_by_key_dict[j] = this_pos_dict[j]
            for x in sort_by_key_dict:
                parts = this_pos_dict[x].split(',')
                ltr = parts[0].lower()
                p = int(parts[1])
                lself.tool_command_list.add_excl_pos_cmd(ltr, p)

        def build_r_pos_grep(lself, this_pos_dict):
            """Builds the grep line for including positions
            """
            # example 'grep -vE \'..b..\'' for b,3
            sort_by_key_dict = {}
            for j in sorted(this_pos_dict):
                sort_by_key_dict[j] = this_pos_dict[j]
            for x in sort_by_key_dict:
                parts = this_pos_dict[x].split(',')
                ltr = parts[0].lower()
                p = int(parts[1])
                lself.tool_command_list.add_incl_pos_cmd(ltr, p)

        def build_requireall_grep(re_btn_var_list):
            """Builds the grep line for requiring letters
            """
            # example 'grep -E \'b|f|k|w\''
            grep_requireall = ""
            pipe = "|"
            itms = []
            for b in re_btn_var_list:
                ltr = b.get()
                if ltr != '-':
                    itms.append("grep -E \'" + ltr + "\'")
            args = pipe.join(itms)
            if len(itms) > 0:
                grep_requireall = args
            return grep_requireall

        # upper frame showing the words
        self.result_frame = ctk.CTkFrame(self,
                                         corner_radius=10,
                                         borderwidth=0)
        self.result_frame.pack(padx=10, pady=2, fill=tk.X)
        self.result_frame.grid_columnconfigure(0, weight=1)  # non-zero weight allows grid to expand
        # the header line above the word list
        lb_result_hd = tk.Label(self.result_frame,
                                text=str_wrd_list_hrd(ln_col),
                                relief='sunken',
                                background='#dedede',
                                anchor='w',
                                borderwidth=0,
                                highlightthickness=0)
        lb_result_hd.grid(row=0, column=0, columnspan=4, sticky='ew', padx=6, pady=2)
        lb_result_hd.configure(font=font_tuple)
        # the word list resulting from grep on the main wordlist
        tx_result = tk.Text(self.result_frame,
                            wrap='word',
                            background='#dedede',
                            borderwidth=0,
                            highlightthickness=0)
        tx_result.grid(row=1, column=0, columnspan=4, sticky='ew', padx=6, pady=4)
        if self.winfo_screenheight() <= 800:
            tx_result.configure(height=12)  # to do, set according to screen height
        else:
            tx_result.configure(height=16)
        tx_result.configure(font=font_tuple)
        # scrollbar for wordlist
        tx_results_sb = ttk.Scrollbar(self.result_frame, orient='vertical')
        tx_results_sb.grid(row=1, column=5, sticky='ens')
        tx_result.config(yscrollcommand=tx_results_sb.set)
        tx_results_sb.config(command=tx_result.yview)

        lb_status = tk.Label(self.result_frame,
                             textvariable=self.status,
                             background='#dedede',
                             borderwidth=0,
                             highlightthickness=0)
        lb_status.grid(row=2, rowspan=1, column=0, columnspan=4, sticky='ew', padx=6, pady=4)
        lb_status.configure(font=font_tuple)
        self.status.set('=> No status yet.')

        # grep line being used
        tx_gr = tk.Text(self.result_frame,
                        wrap='word',
                        height=2,
                        background='#dedede',
                        borderwidth=0,
                        highlightthickness=0)
        tx_gr.grid(row=4, column=0, columnspan=4, sticky='ew', padx=6, pady=4)
        tx_gr.configure(font=font_tuple)
        tx_gr.delete(1.0, tk.END)
        # scrollbar for grep line
        tx_gr_sb = ttk.Scrollbar(self.result_frame, orient='vertical')
        tx_gr_sb.grid(row=4, column=5, sticky='ens', pady=4)
        tx_gr.config(yscrollcommand=tx_gr_sb.set)
        tx_gr_sb.config(command=tx_gr.yview)

        # grep criteria outer frame holding:
        # letter require frame
        # letter exclusion frame
        # letter position frame
        self.criteria_frame = ctk.CTkFrame(self,
                                           width=900,
                                           # height=100,
                                           corner_radius=10,
                                           borderwidth=0)
        self.criteria_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=0)

        # letter exclusion frame - uses pack
        self.criteria_frame_x = ttk.LabelFrame(self.criteria_frame,
                                               width=900,
                                               # height=100,
                                               text='Letters To Be Excluded'
                                               )
        self.criteria_frame_x.pack(side=tk.TOP, fill=tk.X, padx=6, pady=1)

        # letter require frame - uses pack
        self.criteria_frame_r = ttk.LabelFrame(self.criteria_frame,
                                               width=900,
                                               # height=100,
                                               text='Letters To Be Required'
                                               )
        self.criteria_frame_r.pack(side=tk.TOP, fill=tk.X, padx=6, pady=1)

        # letter position frame overall - uses pack
        self.criteria_frame_p = ttk.LabelFrame(self.criteria_frame,
                                               width=900,
                                               # height=100,
                                               text='Letters Positioning',
                                               )
        self.criteria_frame_p.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=4)

        # letter position frame exclude - uses pack
        self.criteria_frame_px = ttk.LabelFrame(self.criteria_frame_p,
                                                width=450,
                                                # height=100,
                                                text='Exclude From Position',
                                                )
        self.criteria_frame_px.pack(side=tk.LEFT, fill=tk.X, padx=4, pady=2)

        # letter position frame require- uses pack
        self.criteria_frame_pr = ttk.LabelFrame(self.criteria_frame_p,
                                                width=450,
                                                # height=100,
                                                text='Require A Position',
                                                )
        self.criteria_frame_pr.pack(side=tk.LEFT, fill=tk.X, padx=4, pady=2)

        # actions frame require- uses pack
        self.actions_frame = ttk.LabelFrame(self.criteria_frame_p,
                                            width=450,
                                            # height=100,
                                            text='General Settings',
                                            )
        self.actions_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=4, pady=2, expand=True)

        # =======  START OF ============ exclude from position controls
        def px_to_uppercase(*args):
            self.pos_px_l.set(self.pos_px_l.get().upper())

        self.pos_px_l = tk.StringVar(name='pos_px_l')
        self.combo_px_l = ttk.Combobox(self.criteria_frame_px,
                                       values=('', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                                               'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                                               'X', 'Y', 'Z'),
                                       width=4,
                                       justify=tk.CENTER,
                                       textvariable=self.pos_px_l
                                       )
        self.combo_px_l.grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.combo_px_l.current(0)
        try:
            # python 3.6
            self.pos_px_l.trace_add('write', px_to_uppercase)
        except AttributeError:
            # python < 3.6
            self.pos_px_l.trace('w', px_to_uppercase)

        self.pos_px_p = tk.StringVar()
        self.combo_px_p = ttk.Combobox(self.criteria_frame_px,
                                       values=('1', '2', '3', '4', '5'),
                                       width=4,
                                       justify=tk.CENTER,
                                       textvariable=self.pos_px_p
                                       )
        self.combo_px_p.grid(row=0, column=1, padx=1, pady=2, sticky='w')
        self.combo_px_p.current(0)

        self.bt_px_add = ctk.CTkButton(self.criteria_frame_px,
                                       text="+", width=20,
                                       command=add_x_pos
                                       )
        self.bt_px_add.grid(row=0, column=2, padx=1, pady=2, sticky='ew')

        self.bt_px_rem = ctk.CTkButton(self.criteria_frame_px,
                                       text="-", width=20,
                                       command=remove_x_pos
                                       )
        self.bt_px_rem.grid(row=0, column=3, padx=1, pady=2, sticky='ew')
        self.bt_px_clr = ctk.CTkButton(self.criteria_frame_px,
                                       text="z", width=20,
                                       command=clearall_x_pos
                                       )
        self.bt_px_clr.grid(row=0, column=4, padx=1, pady=2, sticky='ew')

        # ======  exclude position treeview
        self.treeview_px = ttk.Treeview(self.criteria_frame_px, style='position.ttk.Treeview')
        self.treeview_px.configure(columns=('1', '2'),
                                   show='headings',
                                   height=5)
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

        # =======  START OF ============ require from position controls
        def pr_to_uppercase(*args):
            self.pos_pr_l.set(self.pos_pr_l.get().upper())

        self.pos_pr_l = tk.StringVar()
        self.combo_pr_l = ttk.Combobox(self.criteria_frame_pr,
                                       values=('', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                                               'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                                               'X', 'Y', 'Z'),
                                       width=4,
                                       justify=tk.CENTER,
                                       textvariable=self.pos_pr_l
                                       )
        self.combo_pr_l.grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.combo_pr_l.current(0)
        try:
            # python 3.6
            self.pos_pr_l.trace_add('write', pr_to_uppercase)
        except AttributeError:
            # python < 3.6
            self.pos_pr_l.trace('w', pr_to_uppercase)

        self.pos_pr_p = tk.StringVar()
        self.combo_pr_p = ttk.Combobox(self.criteria_frame_pr,
                                       values=('1', '2', '3', '4', '5'),
                                       width=4,
                                       justify=tk.CENTER,
                                       textvariable=self.pos_pr_p
                                       )
        self.combo_pr_p.grid(row=0, column=1, padx=1, pady=2, sticky='w')
        self.combo_pr_p.current(0)

        self.bt_pr_add = ctk.CTkButton(self.criteria_frame_pr,
                                       text="+", width=20,
                                       command=add_r_pos
                                       )
        self.bt_pr_add.grid(row=0, column=2, padx=1, pady=2, sticky='ew')

        self.bt_pr_rem = ctk.CTkButton(self.criteria_frame_pr,
                                       text="-", width=20,
                                       command=remove_r_pos
                                       )
        self.bt_pr_rem.grid(row=0, column=3, padx=1, pady=2, sticky='ew')

        self.bt_pr_clr = ctk.CTkButton(self.criteria_frame_pr,
                                       text="z", width=20,
                                       command=clearall_r_pos
                                       )
        self.bt_pr_clr.grid(row=0, column=4, padx=1, pady=2, sticky='ew')

        # style='position.ttk.Treeview')
        self.treeview_pr = ttk.Treeview(self.criteria_frame_pr, style='position.ttk.Treeview')
        self.treeview_pr.configure(columns=('1', '2'),
                                   show='headings',
                                   height=5
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

        # ======= START OF ======== Exclude Letters =============
        self.v_xE = tk.StringVar()
        self.v_xE.set('-')
        bt_x_e = ttk.Checkbutton(self.criteria_frame_x, text="E", variable=self.v_xE, onvalue='e', offvalue='-',
                                 command=do_grep)
        bt_x_e.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xA = tk.StringVar()
        self.v_xA.set('-')
        bt_x_a = ttk.Checkbutton(self.criteria_frame_x, text="A", variable=self.v_xA, onvalue='a', offvalue='-',
                                 command=do_grep)
        bt_x_a.pack(side=tk.LEFT, padx=2, pady=2)
        sep_1 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_1.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_xR = tk.StringVar()
        self.v_xR.set('-')
        bt_xR = ttk.Checkbutton(self.criteria_frame_x, text="R", variable=self.v_xR, onvalue='r', offvalue='-',
                                command=do_grep)
        bt_xR.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xO = tk.StringVar()
        self.v_xO.set('-')
        bt_xO = ttk.Checkbutton(self.criteria_frame_x, text="O", variable=self.v_xO, onvalue='o', offvalue='-',
                                command=do_grep)
        bt_xO.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xT = tk.StringVar()
        self.v_xT.set('-')
        bt_xT = ttk.Checkbutton(self.criteria_frame_x, text="T", variable=self.v_xT, onvalue='t', offvalue='-',
                                command=do_grep)
        bt_xT.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xI = tk.StringVar()
        self.v_xI.set('-')
        bt_xI = ttk.Checkbutton(self.criteria_frame_x, text="I", variable=self.v_xI, onvalue='i', offvalue='-',
                                command=do_grep)
        bt_xI.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xL = tk.StringVar()
        self.v_xL.set('-')
        bt_xL = ttk.Checkbutton(self.criteria_frame_x, text="L", variable=self.v_xL, onvalue='l', offvalue='-',
                                command=do_grep)
        bt_xL.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xS = tk.StringVar()
        self.v_xS.set('-')
        bt_xS = ttk.Checkbutton(self.criteria_frame_x, text="S", variable=self.v_xS, onvalue='s', offvalue='-',
                                command=do_grep)
        bt_xS.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xN = tk.StringVar()
        self.v_xN.set('-')
        bt_xN = ttk.Checkbutton(self.criteria_frame_x, text="N", variable=self.v_xN, onvalue='n', offvalue='-',
                                command=do_grep)
        bt_xN.pack(side=tk.LEFT, padx=2, pady=2)
        sep_2 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_2.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_xU = tk.StringVar()
        self.v_xU.set('-')
        bt_xU = ttk.Checkbutton(self.criteria_frame_x, text="U", variable=self.v_xU, onvalue='u', offvalue='-',
                                command=do_grep)
        bt_xU.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xC = tk.StringVar()
        self.v_xC.set('-')
        bt_xC = ttk.Checkbutton(self.criteria_frame_x, text="C", variable=self.v_xC, onvalue='c', offvalue='-',
                                command=do_grep)
        bt_xC.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xY = tk.StringVar()
        self.v_xY.set('-')
        bt_xY = ttk.Checkbutton(self.criteria_frame_x, text="Y", variable=self.v_xY, onvalue='y', offvalue='-',
                                command=do_grep)
        bt_xY.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xH = tk.StringVar()
        self.v_xH.set('-')
        bt_xH = ttk.Checkbutton(self.criteria_frame_x, text="H", variable=self.v_xH, onvalue='h', offvalue='-',
                                command=do_grep)
        bt_xH.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xD = tk.StringVar()
        self.v_xD.set('-')
        bt_xD = ttk.Checkbutton(self.criteria_frame_x, text="D", variable=self.v_xD, onvalue='d', offvalue='-',
                                command=do_grep)
        bt_xD.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xP = tk.StringVar()
        self.v_xP.set('-')
        bt_xP = ttk.Checkbutton(self.criteria_frame_x, text="P", variable=self.v_xP, onvalue='p', offvalue='-',
                                command=do_grep)
        bt_xP.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xG = tk.StringVar()
        self.v_xG.set('-')
        bt_xG = ttk.Checkbutton(self.criteria_frame_x, text="G", variable=self.v_xG, onvalue='g', offvalue='-',
                                command=do_grep)
        bt_xG.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xM = tk.StringVar()
        self.v_xM.set('-')
        bt_xM = ttk.Checkbutton(self.criteria_frame_x, text="M", variable=self.v_xM, onvalue='m', offvalue='-',
                                command=do_grep)
        bt_xM.pack(side=tk.LEFT, padx=2, pady=2)
        sep_3 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_3.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_xB = tk.StringVar()
        self.v_xB.set('-')
        bt_xB = ttk.Checkbutton(self.criteria_frame_x, text="B", variable=self.v_xB, onvalue='b', offvalue='-',
                                command=do_grep)
        bt_xB.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xF = tk.StringVar()
        self.v_xF.set('-')
        bt_xF = ttk.Checkbutton(self.criteria_frame_x, text="F", variable=self.v_xF, onvalue='f', offvalue='-',
                                command=do_grep)
        bt_xF.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xK = tk.StringVar()
        self.v_xK.set('-')
        bt_xK = ttk.Checkbutton(self.criteria_frame_x, text="K", variable=self.v_xK, onvalue='k', offvalue='-',
                                command=do_grep)
        bt_xK.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xW = tk.StringVar()
        self.v_xW.set('-')
        bt_xW = ttk.Checkbutton(self.criteria_frame_x, text="W", variable=self.v_xW, onvalue='w', offvalue='-',
                                command=do_grep)
        bt_xW.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xV = tk.StringVar()
        self.v_xV.set('-')
        bt_xV = ttk.Checkbutton(self.criteria_frame_x, text="V", variable=self.v_xV, onvalue='v', offvalue='-',
                                command=do_grep)
        bt_xV.pack(side=tk.LEFT, padx=2, pady=2)
        sep_4 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_4.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_xX = tk.StringVar()
        self.v_xX.set('-')
        bt_xX = ttk.Checkbutton(self.criteria_frame_x, text="X", variable=self.v_xX, onvalue='x', offvalue='-',
                                command=do_grep)
        bt_xX.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xZ = tk.StringVar()
        self.v_xZ.set('-')
        bt_xZ = ttk.Checkbutton(self.criteria_frame_x, text="Z", variable=self.v_xZ, onvalue='z', offvalue='-',
                                command=do_grep)
        bt_xZ.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xQ = tk.StringVar()
        self.v_xQ.set('-')
        bt_xQ = ttk.Checkbutton(self.criteria_frame_x, text="Q", variable=self.v_xQ, onvalue='q', offvalue='-',
                                command=do_grep)
        bt_xQ.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_xJ = tk.StringVar()
        self.v_xJ.set('-')
        bt_xJ = ttk.Checkbutton(self.criteria_frame_x, text="J", variable=self.v_xJ, onvalue='j', offvalue='-',
                                command=do_grep)
        bt_xJ.pack(side=tk.LEFT, padx=2, pady=2)
        sep_5 = ttk.Separator(self.criteria_frame_x, orient='vertical')
        sep_5.pack(side=tk.LEFT, fill='y', padx=8)
        self.ex_btn_vars = [self.v_xA, self.v_xB, self.v_xC, self.v_xD, self.v_xE, self.v_xF,
                            self.v_xG, self.v_xH, self.v_xI, self.v_xJ, self.v_xK, self.v_xL,
                            self.v_xM, self.v_xN, self.v_xO, self.v_xP, self.v_xQ, self.v_xR,
                            self.v_xS, self.v_xT, self.v_xU, self.v_xV, self.v_xW, self.v_xX,
                            self.v_xY, self.v_xZ]

        def clear_excl_ckbs():
            for x_var in self.ex_btn_vars:
                x_var.set('-')
            do_grep()

        self.bt_x_clr = ctk.CTkButton(self.criteria_frame_x,
                                      text="Clear", width=20,
                                      command=clear_excl_ckbs
                                      )
        self.bt_x_clr.pack(side=tk.TOP, padx=2, pady=2)
        # == END OF ========== Exclude Letters =============

        # ==== START OF =========== Require Letters =============
        self.v_rE = tk.StringVar()
        self.v_rE.set('-')
        bt_r_E = ttk.Checkbutton(self.criteria_frame_r, text="E", variable=self.v_rE, onvalue='e', offvalue='-',
                                 command=do_grep)
        bt_r_E.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rA = tk.StringVar()
        self.v_rA.set('-')
        bt_r_A = ttk.Checkbutton(self.criteria_frame_r, text="A", variable=self.v_rA, onvalue='a', offvalue='-',
                                 command=do_grep)
        bt_r_A.pack(side=tk.LEFT, padx=2, pady=2)
        sep_1 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_1.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_rR = tk.StringVar()
        self.v_rR.set('-')
        bt_r_R = ttk.Checkbutton(self.criteria_frame_r, text="R", variable=self.v_rR, onvalue='r', offvalue='-',
                                 command=do_grep)
        bt_r_R.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rO = tk.StringVar()
        self.v_rO.set('-')
        bt_r_O = ttk.Checkbutton(self.criteria_frame_r, text="O", variable=self.v_rO, onvalue='o', offvalue='-',
                                 command=do_grep)
        bt_r_O.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rT = tk.StringVar()
        self.v_rT.set('-')
        bt_r_T = ttk.Checkbutton(self.criteria_frame_r, text="T", variable=self.v_rT, onvalue='t', offvalue='-',
                                 command=do_grep)
        bt_r_T.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rI = tk.StringVar()
        self.v_rI.set('-')
        bt_r_I = ttk.Checkbutton(self.criteria_frame_r, text="I", variable=self.v_rI, onvalue='i', offvalue='-',
                                 command=do_grep)
        bt_r_I.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rL = tk.StringVar()
        self.v_rL.set('-')
        bt_r_L = ttk.Checkbutton(self.criteria_frame_r, text="L", variable=self.v_rL, onvalue='l', offvalue='-',
                                 command=do_grep)
        bt_r_L.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rS = tk.StringVar()
        self.v_rS.set('-')
        bt_r_S = ttk.Checkbutton(self.criteria_frame_r, text="S", variable=self.v_rS, onvalue='s', offvalue='-',
                                 command=do_grep)
        bt_r_S.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rN = tk.StringVar()
        self.v_rN.set('-')
        bt_r_N = ttk.Checkbutton(self.criteria_frame_r, text="N", variable=self.v_rN, onvalue='n', offvalue='-',
                                 command=do_grep)
        bt_r_N.pack(side=tk.LEFT, padx=2, pady=2)
        sep_2 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_2.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_rU = tk.StringVar()
        self.v_rU.set('-')
        bt_r_U = ttk.Checkbutton(self.criteria_frame_r, text="U", variable=self.v_rU, onvalue='u', offvalue='-',
                                 command=do_grep)
        bt_r_U.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rC = tk.StringVar()
        self.v_rC.set('-')
        bt_r_C = ttk.Checkbutton(self.criteria_frame_r, text="C", variable=self.v_rC, onvalue='c', offvalue='-',
                                 command=do_grep)
        bt_r_C.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rY = tk.StringVar()
        self.v_rY.set('-')
        bt_r_Y = ttk.Checkbutton(self.criteria_frame_r, text="Y", variable=self.v_rY, onvalue='y', offvalue='-',
                                 command=do_grep)
        bt_r_Y.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rH = tk.StringVar()
        self.v_rH.set('-')
        bt_r_H = ttk.Checkbutton(self.criteria_frame_r, text="H", variable=self.v_rH, onvalue='h', offvalue='-',
                                 command=do_grep)
        bt_r_H.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rD = tk.StringVar()
        self.v_rD.set('-')
        bt_r_D = ttk.Checkbutton(self.criteria_frame_r, text="D", variable=self.v_rD, onvalue='d', offvalue='-',
                                 command=do_grep)
        bt_r_D.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rP = tk.StringVar()
        self.v_rP.set('-')
        bt_r_P = ttk.Checkbutton(self.criteria_frame_r, text="P", variable=self.v_rP, onvalue='p', offvalue='-',
                                 command=do_grep)
        bt_r_P.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rG = tk.StringVar()
        self.v_rG.set('-')
        bt_r_G = ttk.Checkbutton(self.criteria_frame_r, text="G", variable=self.v_rG, onvalue='g', offvalue='-',
                                 command=do_grep)
        bt_r_G.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rM = tk.StringVar()
        self.v_rM.set('-')
        bt_r_M = ttk.Checkbutton(self.criteria_frame_r, text="M", variable=self.v_rM, onvalue='m', offvalue='-',
                                 command=do_grep)
        bt_r_M.pack(side=tk.LEFT, padx=2, pady=2)
        sep_3 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_3.pack(side=tk.LEFT, fill='y', padx=8)
        self.v_rB = tk.StringVar()
        self.v_rB.set('-')
        bt_r_B = ttk.Checkbutton(self.criteria_frame_r, text="B", variable=self.v_rB, onvalue='b', offvalue='-',
                                 command=do_grep)
        bt_r_B.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rF = tk.StringVar()
        self.v_rF.set('-')
        bt_r_F = ttk.Checkbutton(self.criteria_frame_r, text="F", variable=self.v_rF, onvalue='f', offvalue='-',
                                 command=do_grep)
        bt_r_F.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rK = tk.StringVar()
        self.v_rK.set('-')
        bt_r_K = ttk.Checkbutton(self.criteria_frame_r, text="K", variable=self.v_rK, onvalue='k', offvalue='-',
                                 command=do_grep)
        bt_r_K.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rW = tk.StringVar()
        self.v_rW.set('-')
        bt_r_W = ttk.Checkbutton(self.criteria_frame_r, text="W", variable=self.v_rW, onvalue='w', offvalue='-',
                                 command=do_grep)
        bt_r_W.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rV = tk.StringVar()
        self.v_rV.set('-')
        bt_r_V = ttk.Checkbutton(self.criteria_frame_r, text="V", variable=self.v_rV, onvalue='v', offvalue='-',
                                 command=do_grep)
        bt_r_V.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rX = tk.StringVar()
        self.v_rX.set('-')
        sep_4 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_4.pack(side=tk.LEFT, fill='y', padx=8)
        bt_r_X = ttk.Checkbutton(self.criteria_frame_r, text="X", variable=self.v_rX, onvalue='x', offvalue='-',
                                 command=do_grep)
        bt_r_X.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rZ = tk.StringVar()
        self.v_rZ.set('-')
        bt_r_Z = ttk.Checkbutton(self.criteria_frame_r, text="Z", variable=self.v_rZ, onvalue='z', offvalue='-',
                                 command=do_grep)
        bt_r_Z.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rQ = tk.StringVar()
        self.v_rQ.set('-')
        bt_r_Q = ttk.Checkbutton(self.criteria_frame_r, text="Q", variable=self.v_rQ, onvalue='q', offvalue='-',
                                 command=do_grep)
        bt_r_Q.pack(side=tk.LEFT, padx=2, pady=2)
        self.v_rJ = tk.StringVar()
        self.v_rJ.set('-')
        bt_r_J = ttk.Checkbutton(self.criteria_frame_r, text="J", variable=self.v_rJ, onvalue='j', offvalue='-',
                                 command=do_grep)
        bt_r_J.pack(side=tk.LEFT, padx=2, pady=2)
        sep_5 = ttk.Separator(self.criteria_frame_r, orient='vertical')
        sep_5.pack(side=tk.LEFT, fill='y', padx=8)

        self.re_btn_vars = [self.v_rA, self.v_rB, self.v_rC, self.v_rD, self.v_rE, self.v_rF,
                            self.v_rG, self.v_rH, self.v_rI, self.v_rJ, self.v_rK, self.v_rL,
                            self.v_rM, self.v_rN, self.v_rO, self.v_rP, self.v_rQ, self.v_rR,
                            self.v_rS, self.v_rT, self.v_rU, self.v_rV, self.v_rW, self.v_rX,
                            self.v_rY, self.v_rZ]

        def clear_reqr_ckbs():
            for r_var in self.re_btn_vars:
                r_var.set('-')
            do_grep()

        self.bt_r_clr = ctk.CTkButton(self.criteria_frame_r,
                                      text='Clear', width=20,
                                      command=clear_reqr_ckbs
                                      )
        self.bt_r_clr.pack(side=tk.TOP, padx=2, pady=2)
        # === END OF ========= Require Letters =============

        # === START OF ====== General Controls ==========
        sw_no_dups = ctk.CTkSwitch(self.actions_frame,
                                   text="Allow Duplicate Letters",
                                   onvalue="on",
                                   offvalue="off",
                                   command=do_grep)
        sw_no_dups.pack(side=tk.TOP, padx=6, pady=6, anchor='w')

        combo_vocab = ttk.Combobox(self.actions_frame,
                                   values=("Use Small Vocabulary", "Use Large Vocabulary"),
                                   state='readonly',
                                   textvariable=self.vocabulary
                                   )
        combo_vocab.pack(side=tk.TOP, padx=6, pady=2, anchor='nw', fill=tk.X)
        combo_vocab.current(0)
        combo_vocab.bind("<<ComboboxSelected>>", callback_do_grep)
        # === END OF ====== General Controls ==========

        # === START OF ====== Application Controls ==========
        # admin (Application) frame - uses pack
        self.admin_frame = ttk.LabelFrame(self.criteria_frame_p,
                                          width=250,
                                          height=100,
                                          text='Application',
                                          )
        self.admin_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=4, pady=2, expand=True)

        self.bt_Q = ctk.CTkButton(self.admin_frame, text="Quit", width=100, command=self.destroy)
        self.bt_Q.pack(side=tk.BOTTOM, padx=6, pady=2, fill=tk.X)

        self.bt_help = ctk.CTkButton(self.admin_frame, text="Information", width=40, command=self.show_help)
        self.bt_help.pack(side=tk.BOTTOM, padx=6, pady=6, fill=tk.X)

        self.bt_zap = ctk.CTkButton(self.admin_frame, text="Clear All Settings", width=40, command=clear_all)
        self.bt_zap.pack(side=tk.TOP, padx=6, pady=6, fill=tk.X)
        # === END OF ====== Application Controls ==========

        # run the initial grep
        do_grep()

    # The help information window
    def create_wnd_help(self):
        global data_path
        self.wnd_help = ctk.CTkToplevel(self)
        self.wnd_help.wm_title('Some Information For You')
        self.wnd_help.resizable(width=False, height=False)

        full_path_name = os.path.join(os.path.dirname(__file__), data_path, 'helpinfo.txt')
        if os.path.exists(full_path_name):
            f = open(full_path_name, "r", encoding="UTF8").read()
        else:
            f = 'This is all the help you get because file helpinfo.txt has gone missing.'

        self.wnd_help.info_frame = ttk.LabelFrame(self.wnd_help,
                                                  borderwidth=0,
                                                  )
        self.wnd_help.info_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2, expand=True)

        msg1 = tk.Text(self.wnd_help.info_frame,
                       wrap='word',
                       width=120,
                       height=30,
                       padx=10,
                       pady=8,
                       background='#dedede',
                       borderwidth=0,
                       highlightthickness=0
                       )
        msg1.grid(row=0, column=0, padx=6, pady=2)
        msg1.configure(font=font_tuple)
        # scrollbar for help
        help_sb = ttk.Scrollbar(self.wnd_help.info_frame, orient='vertical')
        help_sb.grid(row=0, column=1, padx=1, pady=2, sticky='ens')
        msg1.config(yscrollcommand=help_sb.set)
        help_sb.config(command=msg1.yview)
        msg1.delete(1.0, tk.END)
        msg1.insert(tk.END, f)

        button_q = ctk.CTkButton(self.wnd_help, text="Close",
                                 command=self.close_help)
        button_q.pack(side="right", padx=20, pady=20)
        self.wnd_help.protocol("WM_DELETE_WINDOW", self.close_help)  # assign to closing button [X]


# end Pywordlemainwindow class

this_app = Pywordlemainwindow()
this_app.mainloop()
