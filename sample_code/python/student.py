from person import Person
class Student(Person):
    # Student inherits from Person

    def __init__(self, name, age, year):
        super().__init__(name, age)
        self.year = year
    
    def about(self):
        print("{} aged {} is in year {}".format(self.name, self.age, self.year))

s = Student("Mary", 25, 3)
print(s.over_18())
s.about()