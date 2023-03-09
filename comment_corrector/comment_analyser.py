from comment_corrector.semantic_diff import *
from comment_corrector.comment_extractor import CommentExtractor
from comment_corrector.spellchecker import SpellChecker
from comment_corrector.reviewable_comment import ReviewableComment
from comment_corrector.category import Category
from comment_corrector.comment_error import CommentError
from comment_corrector.utils import Utils
from abc import ABC, abstractclassmethod
import sys
import re
import json

class CommentAnalyser(ABC):
    COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
    TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]
    SYMBOLS_REGEX = "[\(\)\{\}\[\]:\"'~^&|!><\+-/\*]"
    ASSIGNMENT_REGEX = "="

    def __init__(self, files, code_word_regexes, terminator):
        self._files = files
        self._code_word_regexes = code_word_regexes
        self._terminator = terminator
        self._reviewable_comments = set()
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
        self._reviewable_comments = list(self._reviewable_comments)
        self._reviewable_comments.sort(key=Utils.sort_comments)
        return self._reviewable_comments
    
    @abstractclassmethod
    def _outdated_analysis(self, tree):
        pass

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
            self._comments = comments_file1 
            self._comments_file2 = [comment.text() for comment in comments_file2]
            comments_set = set(comments_file2)
            self._new_comments = comments_set.difference(comments_file1)
            self._comment_index = 0
            self._current_comment = self._comments[self._comment_index]
            self._set_tree()
            self._edit_script_actions = diff(self._files)
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
        
        symbol_search_result = re.search(self.SYMBOLS_REGEX, comment_text)
        if symbol_search_result is not None:
            # Allow web links of the form http://www.example.com
            if symbol_search_result.group(0) == ":":
                weblink_substring = "://www."
                index = symbol_search_result.span()[1]
                context = comment_text[index:index+len(weblink_substring)-1]
                return context == weblink_substring

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

    def _check_comment(self):
        if self._current_comment.text() in self._comments_file2:
            self._cosmetic_check(self._current_comment)

        self._next_comment()

    def _check_relevance(self, file_position, length):
        reference_point = file_position + length
        if self._current_comment.text() in self._comments_file2:
            cosmetic_errors = self._cosmetic_check(self._current_comment)
            if CommentError.COMMENTED_CODE not in cosmetic_errors:
                # Generally a change is comprised of many actions, meaning the register_outdated_comment function could be called several times.
                # To ensure that a comment is only marked as outdated once a set is used for the variable reviewable_comments.
                for action in self._edit_script_actions:
                    if action.type() == "update-node" and file_position <= action.src_start() and action.src_start() <= reference_point:
                        self._register_outdated_comment(cosmetic_errors)
                    elif action.type() == "insert-node" and file_position == action.dst_start():
                        self._register_outdated_comment(cosmetic_errors)
                    elif action.type() == "move-tree" and file_position == action.src_start():
                        self._register_outdated_comment(cosmetic_errors) 
                    elif action.type() == "move-tree" and file_position == action.dst_start():
                        self._register_outdated_comment(cosmetic_errors)
                    elif action.type() == "delete-tree" and file_position == action.src_start():
                        self._register_outdated_comment(cosmetic_errors)
      
        self._next_comment()    

    def _register_outdated_comment(self, cosmetic_errors):
        if len(cosmetic_errors) > 0:
            reviewable_comment = list(self._reviewable_comments().pop)
            reviewable_comment.add_error(CommentError.OUTDATED_COMMENT)
            self._reviewable_comments.add(reviewable_comment)
        else:
            self._reviewable_comments.add(ReviewableComment(self._current_comment, errors=[CommentError.OUTDATED_COMMENT]))

    def _full_analysis(self):
        self._outdated_analysis(self._tree)
        for comment in self._new_comments:
            self._cosmetic_check(comment)
    
    def _cosmetic_check(self, comment):
        errors = []
        description = ""
        spelling_suggestion = self._check_spelling(comment.text()) # TODO make more readable

        if comment.category() != Category.UNTRACKABLE:
            if self._is_commented_code(comment.text()) and comment.category() != Category.DOCUMENTATION:
                errors.append(CommentError.COMMENTED_CODE)
                self._reviewable_comments.add(ReviewableComment(comment, errors))
                return errors
            
            if self._is_task_comment(comment.text()):
                errors.append(CommentError.REMAINING_TASK)            
            if spelling_suggestion:
                errors.append(CommentError.SPELLING_ERROR)
                description = spelling_suggestion
            if len(errors) > 0:
                self._reviewable_comments.add(ReviewableComment(comment, errors, description=description))
        
        return errors

    def _cosmetic_analysis(self): 
        for comment in self._comments:
            self._cosmetic_check(comment)

    def _no_analysis(self):
        # Exiting as no comments to review
        sys.exit()