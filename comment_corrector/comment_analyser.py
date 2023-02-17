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
    COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"] # Q even need anymore
    TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]
    SYMBOLS_REGEX = "[\(\)\{\}\[\],.:\"'~^&|!><%\+-/\*]"
    ASSIGNMENT_REGEX = "="

    def __init__(self, files, code_words, terminator):
        self._files = files
        self._code_words = code_words
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
        task_comment = False
        for keyword in self.TASK_IDENTIFIERS:
            task_comment = task_comment or keyword in comment_text
        return task_comment
    
    def _is_copyright_comment(self, comment_text):
        copyright_comment = False
        for keyword in self.COPYRIGHT_IDENTIFIERS:
            copyright_comment = copyright_comment or keyword in comment_text or keyword.capitalize() in comment_text
        return copyright_comment
    
    def _is_commented_code(self, comment_text):
        if self._terminator and re.search(self._terminator, comment_text) is not None:
            return True
        if re.search(self.ASSIGNMENT_REGEX, comment_text) is not None:
            return True
        if re.search(self.SYMBOLS_REGEX, comment_text) is not None:
            return True
        
        for word in self._code_words:
            if word in comment_text:
                return True
        
        return False
     
    def _check_spelling(self, comment_text):
        return self._spell_checker.check_spelling(comment_text)

    # add to analyse comment but only if 2 file version
    # have as strategy
    def _is_outdated(self, comment): # could be outdated and other errors
        pass
    
    def _full_analysis(self):
        # passed 2 entities??
        # outdated and cosmetic called
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