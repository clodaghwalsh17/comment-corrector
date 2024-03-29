from enchant.checker import SpellChecker as EnchantSpellChecker
import re

class SpellChecker():

    def __init__(self, language=None, custom_words_file=None):
        if language:
            self.__language = language
        else:
            self.__language = 'en_US'

        self.__checker = EnchantSpellChecker(self.__language)
        self.__dictionary = []    

        self.__add_custom_words('default_words.txt')
        
        if custom_words_file: 
            self.__add_custom_words('/github/workspace/.github/workflows/' + custom_words_file)

    def __add_custom_words(self, file):
        with open(file) as f:
            custom_words = f.readlines()

            for word in custom_words:
                self.__dictionary.append(word.strip())
    
    def _split_camel_case(self, text):
        return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', text) 

    def _is_valid_camel_case(self, text, dictionary):
        for word in dictionary:
            if text == word:
                return True
        
        return False

    def get_dictionary(self):
        return self.__dictionary

    # This function returns a dictionary with the misspelled word as the key and a list of suggestions as the value
    def check_spelling(self, text): 
        self.__checker.set_text(text)
        spelling_suggestions = {}

        for err in self.__checker:
            if err.word not in self.__dictionary:
                suggestions = self.__checker.suggest(err.word)
                individual_words = self._split_camel_case(err.word)
                
                if len(individual_words) > 0: 
                    string = ' '.join(individual_words)

                    if not self._is_valid_camel_case(string, suggestions):
                        spelling_suggestions[err.word] = suggestions
                        
                else:
                    spelling_suggestions[err.word] = suggestions

        return spelling_suggestions
