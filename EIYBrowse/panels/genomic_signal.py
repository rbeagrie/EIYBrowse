from .base import FilePanel
import numpy as np

class GenomicSignalPanel(FilePanel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) accross a genomic region"""
    def __init__(self, gsignal_path, gsignal_type, **config):
        super(GenomicSignalPanel, self).__init__(gsignal_path, gsignal_type)

        self.config = { 'name':None,
                        'bins':800,
                        'color':'#377eb8',
                        'height':4,
                        'top':10,
                        'bottom':0,
                        'negative_color':None}

        self.config.update(**config)

        self.name = self.config['name']
        
    def get_config(self, feature, browser_config):

        return { 'lines' : self.config['height'] }

    def _plot(self, ax, feature):

        ax.set_axis_off()

        sig_x, sig_y = self.datafile.local_coverage(feature, bins=self.config['bins'])
        
        if self.config['negative_color'] is not None:
            pos_y = sig_y.copy()
            pos_y[pos_y <= 0.] = np.NAN

            pos_patches = ax.fill_between(sig_x, pos_y, color=self.config['color'])

            neg_y = sig_y.copy()
            neg_y[neg_y >= 0.] = np.NAN

            neg_patches = ax.fill_between(sig_x, neg_y, color=self.config['negative_color'])

            patches = [pos_patches, neg_patches]

        else:

            patches = ax.fill_between(sig_x, sig_y, color=self.config['color'])

        ax.set_xlim(feature.start, feature.stop)
        ax.set_ylim(self.config['bottom'], self.config['top'])

        return { 'patches' : patches ,
                 'data' : (sig_x, sig_y),
               }
