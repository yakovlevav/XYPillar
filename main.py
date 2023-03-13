import customtkinter
import pandas as pd
import os
from io import StringIO
import re

try:
    import pyi_splash
    pyi_splash.update_text('XYPillar loadind...')
    pyi_splash.close()
except:
    pass

# import plotly.express as px
# df = px.data.iris()
# fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
# fig.show()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("500x300")
        self.title("XYPillar v0.1")
        self.minsize(800, 600)
        self.maxsize(800, 600)

        # create 2x2 grid system
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((5, 6), weight=1)

        self.label = customtkinter.CTkLabel(master=self, text="Input file")
        self.label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.textbox = customtkinter.CTkEntry(master=self)
        self.textbox.grid(row=0, column=2, padx=10, pady=10,  sticky="ew")

        self.button = customtkinter.CTkButton(master=self, command=self.button_callback, text="Open File")
        self.button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        self.button = customtkinter.CTkButton(master=self, command=self.convert, text="Save")
        self.button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        self.input_box = customtkinter.CTkTextbox(master=self, 
                                                width=400, corner_radius=15, wrap='none',
                                                text_color='light yellow', state='disable',
                                                border_color = 'light yellow')
        self.input_box.grid(row=1, column=1, columnspan=6, sticky="nsew", padx=10, pady=10)

        self.out_box = customtkinter.CTkTextbox(master=self, width=400, 
                                                corner_radius=15, wrap='none', 
                                                text_color='light green', state='disable',
                                                border_color = 'light green')
        self.out_box.grid(row=2, column=1, columnspan=6, sticky="nsew", padx=10, pady=10, )

    def button_callback(self):
        self.input_file_path = customtkinter.filedialog.askopenfilename(typevariable = 'str')
        base = os.path.basename(self.input_file_path)
        self.textbox.delete('0', customtkinter.END)
        self.textbox.insert("insert", "{}".format(base))
        self.input_file_name = os.path.splitext(base)[0]
        # print(self.input_file_name)

        with open(self.input_file_path, 'r') as file:
            self.dataset = file.read()

        self.input_box.configure(state='normal')
        self.input_box.delete('0.0', customtkinter.END)
        self.input_box.insert('0.0', self.dataset)
        self.input_box.configure(state='disable')

        self.convert()

        self.out_box.configure(state='normal')
        self.out_box.delete('0.0', customtkinter.END)
        self.out_box.insert('0.0',self.dataset_converted.to_csv(index=False, sep=';'))
        self.out_box.configure(state='disable')

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
        # print(x, y)

    def save(self):
        self.dataset_converted.to_csv( os.path.join(os.getcwd(),'Output',self.input_file_name+'_out.txt'), index=False, sep=';')


if __name__ == "__main__":
    app = App()
    app.mainloop()