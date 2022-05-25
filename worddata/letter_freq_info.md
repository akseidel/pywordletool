# The letter frequency/ranking information

The letter ranking information was obtained by using grep for each letter on the wo word list. The wo word list is the smaller wordle word list that contains only the words that are wordle answers. In other words the other wordle word list, which was not used to generate the letter ranking information, contains words that would never be wordle answers.

The difference between letter rankings generated from the two word lists is that the smaller word promotes some letters higher than the larger word list and vice versa.

The grep operation used operates on the word level and not the letter level. For example a word containing two E letters counts once, not twice.

The least occurring letter is the basis for all the other letter rankings. The letter J is counted in 27 words. Its rank is assigned to 1. The letter E is counted in 1053 words. Its rank is assigned 1053/27 or 39.0.

The word rank shown by the wordletool is the sum of the ranking for each letter in a word. A word having a rank higher than another word has a higher probability of identifying an answer letter than a lower ranking word. Conversely, a lower ranking word has a higher probability of identifying non answer letters than a higher ranking word. The value of both types of information varies in importance as to the current game status.
