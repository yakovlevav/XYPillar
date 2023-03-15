import customtkinter
import pandas as pd
import os
from io import StringIO
import re
from PIL import Image
from datetime import datetime

import version_query

try:
    version_str = version_query.predict_version_str()
except Exception as e:
    version_str = '0.1.0'

try:
    import pyi_splash
    pyi_splash.update_text('XYPillar loadind...')
    pyi_splash.close()
except: pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        window_width = 800
        window_height = 750

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # Make window with size and in the center of the sreen
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, center_x, center_y))
        self.title("XYPillar {}".format(version_str))
        self.iconbitmap("XYpillar.ico")
        self.minsize(800, 750)
        self.maxsize(800, 750)
        self.attributes('-topmost',True) #Bring window on top
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(3)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="XYPillar", 
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.my_image = customtkinter.CTkImage(light_image=Image.open("XYpillar.png"),
                                  dark_image=Image.open("XYpillar.png"),
                                  size=(150, 150))
        
        self.logo = customtkinter.CTkLabel(self.sidebar_frame, text='', image=self.my_image)
        self.logo.grid(row=1, column=0, padx=20, pady=(20, 10))


        self.button = customtkinter.CTkButton(master=self.sidebar_frame, 
                                              command=self.button_callback, 
                                              text="Open XYP File")
        self.button.grid(row=2, column=0, padx=20, pady=10)

        self.button = customtkinter.CTkButton(master=self.sidebar_frame, 
                                              command=self.save, 
                                              text="Export")
        self.button.grid(row=3, column=0, padx=20, pady=10, sticky="n")

        self.main_frame = customtkinter.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        # self.main_frame.grid_rowconfigure(2)
        # self.main_frame.grid_columnconfigure(1)

        self.label = customtkinter.CTkLabel(master=self.main_frame, text="Input file:", anchor='e',)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.textbox = customtkinter.CTkEntry(master=self.main_frame, state='disabled')
        self.textbox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.input = customtkinter.CTkLabel(master=self.main_frame, text="Input data", anchor='sw', text_color='grey')
        self.input.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

        self.input_box = customtkinter.CTkTextbox(master=self.main_frame, 
                                                width=590, corner_radius=15, wrap='none',
                                                text_color='light yellow', state='disabled',
                                                border_color = 'light yellow')
        self.input_box.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.output = customtkinter.CTkLabel(master=self.main_frame, text="Converted data", anchor='sw', text_color='grey')
        self.output.grid(row=3, column=0, padx=10, pady=0, sticky="nsew")
        self.out_box = customtkinter.CTkTextbox(master=self.main_frame, width=590, 
                                                corner_radius=15, wrap='none', 
                                                text_color='light green', state='disabled',
                                                border_color = 'light green')
        self.out_box.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.status = customtkinter.CTkLabel(master=self.main_frame, text="Status log", anchor='sw', text_color='grey')
        self.status.grid(row=5, column=0, padx=10, pady=0, sticky="nsew")
        self.statusbox = customtkinter.CTkTextbox(master=self.main_frame, state='disabled', height=150, text_color='grey')
        self.statusbox.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def set_status(self, status):
        self.statusbox.configure(state='normal')
        self.statusbox.insert('0.0', "{}: {}\n".format(datetime.now(),status))
        self.statusbox.configure(state='disabled')

    def button_callback(self):
        self.input_file_path = customtkinter.filedialog.askopenfilename(filetypes=[("Text files","*.txt")])
        self.set_status("File input path: {}".format(self.input_file_path))
        base = os.path.basename(self.input_file_path)
        self.textbox.configure(state='normal')
        self.textbox.delete('0', customtkinter.END)
        self.textbox.insert("insert", "{}".format(base))
        self.textbox.configure(state='disabled')
        self.input_file_name = os.path.splitext(base)[0]

        
        try:
            with open(self.input_file_path, 'r') as file:
                self.dataset = file.read()
            self.set_status("File opened")
        except:
            self.set_status("Unable to open file!")
            return()
        

        self.input_box.configure(state='normal')
        self.input_box.delete('0.0', customtkinter.END)
        self.input_box.insert('0.0', self.dataset)
        self.input_box.configure(state='disabled')

        self.convert()
        self.set_status("File converted successfully")
        self.out_box.configure(state='normal')
        self.out_box.delete('0.0', customtkinter.END)
        self.out_box.insert('0.0',self.dataset_converted.to_csv(index=False, sep=';'))
        self.out_box.configure(state='disabled')

    def convert(self):
        parts = self.dataset.split('# Layout position')[1]
        #Read first board position
        #Get header
        header = pd.read_csv(StringIO(parts), 
                            sep='|', 
                            skiprows=1, 
                            nrows=0, 
                            ).columns.str.strip()
        #Get body
        df = pd.read_csv(StringIO(parts), 
                        sep='|',
                        comment = "#",
                        skiprows=1,
                        names = header,
                        usecols= ['#refdes', 'device type', 'cRot(P)', 'cX(P)', 'cY(P)', 'side(P)']
                        )
        df[ ["Part Number", 'device type'] ] = df['device type'].str.split(',', n = 1, expand=True)
        df[ ["Package", 'Part Number'] ] = df['Part Number'].str.split('-', n = 1, expand=True)
        #Drops and renames
        df = df.drop(columns = 'device type')
        df = df.rename(columns={'#refdes': "Ref. Designator", 'side(P)':"Side", 'cRot(P)':'Rotation', 'cX(P)':'X', 'cY(P)':'Y'})

        #Read glob fiducials
        gfids_data = self.dataset.split('# End of list.')[1]  
        gfids = pd.read_csv(StringIO(gfids_data), 
                            sep='|', 
                            comment = "#",
                            names=["Side", "Ref. Designator", "X", "Y", 'blank'],
                            usecols=range(4),
                            )

        #Modes for glob fids
        gfids['Part Number'] = 'GlobFig'
        gfids['Package'] = 'GFID'
        gfids['Rotation'] = 0
        df = pd.concat([df,gfids],ignore_index=True)
        df = df.sort_values('Ref. Designator')

        #Final adjustments before export, sorting, striping
        df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        df = df[['Ref. Designator', 'Part Number', 'Package', 'Rotation', 'X', 'Y', 'Side']]
        self.dataset_converted = df

        # Find coordinate of the shift
        coordinates_1_1 = re.search(r'# Layout position 1,1 at (.*)', self.dataset).group(1)
        x1, y1 = coordinates_1_1.split()
        x1, y1 = float(x1[2:]), float(y1[2:])

        coordinates_2_1 = re.search(r'# Layout position 2,1 at (.*)', self.dataset).group(1)
        x2, y2 = coordinates_2_1.split()
        x2, y2 = float(x2[2:]), float(y2[2:])
        x = abs(x2-x1)
        y = abs(y2-y1)
        self.set_status("Your panel steps: X:{} Y:{}".format(x,y))

    def save(self):
        self.output_file_path = customtkinter.filedialog.askdirectory()
        if not self.output_file_path:
            self.set_status("No output path selected!")
            return
        try:
            path = os.path.join(os.getcwd(),'Output',self.input_file_name+'_converted.txt')
            self.dataset_converted.to_csv( path, index=False, sep=';')
            self.set_status("File saved successfully")
            self.set_status("File path: {}".format(path))
        except:
            self.set_status("Unable to export file!")


if __name__ == "__main__":
    app = App()
    app.mainloop()