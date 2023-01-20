from enchant.checker import SpellChecker

language = 'en_GB'
if language:
    checker = SpellChecker(language)
else:
    checker = SpellChecker('en_US')

custom_words_filepath = 'custom_words.txt'
if custom_words_filepath: 
    with open(custom_words_filepath) as f:
        custom_words = f.readlines()

    for word in custom_words:
        checker.add(word)   


checker.set_text("An example commnt with spellin mistks. \
The word colour can be spelt many ways. Nouns like america should be in caps.\
Sometimes comments have variable names eg myVar or myFunc.")
for err in checker:
    print("ERROR:", err.word)
    suggestions = checker.suggest(err.word)
    if err.word.capitalize() in suggestions:
        err.replace_always(err.word.capitalize())
    print(suggestions)

after = checker.get_text()
print(after)