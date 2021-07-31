# dbSTT
###### Speech database creator for AI training
## Prerequisites
1. Install [**Python**](https://www.python.org/downloads/).
2. Install [ffmpeg](http://ffmpeg.org/download.html).
3. Run `pip install -r requirements.txt` to install dependencies.
4. Create an [Microsoft Azure](https://azure.microsoft.com/pl-pl/free/) account and create **Speech** resource.
## Usage
1. Run `main.py` to start program and create your config file on first usage. The key and region can be found on your Azure Speech resource tab.
2. Choose your source file and destination of result files by clicking on a right button.
3. Enter and confirm a duration of files sent to external server, default is 15000ms = 15s.
4. Enter and confirm a duration of result file duration, default is 5000ms = 5s.
5. If everything goes well, you will get result files in a selected folder.
## Warning
Speech API cuts recognition after 2s of silence, what's a reason of splitting source files.
Using 15s parts reduces the risk of cutting too much of the source file.
Silence-trimming tools like [my another repo](https://github.com/wm1511/VisTrim) can be used before using this program.
Then you can reduce the duration of intermediary files and increase precision.