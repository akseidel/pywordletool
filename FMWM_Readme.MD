# fmwm.py

## Finite Monkey Wordle Machine (fmwm)

* The **Finite Monkey Wordle Machine** (**FMWM**) makes guesses in a certain way to calculate the average number of guesses required to solve a known **Wordle** word. The machine’s purpose is for measuring how hard a word is compared to another word or whether a certain guessing mode works better than another guessing mode.

* **FMWM** currently runs in console mode, ie without a GUI interface, and it relies on the **pywordletool** backend **helper** and **worddata** files.

* **FMWM** will calculate the average number of guesses required to solve a known **Wordle** word in interactive mode where it prompts you for the target **Wordle** word. It can also automatically process every word in the **Wordle** word vocabulary by using a command line argument. The results may be written to a text file for further processing.

* **FMWM** runs in a 'dumb monkey' mode and a 'smart monkey' mode. Dumb mode, otherwise called full random mode, guesses a random word in every guess step towards solving the target **Wordle** word. After each guess the pool of words for guess selection gets smaller and smaller according to what was learned by each previous guess. **FMWM** makes all it guesses in what is known as **Wordle** 'hard mode'. The first pick can be any word from the entire **Wordle** ***solutions*** list. Their second pick can be any word from the **Wordle** ***solutions*** list less any words ruled out by the first pick. Since **FMWM** knows the answer, it knows how to properly eliminate words. And so on it goes until the **FMWM** by chance picks the solution out of what remains in the selection list or until only one word, the solution, remains. That process, referred as a 'run', ie a sample, is repeated many times to arrive at an average guesses. This full random mode provides the benchmark for word difficulty.

* An **FMWM** 'smart monkey' does not make random guesses, except for the first guess. Starting with the second guess, the **FMWM** 'smart monkey' guesses the selection pool’s highest ranked word. The first guess was random. That random first guess makes the selection pool for the second guess different for every run. Otherwise the **FMWM** would guess the same highest rank set of words in every run. The second guess is the top ranked word from the second guess pool. The selection pools are created in ranked order. The **FMWM** just picks the top word. The **FMWM** looks at that guess and rules out the right words to get the third guess selection pool. And so it goes just like before.

### Requirements To Run IMWN

* **FMWM** is a **python** program and it relies on utilities that are typically present in UNIX, Apple OSX and Linux operating systems. Therefore a recent **python** installation on any UNIX, Apple OSX or Linux operating system computer is the requirement. For Windows based computers a Linux subsystem would need to be installed with **python** installed within it. **FMWM** would need to be run within that Linux subsystem.

### How to run fmwm

* Run **FMWM** in a Terminal window using the command: **python3 fmwm.py**

### Running Options

* **FMWM** prompts for the target word.
* **FMWM** prompts for an optional first guess word. In other words you can specify the word used for the first guess instead of **FMWM** making a random first guess word.
* **FMWM** prompts for the running mode. This can be **Random** where all guesses are random words or it can be a **Ranked** mode where each guess, starting with the second guess if no first guess option is used, uses one of the three **Ranking** schemes as used in **The Wordle Helper**, i.e. **pywt.py**, program.

* A standard run interactive output looks like this:

```text
python3 fmwm.py

1 word: Average guesses to solve Wordle by sampling 100 tries.
Enter a valid Wordle target word: covet
Run using a given first guess? Enter y/n: n
Guess Type? Random(0), or Rank by Occurrence (1), Position (2) or Both (3), Enter 0,1,2 or 3: 1
target_wrd: covet, 100 samples, rank mode type 1 guesses, initial duplicates:False, wo_nyt_wordlist.txt
target_wrd: covet, averaged 4.480 guesses to solve, 100 samples, rank mode type 1 guesses, initial duplicates:False, wo_nyt_wordlist.txt, 4.4157 seconds
```

* Verbose output revealing the guess data during each run is possible when running **FMWM** with command line arguments.

#### Command Line Options

This is the help hints for the command line arguments:

```text
usage: fmwm.py [-h] [-d] [-l] [-n] [-t T] [-s S] [-r {0,1,2,3}] [-x X] [-v]

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
  -v            For guessing, use the Wordle vocabulary that includes non-solution words.
  -w            Writes output to CVS file having a timestamp filename.
  -a            Process every vocabulary word as a target word.
```

A use example:

```text
python3 fmwm.py -l -n -t feast -r 0 -x 4
1 word: Average guesses to solve Wordle by sampling 4 trys.
target_wrd: feast, 4 samples, random guesses, initial duplicates:True, wo_nyt_wordlist.txt
[1, 3, 'feast', 'shown', 122, 'flask', 1]
[2, 3, 'feast', 'mafia', 33, 'fecal', 1]
[3, 4, 'feast', 'wrack', 106, 'blaze', 8, 'heath', 3, 'feast', 1]
[4, 5, 'feast', 'lodge', 256, 'teary', 4, 'meant', 2, 'beast', 1]
target_wrd: feast, averaged 3.750 guesses to solve, 4 samples, random guesses, initial duplicates:True, wo_nyt_wordlist.txt, 0.1681 seconds
```

