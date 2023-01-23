import random # Built in module

PI = 3.14 # Value of pi

# Find area of circle with random radius
def area():   
   r = random.randint(1, 5) # Random value between 1 and 5
   area = PI * r * r # Formula for area for circle
   # Print information
   print("Radius={}, Area={}".format(r,area))

print("Pi={}\n".format(PI))
area()