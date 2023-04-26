import json
import subprocess
import sys
from pathlib import Path

import tkinter.filedialog as fd
from tkinter import *
from tkinter.ttk import Combobox
from tkinter.messagebox import showinfo
from requests import HTTPError
import translators as ts

LANGUAGES = {'Russian': 'ru', 'English': 'en', 'German': 'de', 'Spanish': 'es', 'French': 'fr'}


class AppInterface:

    def __init__(self):
        # window
        self.app = Tk()
        self.app.title("Localization tool")
        self.app.resizable(False, False)
        self.app.geometry("500x400")
        self.app.config(padx=20, pady=20)

        self.input_directory = None
        self.input_file = None
        self.output_directory = None
        self.language = None
        self.extensions = [('all allowed formats', '*.arb')]

        # canvas with logo
        self.canvas = Canvas(width=330, height=150)
        self.logo_img = PhotoImage(file="logo.png")
        self.canvas.create_image(165, 75, image=self.logo_img)
        self.canvas.grid(column=0, row=0, columnspan=3)

        # radio buttons
        self.r_var = StringVar()
        self.r_var.set('single')
        self.singe = Radiobutton(text='Translate single .arb file', variable=self.r_var, value='single')
        self.singe.grid(row=1, column=0, sticky='w', columnspan=2)
        self.multi = Radiobutton(text='Choose directory with .arb files', variable=self.r_var, value='multi')
        self.multi.grid(row=2, column=0, sticky='w', columnspan=2)

        # buttons
        self.select_path_btn = Button(text='Select', width=14, command=self.open)
        self.select_path_btn.grid(column=2, row=3, sticky='w')

        self.translate_btn = Button(text="Translate", width=26, command=self.save)
        self.translate_btn.grid(column=1, row=5, columnspan=3, sticky="w", pady=10, padx=10)

        # labels
        self.select_file_label = Label(text="File/Directory:")
        self.select_file_label.grid(column=0, row=3, sticky="e")

        self.select_language_label = Label(text="Target Language:")
        self.select_language_label.grid(column=0, row=4, sticky="e")

        # entries
        self.selected_path_entry = Entry(width=24)
        self.selected_path_entry.grid(column=1, row=3)

        # combobox
        self.language_combobox = Combobox(values=sorted(tuple(LANGUAGES.keys())))
        self.language_combobox.grid(column=1, row=4, columnspan=2, sticky="w", padx=10, pady=10)

        self.app.mainloop()

    def open(self):
        if self.r_var.get() == 'single':
            self.input_file = fd.askopenfilename(parent=self.app, initialdir='/', filetypes=self.extensions,
                                                 title='Select File')
            if self.input_file:
                showinfo(title='Selected Files', message=self.input_file)
                self.selected_path_entry.insert(0, self.input_file)
            else:
                showinfo(title='Selected Files', message="None")
        else:
            self.input_directory = fd.askdirectory(parent=self.app, initialdir='/',
                                                   title='Select Directory With .arb Files')
            if self.input_directory:
                showinfo(title='Selected Directory', message=self.input_directory)
                self.selected_path_entry.insert(0, self.input_directory)
            else:
                showinfo(title='Selected Files', message="None")

    def save(self):
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        if self.language_combobox.get():
            self.language = LANGUAGES[self.language_combobox.get()]
            if self.input_file:
                self.output_directory = fd.askdirectory(parent=self.app, initialdir=self.input_directory,
                                                        title='Save To')
                showinfo(title='Selected Directory To Save', message=self.output_directory)
                self.translate_single_file(self.input_file, self.language)
                self.input_file = None
                self.selected_path_entry.delete(0, END)
                self.language = None
                showinfo(title='Success', message='Translation Completed!')
                subprocess.call([opener, self.output_directory])
            elif self.input_directory:
                self.output_directory = fd.askdirectory(parent=self.app, initialdir=self.input_directory,
                                                        title='Save To')
                showinfo(title='Selected Directory To Save', message=self.output_directory)
                self.multiple_translation()
                self.input_directory = None
                self.selected_path_entry.delete(0, END)
                self.language = None
                showinfo(title='Success', message='Translation Completed!')
                subprocess.call([opener, self.output_directory])
            else:
                showinfo(title='Warning', message='Please, choose file or directory!')
        else:
            showinfo(title='Warning', message='Please, choose a target language!')

    def translate(self, text, lang):
        translated_text = ''
        try:
            translated_text = ts.translate_text(text, from_language='auto', to_language=lang, translator='google')
            return translated_text
        except HTTPError:
            print("HTTPError, try to use another translator in parameter translator")
            return translated_text

    def translate_single_file(self, file_path, lang):
        input_path = Path(file_path)
        file_name = input_path.stem
        if Path(file_path).is_file() and Path(file_path).suffix == '.arb':
            try:
                with open(file_path, encoding='utf-8') as file:
                    text = file.read()
                    # get list of tuples with key-value pairs from arb
                    decoded_arb_file = json.loads(text, object_pairs_hook=list)
            except Exception as err:
                print(err)
            # get values from arb file and converse it to single string of values using line break for delimiter
            # it needs to send one request to translator API instead of many for each value"""
            values_str = '\n'.join([key_value[1] for key_value in decoded_arb_file])

            translated_values_list = self.translate(values_str, lang).split('\n')

            # collect output arb with translated values
            output_arb = {value[0]: translated_values_list[index] for index, value in enumerate(decoded_arb_file)}

            output_file_name = f'translated_{Path(file_name).stem}.arb'
            output_path = f'{self.output_directory}/{output_file_name}'

            with open(output_path, "w", encoding="utf-8") as write_file:
                json.dump(output_arb, write_file, ensure_ascii=False)

    def multiple_translation(self):
        all_files = []
        for ext in self.extensions:
            all_files.extend(Path(self.input_directory).glob(ext[1]))

        for index, item in enumerate(all_files):
            self.translate_single_file(item, self.language)
            print(f"Completed: {index + 1}/{len(all_files)}")


def main():
    app = AppInterface()


if __name__ == "__main__":
    main()
