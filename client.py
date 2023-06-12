import requests
import os
import pyAesCrypt
import io


cwd = os.getcwd()
if not os.path.isdir(cwd + '/downloads'):
    os.mkdir(cwd + '/downloads')

params = {"cameraId": "5"}

# IP address should be changed to real
response = requests.post('http://192.168.0.97:4000/get_photo', json=params)

with open(cwd + '/downloads/photo._pg', 'wb') as s:
    for chunk in response.iter_content(chunk_size=64):
        s.write(chunk)

pyAesCrypt.decryptFile(cwd + '/downloads/photo._pg', cwd + '/downloads/photo.jpg', 'qwerty', 64 * 1024)
