from comment_corrector.extract_comments import list_comments
from comment_corrector.spellchecker import SpellChecker
from comment_corrector.reviewable_comment import ReviewableComment
from comment_corrector.category import Category
from comment_corrector.comment_error import CommentError
from abc import ABC, abstractmethod
import sys

COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]

class CommentAnalyser(ABC):
    def __init__(self, files):
        self._files = files
        self._reviewable_comments = []
        self._spell_checker = SpellChecker()
    
    def set_spellchecker_language(self, language):
        self._spell_checker = SpellChecker(language=language)

    def set_spellchecker_custom_words(self, custom_words):
        self._spell_checker = SpellChecker(custom_words_filepath=custom_words)

    def set_spellchecker_settings(self, language, custom_words):
        self._spell_checker = SpellChecker(language=language,custom_words_filepath=custom_words)

    def analyse_comments(self):
        self._analysis_strategy()
        return self._reviewable_comments

    def _set_analysis_strategy(self, mime_type):
        comments_file1 = list_comments(self._files[0], mime_type) 
        comments_file2 = list_comments(self._files[1], mime_type) 
        if comments_file1 and comments_file2:
            self._analysis_strategy = self._full_analysis
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
        for keyword in TASK_IDENTIFIERS:
            task_comment = task_comment or keyword in comment_text
        return task_comment
    
    def _is_copyright_comment(self, comment_text):
        copyright_comment = False
        for keyword in COPYRIGHT_IDENTIFIERS:
            copyright_comment = copyright_comment or keyword in comment_text or keyword.capitalize() in comment_text
        return copyright_comment
    
    @abstractmethod
    def _is_commented_code(self, comment_text):
        pass
    
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
                if errors is not None:
                    self._reviewable_comments.append(ReviewableComment(comment, errors, description=description))

    def _no_analysis(self):
        # Exiting as no comments to review
        sys.exit()