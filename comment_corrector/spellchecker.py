from enchant.checker import SpellChecker as EnchantSpellChecker

class SpellChecker():

    def __init__(self, language=None, custom_words_filepath=None):
        if language:
            self.__language = language
        else:
            self.__language = 'en_US'

        self.__checker = EnchantSpellChecker(self.__language)

        self.__add_custom_words('default_words.txt')
        
        if custom_words_filepath: 
            self.__add_custom_words(custom_words_filepath)

    def __add_custom_words(self, file):
        with open(file) as f:
            custom_words = f.readlines()

            for word in custom_words:
                self.__checker.add(word) 
    
    # This function returns a dictionary with the misspelled word as the key and a list of suggestions as the value
    def check_spelling(self, text): 
        self.__checker.set_text(text)
        spelling_suggestions = {}

        for err in self.__checker:
            suggestions = self.__checker.suggest(err.word)
            spelling_suggestions[err.word] = suggestions

        return spelling_suggestions
