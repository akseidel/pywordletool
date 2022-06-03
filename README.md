# pywt.py

## A python based wordle game helper

!['Main Window Image'](InfoImages/PYWTMainWindow.png)
!['Help Window Image'](InfoImages/PYWTHelp.png)

#### Requirements

* python3: (<https://www.python.org/downloads/>)
* pip: (<https://pypi.org/project/pip/>)
* customtkinter

'tkinter' provides graphical user interface support for python applications. It comes with python. 'customtkinter' is an expansion to 'tkinter'. This wordle game helper uses some customtkinter features and so it needs to be installed along with python3. 'pip' is python's utility for installing components like 'customtkinter'. 'pip' needs to be installed in order to install customtkinter.

After installing python3 and pip, the following commands entered in a Terminal window will install 'customtkinter':

`pip3 install customtkinter`

#### Installing the wordle helper

* Create a folder for holding the wordle helper.
* Place the two files pywt.py and helpers.py into that folder.
* Create a folder named **worddata** inside the same folder where the two files *pywt.py* and *helpers.py* were placed. The folder **worddata** is where the wordle helper expects to find its word lists, ranking list and its help text file.
* Place the two *\*nyt_wordlist.txt* files, the *letter_ranks.txt* file and the *helpinfo.txt* into the **worddata** folder. These four files are required by the wordle helper.

#### Running the wordle helper

* Open a Terminal window
* Change to the folder where you placed **pywy.py**.
* Enter the command **python3 pywt.py**
