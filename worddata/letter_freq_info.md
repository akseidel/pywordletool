# The letter frequency/ranking information

The letter ranking information was obtained by using grep for each letter on the wo word list. The wo word list is the smaller wordle word list that contains only the words that are wordle answers. In other words the other wordle word list, which was not used to generate the letter ranking information, contains words that would never be wordle answers.

The difference between letter rankings generated from the two word lists is that the smaller word promotes some letters higher than the larger word list and vice versa.

The grep operation used operates on the word level and not the letter level. For example a word containing two E letters counts once, not twice.

The least occurring letter is the basis for all the other letter rankings. The letter J is counted in 27 words. Its rank is assigned to 1. The letter E is counted in 1053 words. Its rank is assigned 1053/27 or 39.0.

The word rank shown by the Wordle **Helper** is the sum of the ranking for each letter in a word. A word having a rank higher than another word has a higher probability of identifying an answer letter than a lower ranking word. Conversely, a lower ranking word has a higher probability of identifying non answer letters than a higher ranking word. The value of both types of information varies in importance as to the current game status.

The Wordle **Helper** by default uses letter rankings newer than what it originally used. The NYT transferred words from the original never-to-be-a-solution Wordle vocabulary to the possible solutions vocabulary and also culled some words they deemed offensive. The **Helper** **Classic+** vocabulary is this revised possible solutions vocabulary and is also now the **Helper's** default possible solutions this.

It is not known if all words in the **Classic+** vocabulary are deemed possible solutions by the NYT, but it is true the NYT Wordlebot will never solve a Wordle if the solution word is not present in the solutions word pool, and it is true the NYT culled certain words. Therefore, if the NYT Wordle manager intends to approve or select the day's Wordle and if the NYT Wordle manager intends to prevent the Wordlebot from inadvertently showing an offensive word as a remaining solution candidate and if the Wordlebot must always succeed, then the **Classic+** vocabulary is best assumed to be the current possible solutions vocabulary.

As of this writing the NYT transferred 857 words from the never-to-be-a-solution Wordle vocabulary to the possible solution vocabulary. Of those transferred words, 238 end in **ED**. The original **Classic** words had only 23 words ending in **ED**. This difference influences the letter ranking. The letter **E** remains the most common letter but is now proportionally stronger than **A** the second highest ranking letter. The **4th** letter position for **E** is now stronger than the **5th** letter position. The letter **D** moves up 4 letter rank positions and its own **5th** letter position rank is half that of its **1st** letter position rank where before it was previously unremarkable as a **5th** letter. There are other ranking differences that are less dramatic.
