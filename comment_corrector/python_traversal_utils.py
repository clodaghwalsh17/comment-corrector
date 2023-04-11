class PythonTraversalUtils:

    @staticmethod
    def find_last_child(entity):
        if not entity:
            return
        
        stack = []
        stack.append(entity)

        while len(stack) > 0:
            root = stack.pop()

            if not root['children']:
                return root
            else:
                children = root['children']
                stack.append(children[len(children)-1])

    @staticmethod
    def get_suite(entity):
        for sub_entity in entity:
            if sub_entity['type'] == "suite":
                return sub_entity
    
    @staticmethod
    def find_docstring_node(entity):
        if entity['children']:
            for sub_entity in entity['children']:
                if PythonTraversalUtils.is_doc_comment(sub_entity):
                    return sub_entity
    
    @staticmethod
    def is_doc_comment(entity):
        if entity['type'] == "simple_stmt" and len(entity['children']) > 0: 
            return entity['children'][0]['type'] == "string" and (entity['children'][0]['label'].startswith("\"\"\"") or entity['children'][0]['label'].startswith("'''"))

        return False
    
    @staticmethod
    def find_suite_indexes(entity):
        indexes = []
        for index, sub_entity in enumerate(entity):
            if sub_entity['type'] == "suite":
                indexes.append(index)
        return indexes 

    @staticmethod
    def find_return_node(entity):
        suite = PythonTraversalUtils.get_suite(entity)
        for sub_entity in suite['children']:
            if not sub_entity:
                return
            
            stack = []
            stack.append(sub_entity)

            while len(stack) > 0:
                root = stack.pop()

                if root['type'] == "return_stmt":
                    return root
                else:
                    children = root['children']
                    for child in children:
                        stack.append(child)

    @staticmethod
    def find_name_node(entity):
        for sub_entity in entity:
            if sub_entity['type'] == "name":
                return sub_entity

    @staticmethod
    def get_function_name(entity):
        return PythonTraversalUtils.find_name_node(entity)['label']

    @staticmethod
    def get_function_params(entity):
        for sub_entity in entity:
            if sub_entity['type'] == "parameters":
                return sub_entity
    
    @staticmethod
    def get_constructor(class_entity):
        suite = PythonTraversalUtils.get_suite(class_entity['children'])
        for sub_entity in suite['children']:
            if sub_entity['type'] == "funcdef" and PythonTraversalUtils.get_function_name(sub_entity['children']) == "__init__":
                return sub_entity
    
    @staticmethod
    def get_first_class_entity(class_suite):
        for sub_entity in class_suite['children']:
            if not PythonTraversalUtils.is_doc_comment(sub_entity):
                return sub_entity