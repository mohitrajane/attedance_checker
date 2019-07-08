from attendance_checker import attendance_check

attendance, image = attendance_check(40716, 19971112)
print(attendance)
with open('test9595', 'wb') as out_file:
    out_file.write(image)
