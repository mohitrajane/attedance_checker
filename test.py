from attendance_checker import attendance_check

attendance, image = attendance_check(40716, 19971112)
img = attendance['admission_no'].split('/')
print(attendance)
img_file = img[0] + img[1] + '.jpg'
with open(img_file, 'wb') as out_file:
    out_file.write(image)
