import os
import glob
import numpy as np
import pandas as pd
import pybedtools

class TooManyFilesError(Exception):
    pass

class My5CFolder(object):
    def __init__(self, folder_path):
        
        self.folder_path = folder_path
        
    def find_chrom_file(self, chrom):
        
        search_string = '*{0}_{0}*.my5c.txt'.format(chrom)
        
        found_files = glob.glob(os.path.join(self.folder_path, search_string))
        
        if len(found_files) > 1:
            raise TooManyFilesError('folder containing my5c files must have only one my5c file per chromosome')
            
        return found_files[0]
    
    def get_my5c_file(self, chrom):

        my5c_path = self.find_chrom_file(chrom)
        
        return My5cFile(my5c_path)

    def interactions(self, feature):

        my5c_file = self.get_my5c_file(feature.chrom)
        
        return my5c_file.get_interactions(feature)

    
class My5cFile(object):
    def __init__(self, file_path):
        
        data = pd.read_csv(file_path,
                           sep='\t', index_col=0)

        self.interactions = np.array(data)
        self.windows = self.format_windows(data.index)
        
    def format_windows(self, windows):
        
        def format_window(window):
            parts = window.split('|')
            location = parts[-1]
            chrom, pos = location.split(':')
            start, stop = map(int, pos.split('-'))
            return chrom, start, stop
        
        return pd.MultiIndex.from_tuples(map(format_window, windows),
                                         names=['chrom', 'start', 'stop'])
    
    def index_from_interval(self, feature):

        window_in_region = np.logical_and(
                                np.logical_and(
                                    self.windows.get_level_values('start') >= feature.start,
                                    self.windows.get_level_values('stop') <= feature.stop),
                                    self.windows.get_level_values('chrom') == feature.chrom)

        covered_windows = np.nonzero(window_in_region)[0]
        start_index = covered_windows[0]
        stop_index = covered_windows[-1] + 1 

        return start_index, stop_index

    def get_interactions(self, feature):
        
        start, stop = self.index_from_interval(feature)
        
        return self.interactions[start:stop, start:stop], self.indices_to_interval(start, stop)
    
    def indices_to_interval(self, start, stop):
        
        start_window = self.windows[start]
        stop_window = self.windows[stop - 1]
        return pybedtools.Interval(start_window[0], start_window[1], stop_window[2])
