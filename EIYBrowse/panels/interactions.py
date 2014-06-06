from .base import FilePanel
from PIL import Image
import numpy as np

class InteractionsPanel(FilePanel):
    """Base panel for displaying 3D interactions data (e.g. Hi-C) across a genomic region"""
    def __init__(self, file_path, file_type, **config):
        super(InteractionsPanel, self).__init__(file_path, file_type)

        self.config = {'flip':False,
                       'log':False}

        self.config.update(config)
        
    def get_config(self, feature):

        return { 'lines' : 16 }

    def remove_diagonal(self, inArray):
        "Puts diag in the offset's diagonal of inArray"

        N = inArray.shape[0]
        assert inArray.shape[1] == N
        inArray.flat[0:N**2:N + 1] = np.NAN

    def clip_for_plotting(self, array, percentile=1.):

        clip_lower = np.percentile(array[np.isfinite(array)], percentile)
        clip_upper = np.percentile(array[np.isfinite(array)], (100. - percentile))
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
    
    def _plot(self, ax, feature, flip=False):
        
        ax.axis('off')

        data, new_feature = self.datafile.interactions(feature)

        self.remove_diagonal(data)

        data = self.clip_for_plotting(data)
        
        rotated = self.rotate_to_fit_ax(ax, data, self.config['flip'])
        
        if self.config['log']:
            rotated = np.log10(rotated)
        
        img = ax.imshow(rotated, interpolation='none')
        
        return new_feature

