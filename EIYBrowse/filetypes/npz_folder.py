from .my5c_folder import My5CFolder, My5cFile
import numpy as np
import pandas as pd


class NpzFolder(My5CFolder):
    def __init__(self, folder_path):

        super(NpzFolder, self).__init__(folder_path,
                                        file_class=NpzFile)
        
        self.extension = 'npz'
    
class NpzFile(My5cFile):
    def __init__(self, file_path):
        
        data = np.load(file_path)
        self.interactions = data['scores']
        self.windows = self.format_windows(data['windows'])
        
    def format_windows(self, windows):
        
        def format_window(window):
            
            chrom = window[0]
            start, stop = map(int, window[1:])
            return chrom, start, stop
        
        return pd.MultiIndex.from_tuples(map(format_window, windows),
                                         names=['chrom', 'start', 'stop'])
