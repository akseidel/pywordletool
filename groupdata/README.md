### All Guess Words Groups Stats

#### Introduction

* The [AllGuessWordsGroupsStats.csv.txt](/groupdata/AllGuessWordsGroupsStats.csv.txt) is a comma separated value format text file summarizing the word grouping performance for every word in the Wordle allowed guess word list used as a guess ***for the starting state where every possible Wordle solution can be the days' Wordle solution***. Data is based upon using the classic 2,309 possible Wordle solutions.

* The data can help one evaluate the merit for a game's first word only. After the first guess is played the list of possible Wordle solutions reduces to a list of remaining possible Wordle solutions. **AllGuessWordsGroupsStats.csv.txt** no longer applies after the first guess.  

* Data is sorted according to the number of word groups generated (descending), then by the maximum group size (ascending) and then by the average group size (ascending).

* The list columns are:
  * guess - This is the guess word.
  * qty   - The number of word groups the guess divides the possible Wordle solution words. As of this file there are 2309 solution words. The guess word identically matches or mismatches all the words in each word group.
  * min   - The number of words in the smallest word group.
  * max   - The number of words in the largest word group. The largest word group is often the words having nothing in common with the guess word.
  * ave   - The average size of all the word groups.
  * wrds/max    - The number of times larger the 2039 solution word is above the maximum group size. This value may have no bearing on the guess's merit, but it does provide a comparison means.

* The **Group Driller** **Condensed** verbose output created the content shown in this list.

#### Observations

* The data is sorted first by group quantity and then by maximum group quantity. As such the better guess, measured by the maximum group quantity, amongst those words generating the same number of groups as a category are the words in that category having the most commonly used letters "AE,NOSTRIL". Such words would be the best guess within the quantity category. This characteristic is what results in the red stripes seen in the graphed data.

#### [AllGuessWordsGroupsStats.csv.txt](/groupdata/AllGuessWordsGroupsStats.csv.txt)

#### This Data Graphed

!['All Guess Words Groups Graphed.png Image'](/InfoImages/GROUPS_AllGuessWordsGroupsGraphed.png)
