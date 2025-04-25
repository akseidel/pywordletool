# fmwm.py

## Finite Monkey Wordle Machine (FMWM)

* The **Finite Monkey Wordle Machine** (**FMWM**) makes guesses in a certain way to calculate the average number of guesses required to solve a known **Wordle** word. The machine’s initial purpose is for measuring how hard a word is compared to another word or whether a certain guessing mode works better than another guessing mode.

* **FMWM** currently runs in console mode, ie without a GUI interface, and it relies on the **pywordletool** backend **helper.py** and **worddata** files. Simple **FMWM** operations can be run in an interactive console mode. The more advanced **FMWM** operations run only in a command argument console mode. Use the **-h** help argument to keep the help messages handy.
  
* **FMWM** will calculate the average number of guesses required to solve a known **Wordle** word in interactive console mode where it prompts you for the target **Wordle** word. It can also automatically process every word in the **Wordle** word vocabulary by using a command line argument. The results may be written to a text file for further processing.

* **FMWM** runs in a 'dumb monkey' mode and a 'smart monkey' mode. Dumb mode, otherwise called full random mode, guesses a random word, *selected from the current remaining words list*, for every guess step towards solving the target **Wordle** word. After each guess the pool of words for guess selection gets smaller and smaller according to what was learned by each previous guess. Thus, **FMWM** makes all it guesses in what is known as **Wordle** 'strict hard mode' where every green, yellow and grey clues are followed. Actual 'hard mode' does not follow grey clues and allows repeating yellow clues. The first pick can be any word from the entire **Wordle** ***solutions*** list. The second pick can be any word from the **Wordle** ***solutions*** list less any words ruled out by the first pick. Since **FMWM** knows the answer, it knows how to properly eliminate words. So proceeds **FMWM** until by chance it picks the solution out of what remains in the selection list or until only one word, the solution, remains. That process, referred as a 'run', ie a sample, is repeated many times to arrive at an average guesses. This full random mode provides the benchmark for word difficulty.

* An **FMWM** 'smart monkey' does not make random guesses, except for the first guess. Starting with the second guess, the **FMWM** 'smart monkey' guesses the selection pool’s highest ranked word. The first guess was random. That random first guess makes the selection pool for the second guess different for every run. Otherwise, **FMWM** would guess the same highest rank set of words in every run. The second guess is the top ranked word from the second guess pool. The selection pools are created in ranked order. The **FMWM** just picks the top word. The **FMWM** looks at that guess and rules out the right words to get the third guess selection pool. And so it goes just like before.

### Magic Words Finder

* WARNING NOTE: **FMWM**'s **magic word process** still has problems with candidate guesses that have multiple same letter situations with the target word. Any identified **magic word** that has multiple same letters should be regarded as suspect. The code does not properly build the require or exclude multiple letter grep arguments for most multiple same letter instances. This happens only for **FMWM**. There is no schedule as to when this will be fixed.

* The **FMWM** can find all the Order M Magic Words for any particular word. An Order 1 Magic Word is a word that reduces the possible guesses down to just the solution word. In other words a Magic Word used as a first guess, or as any guess, played in hard mode, forces the next fitting guess to be the solution. Likewise, an Order 2 Magic Word reduces the possible guesses to two words, one of which is the solution word. Magic word finding is initiated using the command line arguments **-m M**. See the **Command Line Options** section below for more information. (Note: Actual 'hard mode' does not follow grey clues. 'hard mode' here requires following every green, yellow and grey clue.)

### Requirements To Run FMWN

* **FMWM** is a **python** program, and it relies on utilities that are typically present in UNIX, Apple OSX and Linux operating systems. Therefore, a recent **python** installation on any UNIX, Apple OSX or Linux operating system computer is the requirement. For Windows based computers a Linux subsystem would need to be installed with **python** installed within it. **FMWM** would need to be run within that Linux subsystem.

### How to run fmwm

* Run **FMWM** in a Terminal window using the command: **python3 fmwm.py**

### Running Options

* **FMWM** prompts for the target word.
* **FMWM** prompts for an optional first guess word. In other words you can specify the word used for the first guess instead of **FMWM** making a random first guess word.
* **FMWM** prompts for the running mode. This can be **Random** where all guesses are random words, or it can be a **Ranked** mode where each guess, starting with the second guess if no first guess option is used, uses one of the three **Ranking** schemes as used in **The Wordle Helper**, i.e. **pywt.py**, program.

* A standard run interactive output looks like this:

