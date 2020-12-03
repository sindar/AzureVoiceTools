import os
from shutil import move

for file in os.listdir('./'):
     filename = os.fsdecode(file)
     if filename.endswith(".wav"):
        move('./' + filename, './' + '10000' + filename)

