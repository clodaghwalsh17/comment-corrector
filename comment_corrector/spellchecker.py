from enchant.checker import SpellChecker as EnchantSpellChecker
import re

class SpellChecker():

    def __init__(self, language=None, custom_words_filepath=None):
        if language:
            self.__language = language
        else:
            self.__language = 'en_US'

        self.__checker = EnchantSpellChecker(self.__language)

        self.__add_custom_words('/github/workspace/default_words.txt')
        
        if custom_words_filepath: 
            self.__add_custom_words(custom_words_filepath)

    def __add_custom_words(self, file):
        with open(file) as f:
            custom_words = f.readlines()

            for word in custom_words:
                self.__checker.add(word) 
    
    def _split_camel_case(self, text):
        return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', text) 

    def _is_valid_camel_case(self, text, dictionary):
        for word in dictionary:
            if text == word:
                return True
        
        return False

    # This function returns a dictionary with the misspelled word as the key and a list of suggestions as the value
    def check_spelling(self, text): 
        self.__checker.set_text(text)
        spelling_suggestions = {}

        for err in self.__checker:
            suggestions = self.__checker.suggest(err.word)
            individual_words = self._split_camel_case(err.word)
            
            if len(individual_words) > 0: 
                string = ' '.join(individual_words)

                if not self._is_valid_camel_case(string, suggestions):
                    spelling_suggestions[err.word] = suggestions
                    
            else:
                spelling_suggestions[err.word] = suggestions

        return spelling_suggestions
