import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import func


# Asking for a source file
def file_browse():
    path = tk.filedialog.askopenfilename(initialdir='/', title='Open file', filetypes=[('Sound files', '*.wav')])
    return path


# Asking for a directory for results
def directory_browse():
    path = tk.filedialog.askdirectory()
    return path


# Checking entry input
def only_numbers(char):
    return char.isdigit()


# Showing intermediary files info
def split_message(index, time):
    tk.messagebox.showinfo(title="Splitting results", message="Files after split: " + str(index) +
                                                              ", Single file length: " + str(time / 1000) + "s")


def hard_error():
    tk.messagebox.showerror(title="Error", message="Recognition failed")


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Database Speech-To-Text')
        self.loaded_file = None
        self.file_list = None

        misc_frame = tk.Frame(self.root)
        open_button = tk.Button(misc_frame, text='Open file and select destination folder', command=self.file_select)
        open_button.grid(row=0, pady=10)
        exit_button = tk.Button(misc_frame, text='Exit', command=self.root.quit)
        exit_button.grid(row=1, pady=10)
        misc_frame.grid(row=0, column=0, padx=20, pady=20)

        split_frame = tk.Frame(self.root)
        split_label = tk.Label(split_frame, text='Duration of intermediary files')
        split_label.grid(pady=10)
        validation = split_frame.register(only_numbers)
        self.split_entry = tk.Entry(split_frame, width=5, validate='key', validatecommand=(validation, '%S'))
        self.split_entry.insert(0, 15000)
        self.split_entry.grid(row=1, pady=10)
        split_button = tk.Button(split_frame, text='Confirm value and split', command=self.file_split)
        split_button.grid(row=2, pady=10)
        split_frame.grid(row=0, column=2, padx=20, pady=20)

        recognize_frame = tk.Frame(self.root)
        recognize_label = tk.Label(recognize_frame, text='Minimal duration of result file')
        recognize_label.grid(pady=10)
        validation = recognize_frame.register(only_numbers)
        self.recognize_entry = tk.Entry(recognize_frame, width=5, validate='key', validatecommand=(validation, '%S'))
        self.recognize_entry.insert(0, 5000)
        self.recognize_entry.grid(row=1, pady=10)
        recognize_button = tk.Button(recognize_frame, text='Confirm value and recognize', command=self.speech_recognize)
        recognize_button.grid(row=2, pady=10)
        recognize_frame.grid(row=0, column=4, padx=20, pady=20)

        # TODO Repair progressbar
        self.progress_bar = tk.ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress_bar.grid(row=2, columnspan=5, pady=20, padx=20)

        tkinter.ttk.Separator(self.root, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=1, sticky='ns')
        tkinter.ttk.Separator(self.root, orient=tk.VERTICAL).grid(row=0, column=3, rowspan=1, sticky='ns')
        tkinter.ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(row=1, columnspan=5, sticky='ew')

        self.root.mainloop()

    # Getting filename from filedialog
    def file_select(self):
        try:
            self.loaded_file = func.Sound(file_browse(), directory_browse())
        except FileNotFoundError:
            tk.messagebox.showerror(title="File error", message="No file was selected!")

    # Getting intermediary files list
    def file_split(self):
        try:
            self.file_list = self.loaded_file.split_to_shorter(int(self.split_entry.get()))
        except AttributeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")

    # Creating final recognition
    def speech_recognize(self):
        try:
            for file in self.file_list:
                recognition = self.loaded_file.recognize_speech(file)
                best_recognition = func.align_to_ms(func.get_best(recognition))
                self.loaded_file.make_transcription(best_recognition, file, int(self.recognize_entry.get()))
                self.loaded_file.clean_directory(file)
                self.progress_bar['value'] += int(500/len(self.file_list))
            tk.messagebox.showinfo(title="Success", message="Recognition succeeded!")
        except TypeError:
            tk.messagebox.showerror(title="File error", message="You have to open sound file first!")
