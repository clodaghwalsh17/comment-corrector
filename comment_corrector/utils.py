import os
import json

SOURCE = "supported_languages.json"

class Utils: 
    def __init__(self):
        with open(SOURCE) as f:
            data = json.load(f)
        # self.mapping is a list of dictionaries
        self.mapping = data['supported_languages']

    def get_file_extension(self, file):
        _, extension = os.path.splitext(file)
        return extension

    def get_mime_type(self, file):
        extension = self.get_file_extension(file)
        map = next((mapping for mapping in self.mapping if extension in mapping['file_extension']), None)
        return map['mime_type']

    def get_programming_language(self, file):
        extension = self.get_file_extension(file)
        map = next((mapping for mapping in self.mapping if extension in mapping['file_extension']), None)
        return map['language']

    def get_supported_languages(self):
        return [mapping['language'] for mapping in self.mapping]

    def get_supported_file_extensions(self):
        file_extensions = [mapping['file_extension'] for mapping in self.mapping]
        return self.flatten_to_list(file_extensions)
    
    def get_mapping(self):
        return self.mapping

    def flatten_to_list(self, struct):
        flatten_operation = lambda *n: (e for a in n for e in (flatten_operation(*a) if isinstance(a, (tuple, list)) else (a,)))
        return list(flatten_operation(struct))

    def validate_files(self, files):
        if (self.get_file_extension(files[0]) == self.get_file_extension(files[1])) and self.get_file_extension(files[0]) in self.get_supported_file_extensions():
            return
        else:
            raise Exception("Error with input files.\nInput files supplied are either written in an unsupported language or the files are not written in the same language.") 