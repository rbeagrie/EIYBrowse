from .base import Panel
import sqlite3
import pybedtools
from PIL import Image
import numpy as np
from pandas.io import sql

class InteractionsBasePanel(Panel):
    """Base panel for displaying 3D interactions data (e.g. Hi-C) across a genomic region"""
    def __init__(self, flip, log, **kwargs):
        super(InteractionsBasePanel, self).__init__()
        self.flip, self.log, self.kwargs = flip, log, kwargs
        
    def get_config(self, feature):

        return { 'lines' : 16 }
    
    def rotate_to_fit_ax(self, ax, data, flip=False):
    
        # The width will be equal to the diagonal of the rotated square
        
        # Make a PIL image from a copy of the array (due to a PIL 2to3 bug)
        # When we rotate, the new background will be at 0.0 - add 100 to 
        # everything so that we can distinguish bins that were 0 to start
        # with.
        im = Image.fromarray(data.copy()+100)
        
        # Resize the data so that the diagonal = width
        #im = im.resize((350,350))
        im = im.resize((800,800))
                
        # Rotate the data and expand to fit the new diagonal
        rot = im.rotate(45, expand=True)
            
        new_width = rot.size[0]
        
        rot = rot.crop((0,0,new_width,new_width / 2))

        
        if flip:
            rot = rot.transpose(Image.FLIP_TOP_BOTTOM)
                
        rot = np.array(rot)
        
        # Any 0's are actually background, so set them to NAN
        rot[rot == 0.] = np.NAN
        
        # Now take off the 100 we added before:
        rot -= 100.
        
        return rot
    
    def _plot(self, ax, feature, flip=False):
        
        ax.axis('off')

        data, new_feature = self.interactions(feature)
        
        rotated = self.rotate_to_fit_ax(ax, data, self.flip)
        
        if self.log:
            rotated = np.log10(rotated)
        
        img = ax.imshow(rotated, interpolation='none', **self.kwargs)
        
        return new_feature

class InteractionsDbPanel(InteractionsBasePanel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) across a genomic region"""
    def __init__(self, interactions_db, flip, log, **kwargs):
        super(InteractionsDbPanel, self).__init__(flip, log, **kwargs)

        self.db = sqlite3.connect(interactions_db)
        self.pos_query = "SELECT i FROM windows WHERE chrom = '{chrom}' AND start <= {start} ORDER BY start DESC LIMIT 1;"
        self.loc_query = "SELECT start, stop FROM windows WHERE i = '{i}' AND chrom = '{chrom}' LIMIT 1;"        

    def get_data_from_bins(self, chrom, start, stop):
            
        query_string = """select x, y, value from {chrom} 
                          where x >= '{start}' and x <= '{stop}'
                          and y >= '{start}' and y <= '{stop}';"""
        
        query = query_string.format(start=start, stop=stop,
                                    chrom=chrom)
                
        data_array = np.array(sql.read_sql(query, self.db).set_index(['x','y']).unstack())

        N = data_array.shape[0]

        data_array.flat[0:N**2:N + 1] = np.NAN

        return data_array
    
    def get_bin_from_location(self, chrom, location):
        pos = sql.read_sql(self.pos_query.format(chrom=chrom, start=location), self.db)
        return pos.values[0,0]
    
    def get_location_from_bin(self, chrom, i):
        loc = sql.read_sql(self.loc_query.format(chrom=chrom, i=i), self.db)
        return tuple(loc.values[0])
    
    def bins_from_feature(self, feature):

        start_bin = self.get_bin_from_location(feature.chrom, feature.start)
        stop_bin = self.get_bin_from_location(feature.chrom, feature.stop)

        return feature.chrom, start_bin, stop_bin
    
    def feature_from_bins(self, chrom, start_bin, stop_bin):
        
        lstart, lstop = self.get_location_from_bin(chrom, start_bin)
        rstart, rstop = self.get_location_from_bin(chrom, stop_bin)
        
        return pybedtools.Interval(chrom, lstart, rstop)
    
    def interactions(self, feature):
        
        chrom, start, stop = self.bins_from_feature(feature)
                
        return self.get_data_from_bins(chrom, start, stop), self.feature_from_bins(chrom, start, stop)
