### All Guess Words Groups Stats

#### Introduction

* The **AllGuessWordsGroupsStats.csv.txt** is a comma separated value format text file summarizing the word grouping performance for every word in the Wordle allowed guess word list used as a guess for the starting state where every possible Wordle solution can be the days' Wordle solution. This is the resulting situation for every possible word used for the first Wordle guess word.

* This file can help one evaluate the merit for a game's first word. The list of possible Wordle solutions changes to a list of remaining possible Wordle solutions after the first guess is played. **AllGuessWordsGroupsStats.csv.txt**, being strongly based upon the initial list, no longer applies.  

* This list is sorted according to the number of word groups generated (descending), then by the maximum group size (ascending) and then by the average group size (ascending).

* The list columns are:
  * guess - This is the guess word.
  * qty   - The number of word groups the guess divides the possible Wordle solution words. As of this file there are 2309 solution words. The guess word identically matches or mismatches all the words in each word group.
  * min   - The number of words in the smallest word group.
  * max   - The number of words in the largest word group. The largest word group is often the words having nothing in common with the guess word.
  * ave   - The average size of all the word groups.
  * wrds/max    - The number of times larger the 2039 solution word is above the maximum group size. This value may have no bearing on the guess's merit, but it does provide a comparison means.
* The **Group Driller** **Condensed** verbose output created the content shown in this list.

#### [AllGuessWordsGroupsStats.csv.txt](AllGuessWordsGroupsStats.csv.txt)

#### This Data Graphed

!['All Guess Words Groups Graphed.png Image'](/InfoImages/GROUPS_AllGuessWordsGroupsGraphed.png)
