# How to get the wordle word list

Source website for how to get wordlist:
<https://notjoemartinez.com/blog/solving_wordle_with_grep/>

The process involves cloning the wordle website to a local directory.

The wordlist is hardcoded within the .js wordle javascript file as two different variables.

You can then extract the variable contents and format the wordlist as needed, which is a text file having one word per line.

This command clones the site:
```$ wget --mirror --page-requisites --convert-links --adjust-extension --compression=auto --no-if-modified-since --no-check-certificate <https://www.nytimes.com/games/wordle/index.html>```

The javscript file is in the wordle folder. Open it in VS code and reformat the code with the Beautify extension.

Copy the wordlist variables to a new empty python file like new.py.

Add these lines to the bottom. In this case the word list variables are named wo and wc:

    for i in wo:
        print(i)
    for j in wc:
        print(j)

Save the file and execute the command:

```python3 new,py >> wordlist```

This writes the wo and wc words out into a single text file. Rename the files as needed.

As of 5/2022 the smaller variable list are the words that would be the answer words. The other variable list are words that would not be answers but would also be recognized as words.

As the game changes so do the variable names.

The pywordletool applies grep filters to the words list to help one make word picks.
