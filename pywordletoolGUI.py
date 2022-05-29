# get customtkinter  -> pip3 install customtkinter
# if already, may need to upgrade it -> pip3 install customtkinter --upgrade
# from tkinter import *
import textwrap

import helpers

import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
import customtkinter as ctk

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

n_col = 7

def str_wrd_list_hrd():
    h_txt = " Word : Rank "
    left_pad = ""
    mid_pad = "  "
    h_line = left_pad + h_txt
    for i in range(1, n_col):
        h_line = h_line + mid_pad + h_txt
    return h_line

class pywordletoolWND(ctk.CTk):
    # global do_grep
    global n_col
    global switch_var

    def __init__(self):
        super().__init__()
        self.title("This Wordle Tool")
        w_width = 900
        w_height = 600
        pos_x = int(self.winfo_screenwidth() / 2 - w_width / 2)
        pos_y = int(self.winfo_screenheight() / 3 - w_height / 2)
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))
        # self.resizable(width=False,height=False)
        Font_tuple = ("PT Mono", 14, "normal")

        self.no_dups = tk.BooleanVar()
        self.no_dupe_state = tk.StringVar()
        self.no_dupe_state.set("on")
        self.vocabulary = tk.StringVar()
        self.status = tk.StringVar()
        self.allgreps = tk.StringVar()

        # return a reformatted string with wordwrapping
        #@staticmethod
        def wrap_this(string, max_chars):
            """A helper that will return the string with word-break wrapping.
            :param str string: The text to be wrapped.
            :param int max_chars: The maximum number of characters on a line before wrapping.
            """
            string = string.replace('\n', '').replace('\r', '') # strip confusing newlines
            words = string.split(' ')
            the_lines = []
            the_line = ""
            for w in words:
                if len(the_line+' '+w) <= max_chars:
                    the_line += ' '+w
                else:
                    the_lines.append(the_line)
                    the_line = w
            if the_line:
                the_lines.append(the_line)
            the_lines[0] = the_lines[0][1:]
            the_newline = ""
            for w in the_lines:
                the_newline += '\n'+w
            return the_newline


        self.result_frame = ctk.CTkFrame(self,
                                  width=900,
                                  height=200,
                                  corner_radius=10,
                                  # relief='sunken',
                                  borderwidth=0,
                                         )
        self.result_frame.pack(padx=20,pady=20)

        # tx_result_hd = tk.Text(self.result_frame, relief='sunken', wrap='word',background='#e3e4e5',borderwidth=0,highlightthickness=0)
        # # tx_result_hd.pack(  fill=tk.X)
        # tx_result_hd.grid(row=0, column=0,  columnspan=4, sticky='ew', padx=4, pady=4)
        # tx_result_hd.configure(font = Font_tuple)
        # place_hd(tx_result_hd)

        lb_result_hd = tk.Label(self.result_frame, text= str_wrd_list_hrd(), relief='sunken',background='#e3e4e5',borderwidth=0,highlightthickness=0)
        # tx_result_hd.pack(  fill=tk.X)
        lb_result_hd.grid(row=0, column=0,  columnspan=4, sticky='ew', padx=6, pady=2)
        lb_result_hd.configure(font = Font_tuple)

        tx_result = tk.Text(self.result_frame, wrap='word',background='#e3e4e5',borderwidth=0,highlightthickness=0)
        # tx_result.pack(  expand= True, fill=tk.X)
        tx_result.grid(row=1, column=0,  columnspan=4,  sticky='ew', padx=6, pady=4)
        tx_result.configure(font = Font_tuple)

        tx_results_scroll_bar = ttk.Scrollbar(self.result_frame, orient='vertical', command=tx_result.yview)
        tx_results_scroll_bar.grid(row=0, rowspan=3, column=5, sticky='ns')
        # tx_results_scroll_bar.pack()


        lb_status = tk.Label(self.result_frame,
                             textvariable=self.status,
                             background='#e3e4e5',
                             borderwidth=0,
                             highlightthickness=0)
        # tx_result.pack(  expand= True, fill=tk.X)
        lb_status.grid(row=4, column=0,  columnspan=4,  sticky='ew', padx=6, pady=4)
        lb_status.configure(font = Font_tuple)
        self.status.set('=> No status yet.')
        print(self.status.get())

        self.settings_frame = ctk.CTkFrame(self,
                                           width=900,
                                           height=100,
                                           corner_radius=10,
                                           # relief='sunken',
                                           borderwidth=0)
        # self.frame.grid(row=0, column=0, rowspan=1, columnspan=3, padx=6, pady=6)
        self.settings_frame.pack(side= tk.BOTTOM, fill=tk.X,  padx=20, pady=10)



        # gr_output = ctk.CTkLabel(self.settings_frame,
        #                          # textvariable=text_var,
        #                          width=778,
        #                          height=100,
        #                          fg_color=("white", "gray75"),
        #                          corner_radius=0
        #                          )
        # # gr_output.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # gr_output.grid(row=1, column=0, rowspan=1, columnspan=2, padx=2, pady=2)
        # # gr_output.pack()

        # self.e = customtkinter.CTkEntry(self,width = 34, borderwidth=2,readonlybackground="")
        # self.e.pack(row=0,column=0,columnspan=1,padx=10,pady=10)
        #
        # self.label2 = customtkinter.CTkLabel(self, text ="Helps you do a wordle.").grid(row=2, column=0, padx=10, pady=6)
        #

        lb_allgreps = tk.Label(self.settings_frame,
                             textvariable=self.allgreps,
                             background='#e3e4e5',
                             borderwidth=0,
                             highlightthickness=0)
        # tx_result.pack(  expand= True, fill=tk.X)
        lb_allgreps.grid(row=3, column=0,  columnspan=6,  sticky='w', padx=6, pady=4)
        lb_allgreps.configure(font = Font_tuple)
        self.allgreps.set('=> AllGreps')
        # print(self.allgreps.get())



        def do_grep():
            """Runs a wordletool helper grep instance
            """
            data_path = 'worddata/' # path from here to data folder
            if sw_no_dups.get() == "on":
                no_dups = False
            else:
                no_dups = True

            if self.vocabulary.get() == "Small Vocabulary":
                vocab_filename = 'wo_nyt_wordlist.txt'
            else:
                vocab_filename = 'nyt_wordlist.txt'

            wordletool = helpers.ToolResults(data_path, vocab_filename, 'letter_ranks.txt', no_dups)
            tx_result.delete( 1.0 , tk.END)

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
                if c == n_col:
                    tx_result.insert(tk.END, l_msg + '\n')
                    c = 0
                    l_msg = ""
                if i == n_items:
                    tx_result.insert(tk.END, l_msg + '\n')
            tx_result.see('end')
            print(wordletool.show_status())
            self.status.set(wordletool.show_status())
            self.allgreps.set(wrap_this(wordletool.show_cmd(),90))


        def callbackFuncVocab(event):
            vocab = event.widget.get()
            print(vocab)
            do_grep()

        combo_vocab = ttk.Combobox(self.settings_frame,
                                   values= ("Small Vocabulary", "Large Vocabulary"),
                                   state= 'readonly',
                                   textvariable = self.vocabulary
                                   )
        combo_vocab.grid(row=0, column=1, padx= 6, pady=6, sticky="W")
        combo_vocab.current(0)
        combo_vocab.configure(font = Font_tuple)
        combo_vocab.bind("<<ComboboxSelected>>", callbackFuncVocab)

        sw_no_dups = ctk.CTkSwitch(self.settings_frame,
                                   text="Allow Duplicate Letters",
                                   onvalue="on",
                                   offvalue="off",
                                   command=do_grep
                                   )
        sw_no_dups.grid(row=0, column=2, padx=20, pady=6, sticky="W")


        self.bt_grep = ctk.CTkButton(self.settings_frame,
                                     text="Do Grep",
                                     command=do_grep
                                     )
        self.bt_grep.grid(row=0, column=0, padx=10, pady=10)

        self.bt_Q = ctk.CTkButton(self.settings_frame, text="Quit", command=self.destroy)
        self.bt_Q.grid(row=3, column=7, columnspan= 1, padx=6, pady=6, sticky='e')








# end pywordletool class

this_app = pywordletoolWND()
this_app.mainloop()
