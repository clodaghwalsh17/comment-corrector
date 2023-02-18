from comment_corrector.semantic_diff import source_to_tree
from comment_corrector.comment_extractor import CommentExtractor
from comment_corrector.spellchecker import SpellChecker
from comment_corrector.reviewable_comment import ReviewableComment
from comment_corrector.category import Category
from comment_corrector.comment_error import CommentError
from comment_corrector.utils import Utils
from abc import ABC
import sys
import re
import json

class CommentAnalyser(ABC):
    COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
    TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]
    SYMBOLS_REGEX = "[\(\)\{\}\[\]:\"'~^&|!><%\+-/\*]"
    ASSIGNMENT_REGEX = "="

    def __init__(self, files, code_word_regexes, terminator):
        self._files = files
        self._code_word_regexes = code_word_regexes
        self._terminator = terminator
        self._reviewable_comments = []
        self._spell_checker = SpellChecker()
        self._set_analysis_strategy()
    
    def set_spellchecker_language(self, language):
        self._spell_checker = SpellChecker(language=language)

    def set_spellchecker_custom_words(self, custom_words):
        self._spell_checker = SpellChecker(custom_words_filepath=custom_words)

    def set_spellchecker_settings(self, language, custom_words):
        self._spell_checker = SpellChecker(language=language,custom_words_filepath=custom_words)

    def analyse_comments(self):
        self._analysis_strategy()
        return self._reviewable_comments

    def _set_tree(self):
        tree = json.loads(source_to_tree(self._files[0]))   
        # self._tree is a dictionary with the keys type, pos, length, children      
        self._tree = tree['root'] 

    def _set_analysis_strategy(self):
        extractor = CommentExtractor(Utils.get_mime_type(self._files[0]))
        comments_file1 = extractor.extract_comments(self._files[0])
        comments_file2 = extractor.extract_comments(self._files[1])
        if comments_file1 and comments_file2:
            self._analysis_strategy = self._full_analysis
            self._comments = [] # FINISH combine comments maybe??
            # self._comment_index = 0
            # self._current_comment = self._comments[self._comment_index]
            self._set_tree() # Q do need 2 trees
        elif comments_file2:
            self._analysis_strategy = self._cosmetic_analysis
            self._comments = comments_file2
        else:
            self._analysis_strategy = self._no_analysis 

    def _next_comment(self):
        self._comment_index += 1
        if self._comment_index < len(self._comments):
            self._current_comment = self._comments[self._comment_index]

    def _is_task_comment(self, comment_text):
        for keyword in self.TASK_IDENTIFIERS:
            result = self._match_phrase(keyword)(comment_text)
            if result is not None:
                return True
        return False
    
    def _is_copyright_comment(self, comment_text):
        for keyword in self.COPYRIGHT_IDENTIFIERS:
            result = self._match_phrase(keyword)(comment_text)
            if result is not None:
                return True
        return False
    
    def _match_phrase(self, word):
        return re.compile(r'\b({})\b'.format(word), flags=re.IGNORECASE).search

    def _is_commented_code(self, comment_text):
        if self._terminator and re.search(self._terminator, comment_text) is not None:
            return True
        if re.search(self.ASSIGNMENT_REGEX, comment_text) is not None:
            return True
        if re.search(self.SYMBOLS_REGEX, comment_text) is not None:
            return True
        
        # Certain keywords of a language can be omitted from the list of regexes as the previous checks identify the commented out code
        # This is beneficial as many keywords are often found in a genuine comment eg the words if, else, for, while, in, is
        # For example the keyword if is always accompanied by a symbol and for this reason is not included in the list
        for regex in self._code_word_regexes:
            result = self._match_phrase(regex)(comment_text)
            if result is not None:
                return True
        
        return False
     
    def _check_spelling(self, comment_text):
        return self._spell_checker.check_spelling(comment_text)

    def _is_outdated(self, comment):
        pass
    
    def _full_analysis(self):
        print("Do full analysis")

    def _cosmetic_analysis(self): 
        for comment in self._comments:
            errors = []
            description = ""
            spelling_suggestion = self._check_spelling(comment.text()) # TODO make more readable

            if comment.category() != Category.UNTRACKABLE:
                if self._is_task_comment(comment.text()):
                    errors.append(CommentError.REMAINING_TASK)            
                if spelling_suggestion:
                    errors.append(CommentError.SPELLING_ERROR)
                    description = spelling_suggestion
                if self._is_commented_code(comment.text()):
                    errors.append(CommentError.COMMENTED_CODE)
                if len(errors) > 0:
                    self._reviewable_comments.append(ReviewableComment(comment, errors, description=description))

    def _no_analysis(self):
        # Exiting as no comments to review
        sys.exit()