from comment_corrector.comment_extractor import CommentExtractor
from comment_corrector.spellchecker import SpellChecker
from comment_corrector.semantic_diff import SemanticDiff
from comment_corrector.reviewable_comment import ReviewableComment
from comment_corrector.category import Category
from comment_corrector.comment_error import CommentError
from comment_corrector.utils import Utils
from abc import ABC, abstractclassmethod
import sys
import re

class CommentAnalyser(ABC):
    COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
    TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]
    SYMBOLS_REGEX = "[\(\)\{\}\[\]:\"'~\^&\|!></\+\*-]"
    ASSIGNMENT_REGEX = "="

    def __init__(self, files, code_word_regexes, terminator):
        self._files = files
        self._code_word_regexes = code_word_regexes
        self._terminator = terminator
        self._reviewable_comments = []
        self._spell_checker = None
        self._full_cosmetic_analysis = False
        self._set_analysis_strategy()
    
    def set_spellchecker_custom_words(self, custom_words):
        self._spell_checker = SpellChecker(custom_words_file=custom_words)

    def analyse_comments(self):
        if self._spell_checker is None:
            self._spell_checker = SpellChecker()
        self._analysis_strategy()
        self._reviewable_comments.sort(key=Utils.sort_comments)
        return self._reviewable_comments
    
    @abstractclassmethod
    def _outdated_analysis(self, tree):
        pass

    def _set_analysis_strategy(self):
        extractor = CommentExtractor(Utils.get_mime_type(self._files[0]))
        
        if len(self._files) == 2:
            comments_file1 = extractor.extract_comments(self._files[0])
            comments_file2 = extractor.extract_comments(self._files[1])
            
            if comments_file1 and comments_file2:
                self._analysis_strategy = self._full_analysis
                self._full_cosmetic_analysis = True
                self._comments = comments_file1 
                self._comments_file2 = comments_file2
                comments_set = set(comments_file2)
                self._new_comments = comments_set.difference(comments_file1)
                self._comment_index = 0
                self._current_comment = self._comments[self._comment_index]
                semantic_diff = SemanticDiff(self._files)
                self._tree = semantic_diff.source_to_tree()
                self._eof = int(self._tree['pos']) + int(self._tree['length']) 
                self._edit_script_actions = semantic_diff.edit_script_actions()
                self._refactored_names = semantic_diff.refactored_names()
                self._deleted_names = semantic_diff.deleted_names()
                self._unreferenced_names = semantic_diff.unreferenced_names()
            elif comments_file2:
                self._analysis_strategy = self._cosmetic_analysis
                self._comments = comments_file2
            else:
                self._analysis_strategy = self._no_analysis 
        else:
            comments = extractor.extract_comments(self._files[0])

            if comments:
                self._analysis_strategy = self._cosmetic_analysis
                self._comments = comments
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
    
    def _find_deleted_names(self, comment_text):
        deleted_names = []
        for name in self._deleted_names:
            result = self._match_phrase(name)(comment_text)
            if result is not None:
                deleted_names.append(name)
        return deleted_names

    def _find_refactored_names(self, comment_text):
        refactored_names = {}
        for v,k in self._refactored_names.items():
            result = self._match_phrase(v)(comment_text)
            if result is not None:
                refactored_names[v] = k
        return refactored_names

    def _contains_unreferenced_names(self, comment_text):
        for name in self._unreferenced_names:
            result = self._match_phrase(name)(comment_text)
            if result is not None:
                return True
        return False

    def _check_spelling(self, comment_text):
        return self._spell_checker.check_spelling(comment_text)

    def _check_comment(self):
        if self._current_comment in self._comments_file2:
            self._cosmetic_check(self._current_comment)

        self._next_comment()

    def _check_relevance(self, entity):       
        if self._current_comment in self._comments_file2:
            cosmetic_errors = self._cosmetic_check(self._current_comment)
            if CommentError.COMMENTED_CODE not in cosmetic_errors:
                # Generally a change is comprised of many actions, meaning the register_outdated_comment function could be called several times.
                # To ensure that a comment is only marked as outdated once a set is used for the variable reviewable_comments.
                for action in self._edit_script_actions:
                    if self._is_comment_editing_action(action, entity):
                        self._register_outdated_comment(cosmetic_errors)
                        break

        self._next_comment()    

    def _is_comment_editing_action(self, action, entity):
        file_position = int(entity['pos'])
        reference_point = file_position + int(entity['length'])

        if action.affects_return():
            return True
        if action.type() == "update-node" and file_position <= action.src_start() and action.src_start() <= reference_point:
            return True
        elif action.type() == "insert-node" and file_position == action.dst_start():
            return True
        elif action.type() == "move-tree" and file_position == action.src_start() and action.src_end() < self._eof:
            return True
        elif action.type() == "move-tree" and file_position == action.dst_start() and action.dst_end() < self._eof:
            return True
        elif action.type() == "delete-tree" and file_position == action.src_start():
            return True
        
        return False

    def _register_outdated_comment(self, cosmetic_errors):
        comment_equivalent = self._get_comment_equivalent()
        if len(cosmetic_errors) > 0:
            reviewable_comment = self._get_registered_comment()
            reviewable_comment.add_error(CommentError.OUTDATED_COMMENT)
            reviewable_comment.update_line_number(comment_equivalent.line_number())
        else:
            self._reviewable_comments.append(ReviewableComment(comment_equivalent, errors=[CommentError.OUTDATED_COMMENT]))

    def _get_comment_equivalent(self):
        index = next((i for i, item in enumerate(self._comments_file2) if item.text() == self._current_comment.text()), -1)
        return self._comments_file2[index]

    def _get_registered_comment(self):
        index = next((i for i, item in enumerate(self._reviewable_comments) if item.text() == self._current_comment.text()), -1)
        return self._reviewable_comments[index]

    def _full_analysis(self):
        self._outdated_analysis(self._tree)
        for comment in self._new_comments:
            self._cosmetic_check(comment)
    
    def _cosmetic_check(self, comment):
        errors = []
        description = "" 

        if comment.category() != Category.UNTRACKABLE:
            if self._is_commented_code(comment.text()) and comment.category() != Category.DOCUMENTATION:
                errors.append(CommentError.COMMENTED_CODE)
                self._reviewable_comments.append(ReviewableComment(comment, errors))
                return errors
            
            if self._is_task_comment(comment.text()):
                errors.append(CommentError.REMAINING_TASK)

            spelling_suggestion = self._check_spelling(comment.text()) 
            if spelling_suggestion:
                errors.append(CommentError.SPELLING_ERROR)
                description += "* " + self._provide_spelling_suggestions(spelling_suggestion)
            
            if self._full_cosmetic_analysis:
                refactored_names = self._find_refactored_names(comment.text()) 
                deleted_names = self._find_deleted_names(comment.text())

                if refactored_names:
                    errors.append(CommentError.REFACTORED_NAME)
                    description += "* " + self._list_refactored_names(refactored_names)
                if self._contains_unreferenced_names(comment.text()):
                    errors.append(CommentError.REFACTORED_NAME)
                    description += "* " + "Name(s) referenced in this comment no longer exist\n"
                if len(deleted_names) > 0:
                    errors.append(CommentError.DELETED_NAME)
                    description += "* " + self._list_deleted_names(deleted_names)
            
            if len(errors) > 0:
                self._reviewable_comments.append(ReviewableComment(comment, errors, description=description))
        
        return errors

    def _cosmetic_analysis(self): 
        for comment in self._comments:
            self._cosmetic_check(comment)

    def _no_analysis(self):
        # Exiting as no comments to review
        sys.exit(0)

    def _provide_spelling_suggestions(self, spelling_suggestions):
        suggestions = "The following word(s) are misspelt:\n"
        for v, k in spelling_suggestions.items():
            suggestions += "- '{}' consider replacing with {}\n".format(v, k)
        return suggestions
    
    def _list_refactored_names(self, refactored_names):
        description = "Name(s) referenced in this comment were refactored:\n"
        for v, k in refactored_names.items():
            description += "- '{}' changed to '{}'\n".format(v, k) 
        return description
    
    def _list_deleted_names(self, deleted_names):
        description = "The following name(s) were deleted:\n"
        for name in deleted_names:
            description += "- {}\n".format(name) 
        return description