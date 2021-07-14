# dbSTT
###### Creating speech database for AI training
## Prerequisites
1. Install [**Python**](https://www.python.org/downloads/).
2. Install [ffmpeg](http://ffmpeg.org/download.html).
3. Run `pip install -r requirements.txt` to install dependencies.
4. Create an [Microsoft Azure](https://azure.microsoft.com/pl-pl/free/) account and create **Speech** resource.
## Usage
1. Run `preprocess.py` to create needed directories and your config file.
The key and region can be found on Azure Speech resource tab.
Supported language codes can be found [here](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#speech-to-text).
2. Put a file containing speech to `source` folder in your repo.
3. Run `dbSTT.py` and enter a name of file you want to transcribe. If something goes wrong, process will stop.
4. If everything goes well, you will get transcribed files in a `result` folder. ***Source files will be deleted.***
## Adjustments
You can adjust manually in `dbSTT.py` length of files in database and files sent to Microsoft servers. 
For database files it's by default 5s (works well with voice cloning) and 15s for intermediary files.
Speech API cuts recognition after 2s of silence, what's a reason of splitting source files.
Using 15s parts reduces the risk of cutting too much of the source file.
Silence-trimming tools like [unsilence](https://github.com/lagmoellertim/unsilence) can be used as well.
