from attendance_checker import attendance_check

attendance, image = attendance_check()
print(attendance)
# print(image)
with open('test9595', 'wb') as out_file:
    out_file.write(image)
