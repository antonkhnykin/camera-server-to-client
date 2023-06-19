import requests
import os
import pyAesCrypt
import io


cwd = os.getcwd()
if not os.path.isdir(cwd + '/downloads'):
    os.mkdir(cwd + '/downloads')

params = {"cameraId": "3"}

# IP address should be changed to real
response = requests.post('http://217.117.182.170:54000/get_photo', json=params)

with open(cwd + '/downloads/photo._pg', 'wb') as s:
    for chunk in response.iter_content(chunk_size=64):
        s.write(chunk)

with open(cwd + '/num.txt', 'r') as f:
    num = f.readline()
    pyAesCrypt.decryptFile(cwd + '/downloads/photo._pg', cwd + '/downloads/photo' + str(num) + '.jpg', 'qwerty', 64 * 1024)
    num = int(num) + 1
    f.close()

with open(cwd + '/num.txt', 'w') as f:
    f.write(str(num))
    f.close()
