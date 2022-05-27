# get customtkinter  -> pip3 install customtkinter
# if already, may need to upgrade it -> pip3 install customtkinter --upgrade
# from tkinter import *

import tkinter as tk  # assigns tkinter stuff to tk namespace so that it may be separate from ttk
# import tkinter.ttk as ttk  # assigns tkinter.ttk stuff to its own ttk namespace so that tk is preserved
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


# customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

def tk_q(self):
    pass


# self.quit()

def do_grep():
    print("do grep")
    # this_app.bt_grep(text = "What")


class pywordletool(customtkinter.CTk):
    # global do_grep
    global switch_var

    def __init__(self):
        super().__init__()
        self.title("This Wordle Tool")
        w_width = 600
        w_height = 400
        pos_x = int( self.winfo_screenwidth()/2 - w_width/2 )
        pos_y = int( self.winfo_screenheight()/2 - w_height/2 )
        self.geometry("{}x{}+{}+{}".format(w_width, w_height, pos_x, pos_y))

        self.frame = customtkinter.CTkFrame(master=self,
                                            width=580,
                                            height=200,
                                            corner_radius=10,
                                            relief='sunken',
                                            borderwidth=2)
        # self.frame.pack(padx=20, pady=20, sticky="nsew")
        # self.frame.pack(padx=20, pady=20)
        self.frame.grid(row=0, column=0, rowspan=1, columnspan=2, padx=6, pady=6)

        text_var = tk.StringVar(value="The grep output goes here. And it goes. And goes. And Goes.")

        t = tk.Text(self.frame,
                    wrap='word'

                    )

        t.grid(row=0, column=0, rowspan=1, columnspan=2, padx=4, pady=4)

        t.insert( 1.0, text_var.get())

        gr_output = customtkinter.CTkLabel(master=self.frame,
                                           textvariable=text_var,
                                           width=578,
                                           height=200,
                                           fg_color=("white", "gray75"),
                                           corner_radius=0
                                           )
        # gr_output.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        gr_output.grid(row=1, column=0, rowspan=1, columnspan=2, padx=2, pady=2)

        # self.e = customtkinter.CTkEntry(self,width = 34, borderwidth=2,readonlybackground="")
        # self.e.pack(row=0,column=0,columnspan=1,padx=10,pady=10)
        #
        # self.label2 = customtkinter.CTkLabel(self, text ="Helps you do a wordle.").grid(row=2, column=0, padx=10, pady=6)
        #
        self.bt_grep = customtkinter.CTkButton(master=self,
                                               text="Do Grep",
                                               # command=(lambda: self.bt_grep.set_text("Changed This To Be Long"))
                                               command=do_grep()
                                               )
        self.bt_grep.grid(row=1, column=1)
        # self.bt_Q = customtkinter.CTkButton(self, text = "Quit",  command=tk_q(self))
        #
        # self.bt_Q.pack(row=3,column=2,padx= 6,pady=6)

        switch_var = tk.StringVar(value="off")   # starting value

        def switch_event():
            pass
            # print("switch toggled, current value:", switch_1.get())

        switch_1 = customtkinter.CTkSwitch(master=self,
                                           text="Allow Duplicate Letters",
                                           command=switch_event,
                                           variable= switch_var,
                                           onvalue="on",
                                           offvalue="off"
                                           )
        switch_1.grid(row=2, column=0, padx= 6, pady=6, sticky="W")


this_app = pywordletool()
this_app.mainloop()
