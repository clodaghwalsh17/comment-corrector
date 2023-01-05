f = open("C:/Users/Admin/Documents/FYP Code/comment-corrector/comment_corrector/sample_code/ExampleA.java", "r")

first_line = f.readline()
print(first_line)

f.seek(115)
change = f.readline()
print(change)

f.close()