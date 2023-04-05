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
from matplotlib.widgets import RadioButtons
import numpy as np

from pandastable import Table, TableModel, config

plt.switch_backend("Agg") # Destroy app after closing
# import version_query

# try:
#     # version_str = version_query.predict_version_str()
# except Exception as e:
version_str = '0.2.1'
try:
    import pyi_splash
    pyi_splash.update_text('XYPillar loadind...')
    pyi_splash.close()
except: pass



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # self.state('zoomed')
        window_width = 1920
        window_height = 1080
        
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
        self.minsize(1920, 1080)
        
        self.create_main_grid()
        self.sidebar()
        self.main_bar()
        self.DataTable()
        self.draw_plot_mainframe()
        
        
    def create_main_grid(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=30)
        self.columnconfigure(2, weight=5)
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
        
        #Create frame
        self.table_buttons_frame = customtkinter.CTkFrame(
            master=self.sidebar_frame, 
            corner_radius=10,
            )
        self.table_buttons_frame.grid(
            row=3, 
            column=0, 
            sticky="news",
            padx=10, 
            pady=10,
        )
        self.table_buttons_frame.columnconfigure(0, weight = 1)
        self.table_buttons_frame.rowconfigure(0, weight = 1)
        self.table_buttons_frame.rowconfigure(1, weight = 1)
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
        self.table_buttons_frame.columnconfigure(0, weight = 1)
        self.reset_table_button = customtkinter.CTkButton(master=self.table_buttons_frame, 
                                              command= self.update_table, 
                                              text="Reset table")
        self.reset_table_button.grid(
            row=1, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="news"
            )
        
        self.export_button = customtkinter.CTkButton(master=self.sidebar_frame, 
                                              command=self.save, 
                                              text="Export")
        self.export_button.grid(row=4, column=0, padx=20, pady=10, sticky="n")
    
    def board_filder_selector(self):
        if not hasattr(self, 'dataset_converted') : return #Check of you have no data
        self.selector_boards = customtkinter.CTkFrame(
            master=self.sidebar_frame, 
            corner_radius=10,
            )
        self.selector_boards.grid(
            row=5, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="news"
            )

        for i, k in enumerate(self.dataset_converted.BoardNumber.unique()):
            checkbox = customtkinter.CTkCheckBox(
                master=self.selector_boards, 
                text=k,
                # variable=True,
                onvalue=True, 
                offvalue=False
                )
            checkbox.grid(
                row=i, 
                column=0, 
                padx=10, 
                pady=10, 
                sticky="news"
                )
        self.update()
    
    def apply_table(self):
        df = self.table.model.df
        if df.empty: 
            return
        else:
            self.dataset_converted = df
        self.clear_out_box()
        self.plot_xyp()
        self.insert_out_box(self.dataset_converted.to_csv(index=False, sep=self.output_sep))
        self.update()
        
    def main_bar(self):
        self.main_frame = customtkinter.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.main_frame.grid(row=0, column=2, sticky="news")
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
            column=1, 
            sticky="news",
            padx=20, 
            pady=20
            )

        self.table = Table(self.datatable_frame, 
                           dataframe=pd.DataFrame(),
                        #    showtoolbar=True, 
                            width=300, maxcellwidth=200,
                           showstatusbar=True,
                           )
        self.table.show()
        
    def update_table(self):
        self.table.resetIndex(False)
        self.table.updateModel(TableModel(self.dataset_converted))
        options = {'fontsize':9, 'align':'center'}
        config.apply_options(options, self.table)
        self.table.adjustColumnWidths()
        # self.table.multiplecollist = [2]
        # self.table.setColorbyValue()
        self.table.redraw()
        
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
        self.dataset_converted = pd.DataFrame()
        #Clearing plot
        self.clear_plot()
        self.set_status("All cleared!")
        
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
        self.update_table()
        self.plot_xyp()
        self.set_status("Data ready for review")
        self.insert_out_box(self.dataset_converted.to_csv(index=False, sep=self.output_sep))
        self.board_filder_selector()
                    
    def convert(self):
        boards = self.dataset.split('\n\n')
        def board_converter(board_data):
            df = pd.read_csv(StringIO(board_data), 
                            sep='|',
                            comment = "#",
                            # skiprows=1,
                            names = ['Ref. Designator', 'Part Number', 'Package', 'Rotation', 'X', 'Y', 'Side', 'BoardNumber'],
                            usecols= [0, 2, 5, 6, 7, 8, 9, 12],
                            converters={'Part Number': lambda x: x.split(',')[0].split('-', 1)[1]},
                            dtype = {'BoardNumber':str}
                            )
            return(df)
        
        #Get All boads in dictionary with number name
        d = dict()
        for i, k in enumerate(boards[1:-2]):
            df = board_converter(k)
            df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
            d.update({df.BoardNumber.iloc[0] : df})
            
        # #Read glob fiducials
        gfids = pd.read_csv(StringIO(boards[-2]),
                            sep='|', 
                            comment = "#",
                            names=["Side", "Ref. Designator", "X", "Y"],
                            usecols=range(4),
                            )
        gfids['Part Number'] = 'GlobFig'
        gfids['Package'] = 'GFID'
        gfids['BoardNumber'] = 'Panel'
        gfids['Rotation'] = 0
        gfids.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        d.update({'glob_fids':gfids})
        # Concat all dataframe to multi index
        self.dataset_converted = pd.concat(d.values(), keys=d.keys(), axis=0)

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
            sticky="w",
            padx=15, 
            pady=15,
        )
        # self.package_switch = customtkinter.CTkSwitch(
        #     master=self.plot_buttons_frame, 
        #     text="Package Names", 
        #     command=self.plot_xyp,
        #     onvalue=True, 
        #     offvalue=False
        #     )
        # self.package_switch.grid(
        #     row=0, 
        #     column=1, 
        #     # sticky="w",
        #     padx=10, 
        #     pady=10,
        # )
        # self.designator_switch = customtkinter.CTkSwitch(
        #     master=self.plot_buttons_frame, 
        #     text="Designator", 
        #     command=self.plot_xyp,
        #     onvalue=True, 
        #     offvalue=False
        #     )
        # self.designator_switch.grid(
        #     row=0, 
        #     column=3, 
        #     # sticky="w",
        #     padx=10, 
        #     pady=10,
        # )
                
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
        toolbarFrame = customtkinter.CTkFrame(self.plot_frame, bg_color='red')
        toolbarFrame.grid(row=3,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        self.boads_plots, = self.ax.plot([],[])
        
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
        
        df = self.dataset_converted
        
        side_selection = self.side_select.get()
        # partnumber_selection = self.package_switch.get()
        # designator_selection = self.designator_switch.get()
        if side_selection != "BOTH": 
            df = df.query('Side.str.contains(@side_selection)', engine='python')
        grouped = df.groupby('BoardNumber')
        
        for BoardNumber, data in grouped:
            self.ax.plot(
                data.X, 
                data.Y, 
                label = BoardNumber, 
                marker='s', 
                markersize=3, 
                alpha=0.5, 
                linestyle='',
                )
            # if partnumber_selection:
            #     for i, x in enumerate(data.X):
            #         self.ax.annotate(
            #             partnumber,
            #             (x, data.Y.iloc[i]),
            #             # fontsize=6,
            #             alpha=0.3,
            #             ha='center',
            #             va="bottom",
            #             )
            # if designator_selection:
            #     for i, x in enumerate(data.X):
            #         self.ax.annotate(
            #             data['Ref. Designator'].iloc[i], 
            #             (x, data.Y.iloc[i]), 
            #             # fontsize=6, 
            #             alpha=0.3, 
            #             ha='center', 
            #             va="top",
            #             )
        # self.ax.lines[0].remove()
        # print(list(self.ax.get_lines()).remove(0))
        # self.ax.scatter(x,y)
        # self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
        #   ncol=8, fancybox=True, prop={'size': 5})
        # self.canvas.get_tk_widget()
        # self.fig.canvas.draw_idle()
        # self.update()
        
    def plot_package():
        choice = self.side_select.get()
        partnumber_selection = self.package_switch.get()
        designator_selection = self.designator_switch.get()
        df = self.dataset_converted
        if choice != "BOTH": 
            df = df.query('Side == @choice')
        grouped = df.groupby('Part Number')
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
        
         
if __name__ == "__main__":
    app = App()
    app.mainloop()