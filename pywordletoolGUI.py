from tkinter import *


def tk_q():
    root.destroy()

root = Tk()

root.title("This Wordle Tool")
root.geometry("600x400")
root.configure(bg='blue')

my_frame = LabelFrame(root,text="Results",pady=10,padx=10, borderwidth=4)
my_frame.grid(row=0,column=0,rowspan=1,columnspan=1,padx=10,pady=10)
# my_frame.pack(padx=10,pady=10)

e = Entry(my_frame,width = 34, borderwidth=2,readonlybackground="")
e.grid(row=0,column=0,columnspan=1,padx=10,pady=10)



my_label1 = Label(root, text = "Wordle Tool").grid(row=1,column=0,padx=10,pady=6)
my_label2 = Label(root, text = "Helps you do a wordle.").grid(row=2,column=0,padx=10,pady=6,sticky=E)

# my_label1.grid(row=0,column=0,padx=10,pady=10)
# my_label2.grid(row=2,column=1,pady=10)



my_button = Button(my_frame, text = "Do Grep").grid(row=3,column=1,padx= 6,pady=6)
bt_Q = Button(my_frame, text = "Quit", font=(24), command=tk_q)
bt_Q.grid(row=3,column=2,padx= 6,pady=6)

root.mainloop()

