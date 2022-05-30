# get customtkinter  -> pip3 install customtkinter
# if already, may need to upgrade it -> pip3 install customtkinter --upgrade
# from tkinter import *
import textwrap

import helpers

import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
import customtkinter as ctk

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
# ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

n_col = 8

def str_wrd_list_hrd():
    """Creates the word list header line.
    """
    h_txt = " Word : Rank "
    left_pad = ""
    mid_pad = "  "
    h_line = left_pad + h_txt
    for i in range(1, n_col):
        h_line = h_line + mid_pad + h_txt
    return h_line

class pywordletoolWND(ctk.CTk):
    """The pywordletool application GUI window
    """
    global n_col
    global switch_var

    def __init__(self):
        super().__init__()
        self.title("This Wordle Tool")
        w_width = 1020
        w_height = 700
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

        # configure style
        # self.style = ttk.Style(self)
        # self.style.configure('TSeparator', )

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
                                      borderwidth=0)
        self.result_frame.pack(padx=20,pady=8)


        lb_result_hd = tk.Label(self.result_frame,
                                text= str_wrd_list_hrd(),
                                relief='sunken',
                                background='#dedede',
                                borderwidth=0,
                                highlightthickness=0)
        lb_result_hd.grid(row=0, column=0,  columnspan=4, sticky='ew', padx=6, pady=2)
        lb_result_hd.configure(font = Font_tuple)

        tx_result = tk.Text(self.result_frame,
                            wrap='word',
                            background='#dedede',
                            borderwidth=0,
                            highlightthickness=0)
        tx_result.grid(row=1, column=0,  columnspan=4,  sticky='ew', padx=6, pady=4)
        tx_result.configure(font = Font_tuple)

        tx_results_scroll_bar = ttk.Scrollbar(self.result_frame, orient='vertical', command=tx_result.yview)
        tx_results_scroll_bar.grid(row=0, rowspan=3, column=5, sticky='ns')

        lb_status = tk.Label(self.result_frame,
                             textvariable=self.status,
                             background='#dedede',
                             borderwidth=0,
                             highlightthickness=0)
        lb_status.grid(row=2, rowspan= 3, column=0,  columnspan=4,  sticky='ew', padx=6, pady=4)
        lb_status.configure(font = Font_tuple)
        self.status.set('=> No status yet.')

        # grep criteria outer frame
        self.criteria_frame = ctk.CTkFrame(self,
                                           width=900,
                                           height=100,
                                           corner_radius=10,
                                           borderwidth=0)
        self.criteria_frame.pack(side= tk.BOTTOM, fill=tk.X,  padx=20, pady=8)

        self.criteria_frame_r = ttk.LabelFrame(self.criteria_frame,
                                        width=900,
                                        height=100,
                                        text= 'Letters To Be Required  (Require is not the same as Allow)',
                                        )
        self.criteria_frame_r.pack(side= tk.BOTTOM, fill=tk.X,  padx=6, pady=6)

        self.criteria_frame_x = ttk.LabelFrame(self.criteria_frame,
                                        width=900,
                                        height=100,
                                        text= 'Letters To Be Excluded',
                                        )
        self.criteria_frame_x.pack(side= tk.BOTTOM, fill=tk.X,  padx=6, pady=6)

        # =============== Exclude Letters =============
        self.v_xE = tk.IntVar()
        self.v_xE.set(0)
        bt_x_E = ttk.Checkbutton(self.criteria_frame_x, text = "E", variable=self.v_xE, onvalue=1, offvalue=0)
        bt_x_E.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xA = tk.IntVar()
        self.v_xA.set(0)
        bt_x_A= ttk.Checkbutton(self.criteria_frame_x, text = "A", variable=self.v_xA, onvalue=1, offvalue=0)
        bt_x_A.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_1 = ttk.Separator(self.criteria_frame_x, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_xR = tk.IntVar()
        self.v_xR.set(0)
        bt_x_R = ttk.Checkbutton(self.criteria_frame_x, text = "R", variable=self.v_xR, onvalue=1, offvalue=0)
        bt_x_R.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xO = tk.IntVar()
        self.v_xO.set(0)
        bt_x_O = ttk.Checkbutton(self.criteria_frame_x, text = "O", variable=self.v_xO, onvalue=1, offvalue=0)
        bt_x_O.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xT = tk.IntVar()
        self.v_xT.set(0)
        bt_x_T = ttk.Checkbutton(self.criteria_frame_x, text = "T", variable=self.v_xT, onvalue=1, offvalue=0)
        bt_x_T.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xI = tk.IntVar()
        self.v_xI.set(0)
        bt_x_I = ttk.Checkbutton(self.criteria_frame_x, text = "I", variable=self.v_xI, onvalue=1, offvalue=0)
        bt_x_I.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xL = tk.IntVar()
        self.v_xL.set(0)
        bt_x_L = ttk.Checkbutton(self.criteria_frame_x, text = "L", variable=self.v_xL, onvalue=1, offvalue=0)
        bt_x_L.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xS = tk.IntVar()
        self.v_xS.set(0)
        bt_x_S = ttk.Checkbutton(self.criteria_frame_x, text = "S", variable=self.v_xS, onvalue=1, offvalue=0)
        bt_x_S.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xN = tk.IntVar()
        self.v_xN.set(0)
        bt_x_N = ttk.Checkbutton(self.criteria_frame_x, text = "N", variable=self.v_xN, onvalue=1, offvalue=0)
        bt_x_N.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_2 = ttk.Separator(self.criteria_frame_x, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_xU = tk.IntVar()
        self.v_xU.set(0)
        bt_x_U = ttk.Checkbutton(self.criteria_frame_x, text = "U", variable=self.v_xU, onvalue=1, offvalue=0)
        bt_x_U.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xC = tk.IntVar()
        self.v_xC.set(0)
        bt_x_C = ttk.Checkbutton(self.criteria_frame_x, text = "C", variable=self.v_xC, onvalue=1, offvalue=0)
        bt_x_C.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xY = tk.IntVar()
        self.v_xY.set(0)
        bt_x_Y = ttk.Checkbutton(self.criteria_frame_x, text = "Y", variable=self.v_xY, onvalue=1, offvalue=0)
        bt_x_Y.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xH = tk.IntVar()
        self.v_xH.set(0)
        bt_x_H = ttk.Checkbutton(self.criteria_frame_x, text = "H", variable=self.v_xH, onvalue=1, offvalue=0)
        bt_x_H.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xD = tk.IntVar()
        self.v_xD.set(0)
        bt_x_D = ttk.Checkbutton(self.criteria_frame_x, text = "D", variable=self.v_xD, onvalue=1, offvalue=0)
        bt_x_D.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xP = tk.IntVar()
        self.v_xP.set(0)
        bt_x_P = ttk.Checkbutton(self.criteria_frame_x, text = "P", variable=self.v_xP, onvalue=1, offvalue=0)
        bt_x_P.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xG = tk.IntVar()
        self.v_xG.set(0)
        bt_x_G = ttk.Checkbutton(self.criteria_frame_x, text = "G", variable=self.v_xG, onvalue=1, offvalue=0)
        bt_x_G.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xM = tk.IntVar()
        self.v_xM.set(0)
        bt_x_M = ttk.Checkbutton(self.criteria_frame_x, text = "M", variable=self.v_xM, onvalue=1, offvalue=0)
        bt_x_M.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_3 = ttk.Separator(self.criteria_frame_x, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_xB = tk.IntVar()
        self.v_xB.set(0)
        bt_x_B = ttk.Checkbutton(self.criteria_frame_x, text = "B", variable=self.v_xB, onvalue=1, offvalue=0)
        bt_x_B.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xF = tk.IntVar()
        self.v_xF.set(0)
        bt_x_F = ttk.Checkbutton(self.criteria_frame_x, text = "F", variable=self.v_xF, onvalue=1, offvalue=0)
        bt_x_F.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xK = tk.IntVar()
        self.v_xK.set(0)
        bt_x_K = ttk.Checkbutton(self.criteria_frame_x, text = "K", variable=self.v_xK, onvalue=1, offvalue=0)
        bt_x_K.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xW = tk.IntVar()
        self.v_xW.set(0)
        bt_x_W = ttk.Checkbutton(self.criteria_frame_x, text = "W", variable=self.v_xW, onvalue=1, offvalue=0)
        bt_x_W.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xV = tk.IntVar()
        self.v_xV.set(0)
        bt_x_V = ttk.Checkbutton(self.criteria_frame_x, text = "V", variable=self.v_xV, onvalue=1, offvalue=0)
        bt_x_V.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xX = tk.IntVar()
        self.v_xX.set(0)
        sep_4 = ttk.Separator(self.criteria_frame_x, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        bt_x_X = ttk.Checkbutton(self.criteria_frame_x, text = "X", variable=self.v_xX, onvalue=1, offvalue=0)
        bt_x_X.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xZ = tk.IntVar()
        self.v_xZ.set(0)
        bt_x_Z = ttk.Checkbutton(self.criteria_frame_x, text = "Z", variable=self.v_xZ, onvalue=1, offvalue=0)
        bt_x_Z.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xQ = tk.IntVar()
        self.v_xQ.set(0)
        bt_x_Q = ttk.Checkbutton(self.criteria_frame_x, text = "Q", variable=self.v_xQ, onvalue=1, offvalue=0)
        bt_x_Q.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_xJ = tk.IntVar()
        self.v_xJ.set(0)
        bt_x_J = ttk.Checkbutton(self.criteria_frame_x, text = "J", variable=self.v_xJ, onvalue=1, offvalue=0)
        bt_x_J.pack(side=tk.LEFT,padx = 2, pady = 2)
        # ==END========== Exclude Letters =============

        # =============== Require Letters =============
        self.v_rE = tk.IntVar()
        self.v_rE.set(0)
        bt_r_E = ttk.Checkbutton(self.criteria_frame_r, text = "E", variable=self.v_rE, onvalue=1, offvalue=0)
        bt_r_E.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rA = tk.IntVar()
        self.v_rA.set(0)
        bt_r_A= ttk.Checkbutton(self.criteria_frame_r, text = "A", variable=self.v_rA, onvalue=1, offvalue=0)
        bt_r_A.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_1 = ttk.Separator(self.criteria_frame_r, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_rR = tk.IntVar()
        self.v_rR.set(0)
        bt_r_R = ttk.Checkbutton(self.criteria_frame_r, text = "R", variable=self.v_rR, onvalue=1, offvalue=0)
        bt_r_R.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rO = tk.IntVar()
        self.v_rO.set(0)
        bt_r_O = ttk.Checkbutton(self.criteria_frame_r, text = "O", variable=self.v_rO, onvalue=1, offvalue=0)
        bt_r_O.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rT = tk.IntVar()
        self.v_rT.set(0)
        bt_r_T = ttk.Checkbutton(self.criteria_frame_r, text = "T", variable=self.v_rT, onvalue=1, offvalue=0)
        bt_r_T.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rI = tk.IntVar()
        self.v_rI.set(0)
        bt_r_I = ttk.Checkbutton(self.criteria_frame_r, text = "I", variable=self.v_rI, onvalue=1, offvalue=0)
        bt_r_I.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rL = tk.IntVar()
        self.v_rL.set(0)
        bt_r_L = ttk.Checkbutton(self.criteria_frame_r, text = "L", variable=self.v_rL, onvalue=1, offvalue=0)
        bt_r_L.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rS = tk.IntVar()
        self.v_rS.set(0)
        bt_r_S = ttk.Checkbutton(self.criteria_frame_r, text = "S", variable=self.v_rS, onvalue=1, offvalue=0)
        bt_r_S.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rN = tk.IntVar()
        self.v_rN.set(0)
        bt_r_N = ttk.Checkbutton(self.criteria_frame_r, text = "N", variable=self.v_rN, onvalue=1, offvalue=0)
        bt_r_N.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_2 = ttk.Separator(self.criteria_frame_r, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_rU = tk.IntVar()
        self.v_rU.set(0)
        bt_r_U = ttk.Checkbutton(self.criteria_frame_r, text = "U", variable=self.v_rU, onvalue=1, offvalue=0)
        bt_r_U.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rC = tk.IntVar()
        self.v_rC.set(0)
        bt_r_C = ttk.Checkbutton(self.criteria_frame_r, text = "C", variable=self.v_rC, onvalue=1, offvalue=0)
        bt_r_C.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rY = tk.IntVar()
        self.v_rY.set(0)
        bt_r_Y = ttk.Checkbutton(self.criteria_frame_r, text = "Y", variable=self.v_rY, onvalue=1, offvalue=0)
        bt_r_Y.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rH = tk.IntVar()
        self.v_rH.set(0)
        bt_r_H = ttk.Checkbutton(self.criteria_frame_r, text = "H", variable=self.v_rH, onvalue=1, offvalue=0)
        bt_r_H.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rD = tk.IntVar()
        self.v_rD.set(0)
        bt_r_D = ttk.Checkbutton(self.criteria_frame_r, text = "D", variable=self.v_rD, onvalue=1, offvalue=0)
        bt_r_D.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rP = tk.IntVar()
        self.v_rP.set(0)
        bt_r_P = ttk.Checkbutton(self.criteria_frame_r, text = "P", variable=self.v_rP, onvalue=1, offvalue=0)
        bt_r_P.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rG = tk.IntVar()
        self.v_rG.set(0)
        bt_r_G = ttk.Checkbutton(self.criteria_frame_r, text = "G", variable=self.v_rG, onvalue=1, offvalue=0)
        bt_r_G.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rM = tk.IntVar()
        self.v_rM.set(0)
        bt_r_M = ttk.Checkbutton(self.criteria_frame_r, text = "M", variable=self.v_rM, onvalue=1, offvalue=0)
        bt_r_M.pack(side=tk.LEFT,padx = 2, pady = 2)
        sep_3 = ttk.Separator(self.criteria_frame_r, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        self.v_rB = tk.IntVar()
        self.v_rB.set(0)
        bt_r_B = ttk.Checkbutton(self.criteria_frame_r, text = "B", variable=self.v_rB, onvalue=1, offvalue=0)
        bt_r_B.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rF = tk.IntVar()
        self.v_rF.set(0)
        bt_r_F = ttk.Checkbutton(self.criteria_frame_r, text = "F", variable=self.v_rF, onvalue=1, offvalue=0)
        bt_r_F.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rK = tk.IntVar()
        self.v_rK.set(0)
        bt_r_K = ttk.Checkbutton(self.criteria_frame_r, text = "K", variable=self.v_rK, onvalue=1, offvalue=0)
        bt_r_K.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rW = tk.IntVar()
        self.v_rW.set(0)
        bt_r_W = ttk.Checkbutton(self.criteria_frame_r, text = "W", variable=self.v_rW, onvalue=1, offvalue=0)
        bt_r_W.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rV = tk.IntVar()
        self.v_rV.set(0)
        bt_r_V = ttk.Checkbutton(self.criteria_frame_r, text = "V", variable=self.v_rV, onvalue=1, offvalue=0)
        bt_r_V.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rX = tk.IntVar()
        self.v_rX.set(0)
        sep_4 = ttk.Separator(self.criteria_frame_r, orient='vertical').pack(side=tk.LEFT, fill='y',padx=8)
        bt_r_X = ttk.Checkbutton(self.criteria_frame_r, text = "X", variable=self.v_rX, onvalue=1, offvalue=0)
        bt_r_X.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rZ = tk.IntVar()
        self.v_rZ.set(0)
        bt_r_Z = ttk.Checkbutton(self.criteria_frame_r, text = "Z", variable=self.v_rZ, onvalue=1, offvalue=0)
        bt_r_Z.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rQ = tk.IntVar()
        self.v_rQ.set(0)
        bt_r_Q = ttk.Checkbutton(self.criteria_frame_r, text = "Q", variable=self.v_rQ, onvalue=1, offvalue=0)
        bt_r_Q.pack(side=tk.LEFT,padx = 2, pady = 2)
        self.v_rJ = tk.IntVar()
        self.v_rJ.set(0)
        bt_r_J = ttk.Checkbutton(self.criteria_frame_r, text = "J", variable=self.v_rJ, onvalue=1, offvalue=0)
        bt_r_J.pack(side=tk.LEFT,padx = 2, pady = 2)
        # ===END========= Require Letters =============




        self.settings_frame = ctk.CTkFrame(self,
                                           width=900,
                                           height=100,
                                           corner_radius=10,
                                           borderwidth=0)
        self.settings_frame.pack(side= tk.BOTTOM, fill=tk.X,  padx=20, pady=6)


        lb_allgreps = tk.Label(self.settings_frame,
                                textvariable=self.allgreps,
                                justify=tk.LEFT,
                                background='#dedede',
                                borderwidth=0,
                                highlightthickness=0)
        lb_allgreps.grid(row=3, column=0,  columnspan=6,  sticky='w', padx=6, pady=10)
        lb_allgreps.configure(font = Font_tuple)
        self.allgreps.set('=> AllGreps')



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
            self.allgreps.set("")
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
                                   command=do_grep)
        sw_no_dups.grid(row=0, column=2, padx=20, pady=6, sticky="W")


        self.bt_grep = ctk.CTkButton(self.settings_frame,
                                     text="Do Grep",
                                     command=do_grep)
        self.bt_grep.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        self.bt_Q = ctk.CTkButton(self.settings_frame, text="Quit", command=self.destroy)
        self.bt_Q.grid(row=3, column=7, columnspan= 1, padx=6, pady=6, sticky='e')

        do_grep()


# end pywordletool class

this_app = pywordletoolWND()
this_app.mainloop()
