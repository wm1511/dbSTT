import tkinter as tk
import tkinter.ttk


class Configurator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Configurator')

        key_frame = tk.Frame(self.root)
        key_label = tk.Label(key_frame, text='Enter your subscription key')
        key_label.pack()
        self.key_entry = tk.Entry(key_frame, width=32)
        self.key_entry.pack()
        key_frame.grid(padx=20, pady=20)

        region_frame = tk.Frame(self.root)
        region_label = tk.Label(region_frame, text='Choose your region')
        region_label.pack()
        self.v1 = tk.StringVar()
        region_combobox = tk.ttk.Combobox(region_frame, width=20, textvariable=self.v1)
        region_combobox['values'] = ('centralus', 'eastus', 'westus', 'canadacentral', 'brazilsouth', 'eastasia',
                                     'southeastasia', 'australiaeast', 'centralindia', 'japaneast', 'japanwest',
                                     'koreacentral', 'northeurope', 'westeurope', 'francecentral', 'uksouth', 'westus2',
                                     'switzerlandnorth', 'eastus2', 'northcentralus', 'southcentralus', 'westcentralus')
        region_combobox.current()
        region_combobox.pack()
        region_frame.grid(row=1, padx=20, pady=10)

        language_frame = tk.Frame(self.root)
        language_label = tk.Label(language_frame, text='Choose language code')
        language_label.pack()
        self.v2 = tk.StringVar()
        language_combobox = tk.ttk.Combobox(language_frame, width=6, textvariable=self.v2)
        language_combobox['values'] = ('ar-EG', 'ca-ES', 'zh-HK', 'zh-CN', 'zh-TW', 'da-DK', 'es-ES', 'sv-SE', 'nl-NL',
                                       'en-AU', 'en-CA', 'en-GB', 'en-US', 'ru-RU', 'es-MX', 'th-TH', 'fi-FI', 'fr-CA',
                                       'fr-FR', 'de-DE', 'el-GR', 'hi-IN', 'ro-RO', 'it-IT', 'ja-JP', 'ko-KR', 'nb-NO',
                                       'pl-PL', 'pt-BR', 'pt-PT')
        language_combobox.current()
        language_combobox.pack()
        language_frame.grid(row=2, padx=20, pady=10)

        confirm_button = tk.Button(self.root, text='Save', command=self.save_data)
        confirm_button.grid(row=3, padx=20, pady=20)

        self.root.mainloop()

    def save_data(self):
        with open("config", "w") as config:
            config.write(self.key_entry.get() + '\n')
            config.write(self.v1.get() + '\n')
            config.write(self.v2.get())
            self.root.quit()
