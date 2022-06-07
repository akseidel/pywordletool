# pywt.py

## A python based wordle game helper

!['Main Window Image'](InfoImages/PYWTMainWindow.png)
!['Help Window Image'](InfoImages/PYWTHelp.png)
!['In use Image Image'](InfoImages/PYWTInUse.png)

#### What To Expect From This Helper

* Expect nothing more than a helper with a thorough vocabulary that presents words only matching the letters you specify.  

#### Running the wordle helper

* Open a **Terminal** window
* Change to the folder where you placed **pywy.py** and the other files and folders.
* Enter the command: ```python3 pywt.py```
* For Apple OSX and Linux systems double-clicking the **start-pywt.command** file in the **Finder** also starts the wordle helper.

#### Requirements

* python3: (<https://www.python.org/downloads/>)
* pip: (<https://pypi.org/project/pip/>)
* customtkinter

'tkinter' provides graphical user interface support for python applications. It comes with python. 'customtkinter' is an expansion to 'tkinter'. This wordle game helper uses some customtkinter features and so it needs to be installed along with python3. 'pip' is python's utility for installing components like 'customtkinter'. 'pip' needs to be installed in order to install customtkinter.

After installing python3 and pip, the following commands entered in a Terminal window will install 'customtkinter':
`pip3 install customtkinter`

#### Installing the wordle helper

* Download the **pywtpackage.zip** release file from the repository releases link.
* Unzip the **pywtpackage.zip** release file. It should unzip to be a folder named pywtpackage.
* Rename the **pywtpackage** folder as you wish and place the folder with its contents to where you would like to keep it.
* A file privilege for the **start-pywt.command** double-click-to-run convenience file needs to be changed for it to work. Use the command: ```chmod +x start-pywt.command``` executed in Terminal, at the file's folder, to make the change.
* This **README.md** file, the images it uses and a couple of files in the **worddata** folder regarding letter ranking may be deleted if desired. The only required files, and their associated folder, that are in **pywtpackage.zip** are:
  * **start-pywt.command**  (the double-click-to-run convenience file)
  * **pywt.py**             (the app.)
  * **helpers.py**          (a helper to the app.)
  * **helpinfo.txt**        (help information)
  * **letter_ranks.txt**    (letter ranking)
  * **nyt_wordlist.txt**    (wordlist - shuffled)
  * **wo_nyt_wordlist.txt** (wordlist - shuffled)
