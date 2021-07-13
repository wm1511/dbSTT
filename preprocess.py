import os


#Making sure needed directories exist
def check_dir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


check_dir("source")
check_dir("result")