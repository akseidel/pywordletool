# Word List Information

The original NYT Wordle maintained two word lists. One list contained 2,309 words that would be solution words. The other list contained 12,546 words that would never be solutions. Both lists combined are 14,855 words that are accepted as valid Wordle guesses. All these words are transmitted to your web browsing device when you work the Wordle puzzle so that the puzzle application does not need to check with the NYT Wordle server for every interaction you do with the Wordle application.

These two lists essentially still exist subsequent to the NYT taking control over Wordle and Wordlebot and after making some application revisions. The word list structure within the Wordle application changed, but the logic regarding two lists remains. The overall 14,855 valid entry words list remains untouched. The 14,855 allowed words divide into two categories. One word category are words the Wordlebot considers possible solutions. This list of Wordlebot possible solutions consists of the original 2,309 NYT Wordle words, less a few original words the NYT considers socially unsuitable, plus some words that were formerly never-to-be-solutions.

Words the Wordlebot might use for a guess are something altogether different. They come from a word list that is not needed by the Wordle application. That list never comes to your device. Those Wordlebot guess words include all the Wordlebot possible solutions words, plus many never-to-be-solutions words that are both potentially useful to the Wordlebot's play strategy and that are not so uncommon that Wordle players might more openly complain about the Wordlebot's word knowledge extent. These added words are only known when seen used by the Wordlebot.

The Classic word list is the original 2,309 words. This is file [wo_nyt_wordlist.txt](/worddata/wo_nyt_wordlist.txt). This list still contains the few words the NYT considered unsuitable.

The 3,200 word Classic+ word list is the word list Wordlebot considers possible solutions. This list is as described above. The NYT occasionally adds words and removes words from this list. A change was expected to occur in early 2025. NYT announced this in late 2024. Changes did occur in July and August 2025. File [botadd_nyt_wordlist.txt](/worddata/botadd_nyt_wordlist.txt) is this list. The file [bot_added_wordlist.txt](/worddata/bot_added_wordlist.txt) contains the words the NYT transferred from the original 12,546 never-to-be-solution list to the possible solution list. A fact that seems to obvious on the surface to mention is that the Wordlebot cannot solve the Wordle without the solution word existing in the Wordlebot possible solutions list. Thus, while some words in the  Wordlebot possible solutions list may never be a solution, the actual solution is always present in the Wordlebot possible solutions list. And, while every word in the Classic solutions list will probably be a solution some day, the actual solution may not be present in the Classic solutions list.

The full 14,855 word list is the file [nyt_wordlist.txt](/worddata/nyt_wordlist.txt).

The following tracks some of the word changes, but has omissions. Removed means removed from being a possible solution. Removed words are still allowed guesses:

* fanny, NYT unsuitable. It was an original 2,309 possible solution.
* gipsy, NYT unsuitable. It was an original 2,309 possible solution.
* gypsy, NYT unsuitable. It was an original 2,309 possible solution.
* lycra, Was a Wordlebot added word, but then later removed. Edited here 8/16/23
* mammy, NYT unsuitable. It was an original 2,309 possible solution.
* pansy, NYT unsuitable. It was an original 2,309 possible solution.
* semen, NYT unsuitable. It was an original 2,309 possible solution.
* welch, NYT unsuitable. It was an original 2,309 possible solution.
* welsh, NYT unsuitable. It was an original 2,309 possible solution.
* yowza, Was a Wordlebot added word, but then later removed. Edited here 8/16/23
* bilgy, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* japed, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* jihad, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* limey, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* miasm, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* mussy, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* pubis, Was a Wordlebot added word, but then later removed. Edited here 11/16/23
* airer, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* chaat, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* dolma, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* doxed, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* fogie, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* hiree, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* hoagy, Was a Wordlebot added word, but then later removed. Edited here 01/25/24
* jerry, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* odeum, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* psyop, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* pwned, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* resod, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* rewax  Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* rewon, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* shlub, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* unbag, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* yeesh, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* zowie, Was a Wordlebot added word, but then later removed. Edited here 01/11/24
* doggo, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* fubar, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* mensa, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* nimby, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* priss, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* proto, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* pshaw, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* schmo, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* shlep, Was a Wordlebot added word, but then later removed. Edited here 08/07/25
* xerox, Was a Wordlebot added word, but then later removed. Edited here 08/07/25