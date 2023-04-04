import customtkinter
from tkinter import messagebox
import pandas as pd
import os
from io import StringIO
import re
from PIL import Image
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pandastable import Table, TableModel

plt.switch_backend("Agg") # Destroy app after closing

# import version_query

# try:
#     # version_str = version_query.predict_version_str()
# except Exception as e:
version_str = '0.1.1'

try:
    import pyi_splash
    pyi_splash.update_text('XYPillar loadind...')
    pyi_splash.close()
except: pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        window_width = 1500
        window_height = 800
        
        self.output_sep = '\t'

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # Make window with size and in the center of the sreen
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, center_x, center_y))
        self.title("XYPillar {}".format(version_str))
        self.iconbitmap(os.path.join(os.path.dirname(__file__), "XYpillar.ico") )
        self.minsize(1500, 750)
        self.create_main_grid()
        self.sidebar()
        self.main_bar()
        self.DataTable()
        self.draw_plot_mainframe()
        
    def create_main_grid(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=20)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight= 1)

    def sidebar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="news")
        self.sidebar_frame.columnconfigure(0, weight = 1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="XYPillar", 
            font=customtkinter.CTkFont(size=20, weight="bold")
            )
        self.logo_label.grid(
            row=0, 
            column=0, 
            padx=20, 
            pady=(20, 10),
            )
        
        self.my_image = customtkinter.CTkImage(
            light_image=Image.open("XYpillar.png"),
            dark_image=Image.open( os.path.join(os.path.dirname(__file__), "XYpillar.png" )),
            size=(150, 150)
            )
        self.logo = customtkinter.CTkLabel(
            self.sidebar_frame,
            text='', 
            image=self.my_image)
        self.logo.grid(
            row=1, 
            column=0, 
            padx=20, 
            pady=(20, 10))


        self.open_button = customtkinter.CTkButton(master=self.sidebar_frame, 
                                              command=self.open_callback, 
                                              text="Open XYP File")
        self.open_button.grid(row=2, column=0, padx=20, pady=10)

        self.export_button = customtkinter.CTkButton(master=self.sidebar_frame, 
                                              command=self.save, 
                                              text="Export")
        self.export_button.grid(row=3, column=0, padx=20, pady=10, sticky="n")
        
        #Create frame
        self.table_buttons_frame = customtkinter.CTkFrame(
            master=self.sidebar_frame, 
            corner_radius=10,
            )
        self.table_buttons_frame.grid(
            row=4, 
            column=0, 
            sticky="news",
            padx=10, 
            pady=10,
        )
        self.table_buttons_frame.columnconfigure(0, weight = 1)
        self.apply_table_button = customtkinter.CTkButton(master=self.table_buttons_frame, 
                                              command=self.apply_table, 
                                              text="Apply table")
        self.apply_table_button.grid(
            row=0, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="news"
            )
    
    def apply_table(self):
        self.dataset_converted = self.table.model.df
        
    def main_bar(self):
        self.tab_view = customtkinter.CTkTabview(master=self)
        self.tab_view.grid(row=0, 
                           column=1, 
                           padx=10, 
                           pady=10,
                           sticky='news'
                           )
        self.tab_view.add("Text Data")
        self.tab_view.add("Edit Table")
        self.tab_view.tab("Text Data").columnconfigure(0, weight=1)
        self.tab_view.tab("Text Data").rowconfigure(0, weight=1)
        self.tab_view.tab("Edit Table").columnconfigure(0, weight=1)
        self.tab_view.tab("Edit Table").rowconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self.tab_view.tab("Text Data"), fg_color='transparent', corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="news")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=10)
        self.main_frame.rowconfigure(0, weight= 1)
        self.main_frame.rowconfigure(1, weight= 1)
        self.main_frame.rowconfigure(2, weight= 50)
        self.main_frame.rowconfigure(3, weight= 1)
        self.main_frame.rowconfigure(4, weight= 50)
        self.main_frame.rowconfigure(5, weight= 1)
        self.main_frame.rowconfigure(6, weight= 1)
        
        self.label = customtkinter.CTkLabel(
            master=self.main_frame, 
            text="Input file:", 
            anchor='e'
            )
        self.label.grid(
            row=0, 
            column=0, 
            padx=10, 
            pady=10,
            sticky="ew"
            )

        self.file_name_box = customtkinter.CTkEntry(
            master=self.main_frame, 
            state='disabled',
            width=200
            )
        self.file_name_box.grid(
            row=0,
            column=1, 
            padx=10, 
            pady=10,
            sticky="w"
            )

        self.input = customtkinter.CTkLabel(
            master=self.main_frame, 
            text="Input data", 
            anchor='w'
            )
        self.input.grid(
            row=1, 
            column=0, 
            padx=20, 
            pady=0,
            sticky="news"
            )

        self.input_box = customtkinter.CTkTextbox(
            master=self.main_frame, 
            corner_radius=15,
            wrap='none',
            state='disabled',
            )
        self.input_box.grid(
            row=2, 
            column=0, 
            columnspan=2, 
            padx=10, 
            pady=10,
            sticky="news"
            )

        self.output = customtkinter.CTkLabel(
            master=self.main_frame, 
            text="Converted data", 
            anchor='w')
        self.output.grid(
            row=3, 
            column=0, 
            padx=20, 
            pady=0,
            sticky="news"
            )
        
        self.out_box = customtkinter.CTkTextbox(
            master=self.main_frame, 
            corner_radius=15, wrap='none', 
            state='disabled',)
        self.out_box.grid(
            row=4, 
            column=0, 
            columnspan=2, 
            padx=10, 
            pady=10,
            sticky="news"
            )

        self.status = customtkinter.CTkLabel(
            master=self.main_frame, 
            text="Status log", 
            anchor='w')
        self.status.grid(
            row=5, 
            column=0, 
            padx=20, 
            pady=0,
            sticky="news"
            )
        self.statusbox = customtkinter.CTkTextbox(
            master=self.main_frame, 
            state='disabled', 
            )
        self.statusbox.grid(
            row=6, 
            column=0, 
            columnspan=2, 
            padx=10, 
            pady=10,
            sticky="news"
            )
        
    def DataTable(self):
        self.datatable_frame = customtkinter.CTkFrame(self)
        self.datatable_frame.grid(
            row=0, 
            column=2, 
            sticky="news",
            padx=20, 
            pady=20
            )

        if not hasattr(self, 'dataset_converted') : 
            df = pd.DataFrame() #Check of you have no data
        else:
            df = self.dataset_converted
        self.table = Table(self.datatable_frame, 
                           dataframe=df,
                           showtoolbar=True, 
                           showstatusbar=True)
        self.table.show()
        
    def set_status(self, status):
        self.statusbox.configure(state='normal')
        self.statusbox.insert('0.0', "{}: {}\n".format(datetime.now(),status))
        self.statusbox.configure(state='disabled')
    
    def clear_file_name_box(self):
        self.file_name_box.configure(state='normal')
        self.file_name_box.delete("0", customtkinter.END)
        self.file_name_box.configure(state='disabled')
    
    def clear_input_box(self):
        self.input_box.configure(state='normal')
        self.input_box.delete("0.0", customtkinter.END)
        self.input_box.configure(state='disabled')
    
    def clear_out_box(self):
        self.out_box.configure(state='normal')
        self.out_box.delete("0.0", customtkinter.END)
        self.out_box.configure(state='disabled')
        
    def file_name_box_insert(self, text):
        self.file_name_box.configure(state='normal')
        self.file_name_box.insert("insert", "{}".format(text))
        self.file_name_box.configure(state='disabled')
        
    def insert_input_box(self, data):
        self.input_box.configure(state='normal')
        self.input_box.delete('0.0', customtkinter.END)
        self.input_box.insert('0.0', data)
        self.input_box.configure(state='disabled')

    def insert_out_box(self, data):
        self.out_box.configure(state='normal')
        self.out_box.delete('0.0', customtkinter.END)
        self.out_box.insert('0.0', data)
        self.out_box.configure(state='disabled')

    def clear_plot(self):
        self.ax.cla() 
        self.fig.canvas.draw_idle()
        
    def clean_all(self):
        self.clear_file_name_box()
        self.clear_input_box()
        self.clear_out_box()
        self.dataset = None
        self.input_file_name = None
        #Clearing plot
        self.clear_plot()
        
    def open_callback(self):
        self.clean_all()
        
        self.input_file_path = customtkinter.filedialog.askopenfilename(filetypes=[("Text files","*.txt")])
        if not self.input_file_path: return
        self.set_status("File input path: {}".format(self.input_file_path))
        base = os.path.basename(self.input_file_path)
        self.file_name_box_insert(base)
        
        self.input_file_name = os.path.splitext(base)[0]
        
        try:
            with open(self.input_file_path, 'r') as file:
                self.dataset = file.read()
            self.set_status("File opened")
        except:
            self.set_status("Unable to open file!")
            return()
        
        self.insert_input_box(self.dataset)
        self.convert()
        self.set_status("File converted successfully")
        self.DataTable()
        self.plot_xyp()
        
        self.insert_out_box(self.dataset_converted.to_csv(index=False, sep=self.output_sep))

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
        if not self.input_file_name:return
        path_name = customtkinter.filedialog.asksaveasfilename(filetypes=[("Text files","*.txt")], initialfile = self.input_file_name+'_converted.txt')
        self.output_file_path = os.path.normpath(path_name)

        if not self.output_file_path:
            self.set_status("No output path selected!")
            return
        try:
            self.dataset_converted.to_csv(self.output_file_path, index=False, sep=self.output_sep, mode='w')
            self.set_status("File path: {}".format(self.output_file_path))
            self.set_status("File saved successfully")

        except Exception as e:
            self.set_status("Unable to export file: {}".format(str(e)))
        
    def draw_plot_mainframe(self):
        #Create main frame with configuration
        self.plot_frame = customtkinter.CTkFrame(self, corner_radius=20)
        self.plot_frame.grid(
            row=0, 
            column=3, 
            sticky="news",
            padx=20, 
            pady=20
            )
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight= 1)
        self.plot_frame.rowconfigure(1, weight= 20)
        self.plot_frame.rowconfigure(2, weight= 1)
        #Create frame for buttons
        self.plot_buttons_frame = customtkinter.CTkFrame(
            master=self.plot_frame, 
            corner_radius=20
            )
        self.plot_buttons_frame.grid(
            row=0, 
            column=0, 
            sticky="news",
            padx=10, 
            pady=10,
            )
        self.plot_buttons_frame.columnconfigure(0, weight=1)
        self.plot_buttons_frame.columnconfigure(1, weight=1)
        self.side_select = customtkinter.CTkOptionMenu(master=self.plot_buttons_frame,
                                       values=["BOTH", "TOP", "BOTTOM"],
                                       command=self.plot_xyp)
        self.side_select.grid(
            row=0, 
            column=0, 
            # sticky="w",
            padx=10, 
            pady=10,
        )
        self.pachage_switch = customtkinter.CTkSwitch(
            master=self.plot_buttons_frame, 
            text="Package Names", 
            command=self.plot_xyp,
            onvalue=True, 
            offvalue=False
            )
        self.pachage_switch.grid(
            row=0, 
            column=1, 
            # sticky="w",
            padx=10, 
            pady=10,
        )
        
        
        self.fig, self.ax = plt.subplots(
            # figsize = (10/2.54,5.8/2.54)
            )
        self.canvas = FigureCanvasTkAgg(self.fig,master= self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=1, 
            column=0, 
            # padx=20, 
            # pady= 20,
            sticky='news'
        )
        #Matplotlib Toolbar
        toolbarFrame = customtkinter.CTkFrame(self.plot_frame)
        toolbarFrame.grid(row=2,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)   
        
    def plot_xyp(self, selection=None):
        if not hasattr(self, 'dataset_converted') : return #Check of you have no data
        self.clear_plot() #Clear plot
        #Make layout adjustments
        self.fig.tight_layout()
        self.ax.set_xlim(0,100)
        self.ax.set_ylim(0,58)
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(4))
        self.ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        self.ax.set_aspect('equal') #Keeps ratio of the axis
        
        choice = self.side_select.get()
        partnumber_selection = self.pachage_switch.get()
        df = self.dataset_converted
        if choice != "BOTH": 
            df = df.query('Side == @choice')
        grouped = df.groupby('Part Number')
        # grouped.plot("X",'Y', ax=self.ax, kind='scatter')
        for partnumber, data in grouped:
            self.ax.plot(
                data.X, 
                data.Y, 
                label = partnumber, 
                marker='s', 
                markersize=3, 
                alpha=0.5, 
                linestyle='',
                )
            if partnumber_selection:
                for i, x in enumerate(data.X):
                    self.ax.annotate(
                        partnumber, 
                        (x, data.Y.iloc[i]), 
                        # fontsize=6, 
                        alpha=0.3, 
                        ha='center', 
                        va="bottom",
                        )
        # self.ax.scatter(x,y)
        # self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
        #   ncol=8, fancybox=True, prop={'size': 5})
        self.canvas.get_tk_widget()
        self.fig.canvas.draw_idle()
        self.update()
        
         
if __name__ == "__main__":
    app = App()
    app.mainloop()