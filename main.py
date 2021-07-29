import os
import dbSTT


dbSTT.check_dirs()
key, region, language = dbSTT.read_config()
speechFile = dbSTT.get_filename()
# Second arg - duration of file processed by sdk [ms]
splitFiles = dbSTT.split_to_shorter(speechFile, 15000)

for file in splitFiles:
    resultJson = dbSTT.recognize_speech(file, key, region, language)
    resultWords = dbSTT.get_best(resultJson)
    # Second arg - minimal duration of result file [ms]
    dbSTT.make_transcription(dbSTT.align_to_ms(resultWords), file, 5000)
    os.remove(dbSTT.proc_path(file))
    print("\n")
os.remove(dbSTT.proc_path(speechFile))
