# get customtkinter  -> pip3 install customtkinter
# if already, may need to upgrade it -> pip3 install customtkinter --upgrade
# from tkinter import *
import time

import helpers

import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
from tkinter.constants import END

import customtkinter as ctk

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
n_col = 7




def sw_no_dup_event():
    pass
    # print("switch toggled, current value:", sw_no_dups.get())

def str_wrd_list_hrd():
    h_txt = " Word : Rank "
    left_pad = ""
    mid_pad = "  "
    h_line = left_pad + h_txt
    for i in range(1, n_col):
        h_line = h_line + mid_pad + h_txt
    return h_line

class pywordletool(ctk.CTk):
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
        Font_tuple = ("PT Mono", 14, "normal")

        self.no_dups = tk.BooleanVar()
        self.vocabulary = tk.StringVar()

        self.result_frame = ctk.CTkFrame(self,
                                  width=900,
                                  height=200,
                                  corner_radius=10,
                                  relief='sunken',
                                  borderwidth=0,
                                         )
        self.result_frame.pack(padx=10,pady=10) # fill=tk.X,

        # self.result_frame.rowconfigure(0, weight = 1)
        # self.result_frame.rowconfigure(1, weight = 10)

        # text_var = tk.StringVar(value="The grep output goes here. And it goes. And goes. And Goes.")

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


        # tx_result.insert(1.0, text_var.get())

        tx_results_scroll_bar = ttk.Scrollbar(self.result_frame, orient='vertical', command=tx_result.yview)
        tx_results_scroll_bar.grid(row=0, rowspan=3, column=5, sticky='ns')
        # tx_results_scroll_bar.pack()

        tx_status = tk.Text(self.result_frame,  wrap='word',background='#e3e4e5',borderwidth=0,highlightthickness=0)
        # tx_result.pack(  expand= True, fill=tk.X)
        tx_status.grid(row=3, column=0,  columnspan=5,  sticky='ew', padx=6, pady=4)
        tx_status.configure(font = Font_tuple)
        tx_status.insert(1.0,'No status yet.')




        self.setting_frame = ctk.CTkFrame(self,
                                  width=780,
                                  height=100,
                                  corner_radius=10,
                                  relief='sunken',
                                  borderwidth=2)
        # self.frame.grid(row=0, column=0, rowspan=1, columnspan=3, padx=6, pady=6)
        self.setting_frame.pack( side= tk.TOP, fill = tk.X, padx=6, pady=6)


        # gr_output = ctk.CTkLabel(self.setting_frame,
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

        combo_vocab = ttk.Combobox(self.setting_frame,
                                values= ("Small Vocabulary", "Large Vocabulary"),
                                state= 'readonly'
                                )
        combo_vocab.grid(row=3, column=0, padx= 6, pady=6, sticky="W")
        combo_vocab.current(0)

        sw_no_dups_var = tk.StringVar(value="off")   # starting value

        sw_no_dups = ctk.CTkSwitch(self.setting_frame,
                             text="Allow Duplicate Letters",
                             variable=sw_no_dups_var,
                             onvalue="on",
                             offvalue="off"
                             )
        sw_no_dups.grid(row=3, column=2, padx=6, pady=6, sticky="W")

        def do_grep():
            data_path = 'worddata/' # path from here to data folder
            if sw_no_dups.get() == "on":
                no_dups = False
            else:
                no_dups = True
            # initialize the wordletool

            if combo_vocab.get() == "Small Vocabulary":
                vocab_filename = 'wo_nyt_wordlist.txt'
            else:
                vocab_filename = 'nyt_wordlist.txt'
            wordletool = helpers.ToolResults(data_path, vocab_filename, 'letter_ranks.txt', no_dups)
            tx_result.delete( 1.0 , END)
            tx_status.delete(1.0, END)

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
                    tx_result.insert(END, l_msg + '\n')
                    c = 0
                    l_msg = ""
                if i == n_items:
                    tx_result.insert(END, l_msg + '\n')
            tx_result.see('end')
            print(wordletool.show_status())
            tx_status.insert(END,wordletool.show_status())

        self.bt_grep = ctk.CTkButton(self.setting_frame, text="Do Grep",
                                     # command=(lambda: self.bt_grep.set_text("Changed This To Be Long"))
                                     command=do_grep
                                     )
        self.bt_grep.grid(row=1, column=0)
        self.bt_Q = ctk.CTkButton(self.setting_frame, text="Quit", command=self.destroy)
        self.bt_Q.grid(row=3, column=3, padx=6, pady=6, sticky='e')








# end pywordletool class

this_app = pywordletool()
this_app.mainloop()
