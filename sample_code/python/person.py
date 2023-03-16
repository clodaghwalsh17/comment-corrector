# Copyright agreement here

class Person:
    # Class representing a person

    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def over_18(self):
        return self.age >= 18


p = Person("Mary", 25)
print(p.over_18())