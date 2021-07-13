import os


#Making sure needed directories exist
def check_dir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


#Creating user config file
def create_config():
    with open("config", "w") as config:
        config.write(input("Enter your subscription key: ") + "\n")
        config.write(input("Enter your region: ") + "\n")
        config.write(input("Enter speech language code: "))


check_dir("source")
check_dir("result")
create_config()