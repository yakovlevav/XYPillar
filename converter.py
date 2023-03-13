import pandas as pd
import os
from io import StringIO
import re

class XYPconverter:
    def __init__(self):
        self.input_path = ''
        self.output_path = ''

# path = os.path.abspath("XYP_10_1_230724.txt")

with open(path, 'r') as file:
    dataset = file.read()
    parts = dataset.split('# Layout position')[1]

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
    gfids_data = dataset.split('# End of list.')[1]  
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

    # Find coordinate of the shift
    coordinates_1_1 = re.search(r'# Layout position 1,1 at (.*)', dataset).group(1)
    x1, y1 = coordinates_1_1.split()
    x1, y1 = float(x1[2:]), float(y1[2:])

    coordinates_2_1 = re.search(r'# Layout position 2,1 at (.*)', dataset).group(1)
    x2, y2 = coordinates_2_1.split()
    x2, y2 = float(x2[2:]), float(y2[2:])
    x = abs(x2-x1)
    y = abs(y2-y1)
    print(x, y)
    df.to_csv('XYP_10_1_230724_out.txt', index=False, sep=';')