In the above example the **-l** argument 'Lists each solution run data' during the **FMWM** operations in square brackets. The first number is the run number. The second number is the number of guesses required to solve in that run. The first quoted word is the target word. The following quoted words are the guess words. The number following each guess word is the selection pool size remaining after applying the results of the guess. In run #1 the guess word 'shown' resulted in a 122 word selection pool. In run #1 the last quoted guess 'flask' is the third guess. One knows that because it resulted in one remaining selection pool word and it is also not the target word. Target words are first verified to be present in the solutions list. Therefore the target word has to be the word in a one word selection pool that filters for the target word. In run #1 that word could only be 'feast' and thus the third required guess would select it. **FMWM** knows this and thus it does not need to proceed another step in the guessing process.

Run #2 and Run #4 are similar to Run #1 in that they also result in a single word remaining situation whereupon 'feast' would be the final guess.

Runs #3 shows the outcome of a 1/3 chance of guessing the solution from a list of three words. Run #3, starting with 'wrack', eventually narrowed the word options to three words after the third guess 'heath'. The next guess 'feast' was the correct guess. The hallmark for a correct guess is it being the target word and also resulting in 1 remaining pool word.

#### Processing the Entire Wordle Vocabulary List

* The **-a** command line argument runs **FMWM** so that it processes every word in the vocabulary list. The **-w** command line argument writes output a CVS text file. Thus **-a** used in combination with the **-w** saves all results in one CVS text file. The filename is automatically generated in a timestamped fashion. The timestamped named file will reside in the directory where **fmwm.py** is located.
* Output also continues to the Terminal window. The output includes an estimate for how long it will take to complete the process.
* Use the **-x X** command line argument to set the number of sample tries for each word. The default value of 100 sample tries may not have the resolution you want. About 400 tries, ie **-x 400**, results in about 0.1 resolution. Sampling 400 times per word will take many hours to process the entire solutions word list.
* During the **-a** processes of every word in the vocabulary list, **FMWM** includes in the Terminal window output an estimated time to finish **(ETF)** value. The **ETF** shows up after the first word is finished. This estimated time is how long it will be until the process is complete. It is the average time per word at the moment multiplied by the number of words remaining to be processed.
* This is a typical output to the Terminal window where the word **least** is designated as the first guess:
```text
Duration so far: 27.1431 seconds, 0.9360 seconds/word, ETF: 0:35:34.008221 
Output being written to 2022-11-25_16_19_15.055581.csv
30 word: Average guesses to solve Wordle by sampling 20 tries.
target_wrd: muddy, 20 samples, random guesses, initial duplicates:True , first guess:least, wo_nyt_wordlist.txt
target_wrd: muddy, averaged 4.700 guesses to solve, 20 samples, random guesses, initial duplicates:True , first guess:least, wo_nyt_wordlist.txt, 0.9364 seconds

Duration so far: 28.0795 seconds, 0.9360 seconds/word, ETF: 0:35:33.104436 
Output being written to 2022-11-25_16_19_15.055581.csv
31 word: Average guesses to solve Wordle by sampling 20 tries.
target_wrd: puppy, 20 samples, random guesses, initial duplicates:True , first guess:least, wo_nyt_wordlist.txt
target_wrd: puppy, averaged 4.550 guesses to solve, 20 samples, random guesses, initial duplicates:True , first guess:least, wo_nyt_wordlist.txt, 0.9660 seconds
```
* The CVS output written to file for the first two words is this:
```text
target wrd,average,guess mode,initial duplicates,first guess,vocabulary,samples,seconds
fuzzy,5.05,random guesses,True,least,wo_nyt_wordlist.txt,20,0.9627162480028346
fizzy,4.65,random guesses,True,least,wo_nyt_wordlist.txt,20,0.9443350170040503
```
* In comparison, the CVS output written to file for the first two words using 400 tries shows different guess averages but the same general difference order:
```text
target wrd,average,guess mode,initial duplicates,first guess,vocabulary,samples,seconds
fuzzy,4.88,random guesses,True,least,wo_nyt_wordlist.txt,400,19.977324250969104
fizzy,4.6,random guesses,True,least,wo_nyt_wordlist.txt,400,19.74195557308849
``` 

* Use the keypress combination **control + C** to stop the **FMWM** prior to its own process completion.

#### Random Mode versus Ranked Mode Inner Workings

**Random** mode Wordle solving is intended to be the benchmark against which all other Wordle solving methods are to be compared. As such **Random** mode needs to a base level of play lacking any sophistication. Therefore **Random** mode makes all its guesses random words and it makes all guesses without regard to when the guess occurs in the play or whether the guess contains multiple occurring letters.

**Ranked** mode on the other hand is intended to model some level of play sophistication. Most reasonable Wordle play does not allow guesses having multiple occurring letters until the third guess. This is what **FMWM** does. If Wordle solutions never had multiple occurring letters then multiple occurring letters would always be excluded. But for **FMWM** to work properly the solution word must be present in the selection pool. For speed purposes **FMWM** lacks code for noticing the dwindling selection pool might or does lack the solution to effect the inclusion change. Often the number of words containing multiple occurring letters is small after the second guess. Therefore allowing multiple occurring letters by the third guess is a reasonable compromise.