```text
python3 fmwm.py
Enter a valid Wordle target word: covet
Run using a given first guess? Enter y/n: n
Guess Type? Random(0), or Rank by Occurrence (1), Position (2) or Both (3), Best Entropy (4) Enter 0,1,2,3 or 4: 1
1 word:covet  Average guesses to solve Wordle by sampling 100 tries.
target wrd: covet, 100 samples, rank mode type 1 guesses, initial duplicates:False, botadd_nyt_wordlist.txt
target wrd: covet, averaged 4.850 guesses to solve, 100 samples, rank mode type 1 guesses, initial duplicates:False, botadd_nyt_wordlist.txt, 7.9480 seconds
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
  -r {0,1,2,3,4}  Guess type: Random(0),Rank Occurrence (1),Rank Position (2), Both (3) or Entropy (4)
  -x X          Override the number of sampling runs to be this number X.
  -v            For guessing, use the Wordle vocabulary that includes non-solution words.
  -z            For word targets, use the Wordle vocabulary that includes non-solution words.
  -w            Writes output to CSV file having a timestamp filename.
  -a            Process every vocabulary word as a target word.
  -q Q          Show guesses that solve on the Qth guess.
  -m M          Find the order M magic words for a target word.
  -p P          Pick-up, ie. resume, after seeing word P.
```

* **-h** Displays the help hints as shown above.
* **-d** Prints out all the word lists at each step, the guesses and other data.
* **-l** Lists out only the guess data and resulting pool sizes for each solution run. For example: [3, 4, 'feast', 'wrack', 106, 'blaze', 8, 'heath', 3, 'feast', 1]
* **-n** Skips asking for a specified first guess.
* **-t T** Solve for a target word as in **-t happy**.
* **-s S** Use this first guess word as in **-t stale**.
* **-r {0,1,2,3,4}** Specify the guessing type. **-r 0** means random guesses for all guesses. **-r 1** means rank 1 type guesses and so on.
* **-x X** Sets the number of sample runs other than the default 100. **-x 1000** would specify 1000 runs.
* **-v** For guessing purposes only, use the Wordle vocabulary that includes non-solution words in addition to solution words. By default, the solutions only list is used. When processing all the words in the list, it is the solutions only list that is processed, but the pool from which guesses are selected can be either the default solutions list or the larger list that also includes words that would never be a solution. The solutions list is the original Wordle solution words, less some words removed by the New York Times, plus words added by the New York Times to accommodate the New York Time WordleBot.
* **-z** For targeting purposes, use the entire Wordle vocabulary that includes non-solution words.
* **-w** Writes the output to a CSV file in addition to showing in the Terminal. The CSV file is timestamp named, so it will always be unique, and it will reside at the directory that holds **fmwm.py**.
* **-a** Processes every vocabulary word (originally 2309 words, now 3189 words) in the solutions list as each target word.
* **-q Q** Lists out only the guess data for runs that result in **Q** guesses. For example **-q 2** outputs only the guess data for runs where the target word is solved in two guesses. In other words after the first guess, only the target word remains.
* **-m M** Finds words from the vocabulary that are order **M** magic word's for the target word. Order 1 magic words reduce the selection pool to contain only the target word. A magic word first guess forces the second guess to be the solution. Order 2 magic words reduce the selection pool to two words where there would be a 50% chance to guess the solution. Order **M** magic words reduce the selection pool to **M** words. By default, **fmwm.py** selects first word guesses from the **Classic+**, ie possible solutions word list. Use the additional **-v** argument to also select from the larger non-solutions list. Be aware, currently the magic word feature does not find all the magic words for target words that contain multiple instances of any letter.
* **-p P** Picks up, i.e. restarts, a vocabulary process after the word **P**. Depending on the process type and its settings, a vocabulary process can take over a day to complete. If for some reason such a process was terminated early after yielding valid data, that process can be restarted after the last valid word data in the previously terminated process. You provide that word as the **P** argument. If .csv files were being made, the restarted run will be a new .csv file with the **P** argument as part of the filename. 
* **-z** Applies only for the **magic word** process. **-z** sets the entire allowed Wordle guess list to be a possible solution when finding **magic words**. Its use is limited to being a puzzle exercise for understanding why **magic words** discovered this way do not overlap with those **magic words** discovered for the solution list that we know is a subset of the larger list.  

Command line use example:

```text
python3 fmwm.py -l -n -t feast -r 0 -x 4
1 word:feast  Average guesses to solve Wordle by sampling 4 tries.
target wrd: feast, 4 samples, random guesses, initial duplicates:True, botadd_nyt_wordlist.txt
[1, 5, 'feast', 'flung', 65, 'freed', 3, 'femme', 2, 'fetch', 1, 'feast']
[2, 4, 'feast', 'divot', 118, 'chest', 4, 'beast', 3, 'feast', 1]
[3, 5, 'feast', 'ebony', 743, 'stele', 10, 'reset', 3, 'heist', 1, 'feast']
[4, 3, 'feast', 'timed', 133, 'chest', 4, 'feast', 1]
target wrd: feast, averaged 4.250 guesses to solve, 4 samples, random guesses, initial duplicates:True, botadd_nyt_wordlist.txt, 0.2469 seconds
```

In the above example the **-l** argument 'Lists each solution run data' during the **FMWM** operations in square brackets. The **-x 4** argument specifies to run the process 4 times.

* The first number is the run number.
* The second number is the number of guesses required to solve in that run.
* The first quoted word is the target word.
* The following quoted words are the guess words.
* The number following each guess word is the selection pool size remaining after applying the results of the guess. 

