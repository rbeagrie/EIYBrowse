from .base import FilePanel

class GenomicSignalPanel(FilePanel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) accross a genomic region"""
    def __init__(self, gsignal_path, gsignal_type, **config):
        super(GenomicSignalPanel, self).__init__(gsignal_path, gsignal_type)

        self.config = { 'name':None,
                        'bins':800,
                        'color':'#377eb8'}

        self.config.update(**config)

        self.name = self.config['name']
        
    def get_config(self, feature):

        return { 'lines' : 4 }

    def _plot(self, ax, feature):

        ax.set_axis_off()

        sig_x, sig_y = self.datafile.local_coverage(feature, bins=self.config['bins'])
        patches = ax.fill_between(sig_x, sig_y, color=self.config['color'])
        ax.set_xlim(feature.start, feature.stop)

        return { 'patches' : patches ,
                 'data' : (sig_x, sig_y),
               }
