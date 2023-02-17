import os
import json

SOURCE = "supported_languages.json"

def get_data():
    with open(SOURCE) as f:
        data = json.load(f)
        return data['supported_languages']

class Utils:    
    # data is a list of dictionaries
    data = get_data()
    
    @staticmethod
    def get_file_extension(file):
        _, extension = os.path.splitext(file)
        return extension

    @staticmethod
    def get_mime_type(file):
        extension = Utils.get_file_extension(file)
        map = next((mapping for mapping in Utils.data if extension in mapping['file_extension']), None)
        return map['mime_type']

    @staticmethod
    def get_programming_language(file):
        extension = Utils.get_file_extension(file)
        map = next((mapping for mapping in Utils.data if extension in mapping['file_extension']), None)
        return map['language']

    @staticmethod
    def get_code_words(language):
        map = next((mapping for mapping in Utils.data if language in mapping['language']), None)
        return map['code_words']
    
    @staticmethod
    def get_terminator(language):
        map = next((mapping for mapping in Utils.data if language in mapping['language']), None)
        return map.get('terminator')

    @staticmethod
    def get_supported_languages():
        return [mapping['language'] for mapping in Utils.data]

    @staticmethod
    def get_supported_file_extensions():
        file_extensions = [mapping['file_extension'] for mapping in Utils.data]
        return Utils.flatten_to_list(file_extensions)
    
    @staticmethod
    def flatten_to_list(struct):
        flatten_operation = lambda *n: (e for a in n for e in (flatten_operation(*a) if isinstance(a, (tuple, list)) else (a,)))
        return list(flatten_operation(struct))
    
    @staticmethod
    def validate_files(files):
        if (Utils.get_file_extension(files[0]) == Utils.get_file_extension(files[1])) and Utils.get_file_extension(files[0]) in Utils.get_supported_file_extensions():
            return
        else:
            raise Exception("Error with input files.\nInput files supplied are either written in an unsupported language or the files are not written in the same language.") 