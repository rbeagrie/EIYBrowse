from .base import FilePanel
from PIL import Image
import numpy as np
from ..utils import Config

class InteractionsPanel(FilePanel):
    """Base panel for displaying 3D interactions data (e.g. Hi-C) across a genomic region"""
    def __init__(self, file_path, file_type, **config):
        super(InteractionsPanel, self).__init__(file_path, file_type)

        self.config = Config({'flip':False,
                       'log':False,
                       'rotate':True,
                       'name':None,
                       'cmap':'jet',
                       'clip_hard_low':None,
                       'clip':1.,
                       'vmin':None,
                       'vmax':None})

        self.config.update(config)

        self.name = self.config['name']
        
    def get_config(self, feature, browser_config):

        lines_wide = browser_config['width'] / browser_config['lineheight']
        if self.config['rotate']:
            needed_lines = lines_wide / 2.
        else:
            needed_lines = lines_wide

        return { 'lines' : int(needed_lines) }

    def remove_diagonal(self, inArray):
        "Puts diag in the offset's diagonal of inArray"

        N = inArray.shape[0]
        assert inArray.shape[1] == N
        inArray.flat[0:N**2:N + 1] = np.NAN

    def clip_for_plotting(self, array, percentile=1.):

        clip_lower = np.percentile(array[np.isfinite(array)], percentile)
        clip_upper = np.percentile(array[np.isfinite(array)], (100. - percentile))
        if not self.config['clip_hard_low'] is None:
            array[array < self.config['clip_hard_low']] = np.NAN
        return np.clip(array, clip_lower, clip_upper)
    
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
    
    def _plot(self, ax, feature):

        data, new_feature = self.datafile.interactions(feature)

        self.plot_matrix(ax, data)
        
        return new_feature

    def plot_matrix(self, ax, data):

        ax.axis('off')

        self.remove_diagonal(data)

        if self.config.clip:
            data = self.clip_for_plotting(data, self.config.clip)
        
        if self.config['rotate']:
            rotated = self.rotate_to_fit_ax(ax, data, self.config['flip'])
        else:
            rotated = data
        
        if self.config['log']:
            rotated = np.log10(rotated)
        
        img = ax.imshow(rotated, interpolation='none',
                        cmap=self.config['cmap'],
                        vmin=self.config['vmin'],
                        vmax=self.config['vmax'])
