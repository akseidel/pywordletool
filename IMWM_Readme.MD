# imwm.py

### Infinite Monkey Wordle Machine (IMWM)

* The **Infinite Monkey Wordle Machine** (**IMWM**)makes guesses in a certain way to calculate the average number of guesses required to solve a known **Wordle** word. The machine’s purpose is for measuring how hard a word is compared to another word or whether a certain guessing mode works better than another guessing mode.

* **IMWM** currently run in console mode, ie without a GUI interface, and it relies on the **pywordletool** backend **helper** and **worddata** files.

* **IMWM** runs in a 'dumb monkey' mode and a 'smart monkey' mode. Dumb mode, otherwise called full random mode, guesses a random word in every guess step towards solving the target **Wordle** word. After each guess the pool of words for guess selection gets smaller and smaller according to what was learned by each previous guess. **IMWM** makes all it guesses in what is known as **Wordle** 'hard mode'. The first pick can be any word from the entire **Wordle** ***solutions*** list. Their second pick can be any word from the **Wordle** ***solutions*** list less any words ruled out by the first pick. Since **IMWM** knows the answer, it knows how to properly eliminate words. And so on it goes until the **IMWM** by chance picks the solution out of what remains in the selection list or until only one word, the solution, remains. That process, referred as a 'run', ie a sample, is repeated many times to arrive at an average guesses. This full random mode provides the benchmark for word difficulty.

* An **IMWM** 'smart monkey' does not make random guesses, except for the first guess. Starting with the second guess, the **IMWM** 'smart monkey' guesses the selection pool’s highest ranked word. The first guess was random. That random first guess makes the selection pool for the second guess different for every run. Otherwise the **IMWM** would guess the same highest rank set of words in every run. The second guess is the top ranked word from the second guess pool. The selection pools are created in ranked order. The **IMWM** just picks the top word. The **IMWM** looks at that guess and rules out the right words to get the third guess selection pool. And so it goes just like before.

### Requirements To Run IMWN

* **IMWM** is a **python** program and it relies on utilities that are typically present in UNIX, Apple OSX and Linux operating systems. Therefore a recent **python** installation on any UNIX, Apple OSX or Linux operating system computer is the requirement. For Windows based computers a Linux subsystem would need to be installed with **python** installed within it. **IMWM** would need to be run within that Linux subsystem.

### How to run IMWM

* Run **IMWM** in a Terminal window using the command: **python3 imwm.py**

### Running Options

* **IMWM** prompts for the target word.
* **IMWM** prompts for an optional first guess word. In other words you can specify the word used for the first guess instead of **IMWM** making a random first guess word.
* **IMWM** prompts for the running mode. This can be Random where all guesses are random words or it can be a Ranked mode where each guess, starting with the second guess if no first guess option is used, uses one of the three Ranking schemes as used in **The Wordle Helper**, i.e. **pywt.py**, program.

* A standard run output looks like this:

```text
Average guesses to solve Wordle sampling
Enter a valid Wordle target word: covet
Run using a given first guess? Enter y/n: n
Guess Type? Random(0), or Rank by Occurrence (1), Position (2) or Both (3), Enter 0,1,2 or 3: 2
target_wrd: covet
100 runs, rank mode 1 guesses, initial allow duplicates: False
target_wrd: covet , averaged 3.950 guesses to solve. 100 runs, rank mode 1 guesses, initial allow duplicates: False
```

* Verbose output revealing the guess data during each run is possible when running **IMWM** with command line arguments.

#### Command Line Options

This is the help hints for the command line arguments:
```text
usage: imwm.py [-h] [-d] [-l] [-n] [-t T] [-s S] [-r {0,1,2,3}] [-x X] [-v]

Process command line settings.

options:
  -h, --help    show this help message and exit
  -d            Prints out lists, guesses etc.
  -l            Lists each solution run data
  -n            Random first guess word, ie skip asking about it
  -t T          Use this target word T.
  -s S          Use this first guess word S.
  -r {0,1,2,3}  Guess type: Random(0),Rank Occurrence (1),Rank Position (2) or Both (3)
  -x X          Override the number of sampling runs to be this number X.
  -v            Use the Wordle vocabulary that includes non-solution words.
```
Here is a use example:

```text
% python3 imwm.py -l -n -t covet -r 0 -x 4

Average guesses to solve Wordle sampling
target_wrd: covet
4 runs, random guesses, initial allow duplicates: True
1 5 ['covet', 'excel', 25, 'crier', 8, 'cadet', 2, 'comet', 1]
2 2 ['covet', 'decry', 64, 'covet', 1]
3 4 ['covet', 'lapel', 159, 'sober', 14, 'coven', 2, 'covet', 1]
4 5 ['covet', 'kebab', 455, 'snipe', 84, 'lover', 2, 'covey', 1]
target_wrd: covet , averaged 4.000 guesses to solve. 4 runs, random guesses, initial allow duplicates: True
```
In the above example the **-l** argument 'Lists each solution run data'. The first number is the run number. The second number is the number of guesses required to solve in that run. The first quoted word is the target word. The following quoted words are the guess words. The number following each guess word is the selection pool size remaining after applying the results of the guess. The guess word 'excel' resulted in a 25 word selection pool. Note the last quoted guess 'comet' is the fourth guess. It resulted in one remaining word.  That word would have been 'covet' and thus the fifth required guess.

In contrast to the first run described above the second run solutions list shows 'covet' as the second guess. In this run the solution 'covet' was picked at random from a pool of 64 words. The knowledge gained by its letters combined with that of the previous guess 'decry' results in only one possible word. That is the hallmark of a correct guess.

The last two runs show the two outcomes of a 50% chance of guessing the solution from a list of two words. The third run, 'lapel', narrowed the word options to two words after the third guess 'coven'. The solution 'covet' was the next pick. A similar situation occurred in the fourth, 'kebab', run. There 'covey' was guessed after 'lover' narrowed the selection to two words leaving only the solution for the fifth guess.