In run #1 the guess word 'shown' resulted in a 122 word selection pool. In run #1 the last quoted guess 'flask' is the third guess. One knows that because it resulted in one remaining selection pool word, and it is also not the target word. Target words are first verified to be present in the solutions list. Therefore, the target word has to be the word in a one word selection pool that filters for the target word. In run #1 that word could only be 'feast' and thus the third required guess would select it. **FMWM** knows this, and thus it does not need to proceed another step in the guessing process.

Run #2 and Run #4 are similar to Run #1 in that they also result in a single word remaining situation whereupon 'feast' would be the final guess.

Runs #3 shows the outcome of a 1/3 chance of guessing the solution from a list of three words. Run #3, starting with 'wrack', eventually narrowed the word options to three words after the third guess 'heath'. The next guess 'feast' was the correct guess. The hallmark for a correct guess is it being the target word and also resulting in 1 remaining pool word.

#### Processing the Entire Wordle Vocabulary List

* The **-a** command line argument runs **FMWM** so that it processes every word in the vocabulary list. The **-w** command line argument writes output a CSV text file. Thus **-a** used in combination with the **-w** saves all results in one CSV text file. The filename is automatically generated in a timestamped fashion. The timestamped named file will reside in the directory where **fmwm.py** is located.
* Output also continues to the Terminal window. The output includes an estimate for how long it will take to complete the process.
* Use the **-x X** command line argument to set the number of sample tries for each word. The default value of 100 sample tries may not have the resolution you want. About 400 tries, ie **-x 400**, results in about 0.1 resolution. Sampling 400 times per word will take many hours to process the entire solutions word list.
* During the **-a** processes of every word in the vocabulary list, **FMWM** includes in the Terminal window output an estimated time to finish **(ETF)** value. The **ETF** shows up after the first word is finished. This estimated time is how long it will be until the process is complete. It is the average time per word at the moment multiplied by the number of words remaining to be processed.
* This is a typical output to the Terminal window where the word **least** is designated as the first guess:

```text
Duration so far: 0:00:01.803758, avg. 0.9019 s/wrd, last word 0.8587 s/wrd, ETF: 0:45:36.696644
Output being written to R0_X20_S_least_2024-09-21_13_23_10.730536.csv
3 word:abash  Average guesses to solve Wordle by sampling 20 tries.
target wrd: abash, 20 samples, random guesses, initial duplicates:True , first guess:least, botadd_nyt_wordlist.txt
target wrd: abash, averaged 3.900 guesses to solve, 20 samples, random guesses, initial duplicates:True , first guess:least, botadd_nyt_wordlist.txt, 0.9217 seconds

Duration so far: 0:00:02.725501, avg. 0.9085 s/wrd, last word 0.9217 s/wrd, ETF: 0:48:56.672223
Output being written to R0_X20_S_least_2024-09-21_13_23_10.730536.csv
4 word:abate  Average guesses to solve Wordle by sampling 20 tries.
target wrd: abate, 20 samples, random guesses, initial duplicates:True , first guess:least, botadd_nyt_wordlist.txt
target wrd: abate, averaged 3.350 guesses to solve, 20 samples, random guesses, initial duplicates:True , first guess:least, botadd_nyt_wordlist.txt, 0.9479 seconds
```

* The CSV output written to file for the first two words is this:

```text
target wrd,average,guess mode,initial duplicates,first guess,vocabulary,samples,seconds
abash,3.9,random guesses,True,least,botadd_nyt_wordlist.txt,20,0.9217426939867437
abate,3.35,random guesses,True,least,botadd_nyt_wordlist.txt,20,0.9478941340057645
```

* In comparison, the CSV output written to file for the first two words using 400 tries shows different guess averages but the same general character:

```text
target wrd,average,guess mode,initial duplicates,first guess,vocabulary,samples,seconds
abash,4.015,random guesses,True,least,botadd_nyt_wordlist.txt,400,21.758871527999872
abate,3.505,random guesses,True,least,botadd_nyt_wordlist.txt,400,22.562121423019562
```

* 400 samples is not large enough to compare words with this measure at the 1/10th of a guess resolution.

* Use the keypress combination **control + C** to stop the **FMWM** prior to its own process completion.

#### Random Mode versus Ranked Mode Inner Workings

**Random** mode Wordle solving is intended to be the benchmark against which all other Wordle solving methods are to be compared. As such **Random** mode needs to be a base level of play lacking any sophistication. Therefore, **Random** mode makes all its guesses random words, and it makes all guesses without regard to when the guess occurs in the play or whether the guess contains multiple occurring letters.

**Ranked** mode on the other hand is intended to model some level of play sophistication. Most reasonable Wordle play does not allow guesses having multiple occurring letters until the third guess. This is what **FMWM** does. If Wordle solutions never had multiple occurring letters then multiple occurring letters would always be excluded. But for **FMWM** to work properly the solution word must be present in the selection pool. For speed purposes **FMWM** lacks code for noticing a dwindling selection pool that would be a basis for effecting an inclusion multiple occurring letters change. Often the number of words containing multiple occurring letters is small after the second guess. Therefore, allowing multiple occurring letters by the third guess is a reasonable compromise.
