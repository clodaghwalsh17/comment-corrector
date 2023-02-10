COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]

class CommentAnalyser():
    def __init__(self, comments):
        self._comments = comments
        self._comment_index = 0
        self._current_comment = self._comments[self._comment_index]
    
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
            copyright_comment = copyright_comment or keyword in comment_text or keyword.capitalize()in comment_text
        return copyright_comment
        