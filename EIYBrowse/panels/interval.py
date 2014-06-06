from .base import FilePanel

class GenomicIntervalPanel(FilePanel):
    """Panel for displaying a discrete signal (e.g. a bed file of binding peaks) accross a genomic region"""
    def __init__(self, gsignal_path, gsignal_type, **config):
        super(GenomicIntervalPanel, self).__init__(gsignal_path, gsignal_type)
        
        self.config = {'name':None,
                       'color':'#377eb8'}

        self.config.update(config)

        self.name = self.config['name']

    def get_config(self, feature):

        return { 'lines' : 1 }

    def _plot(self, ax, feature):

        ax.set_axis_off()

        ax.set_xlim(feature.start, feature.end)
        ax.set_ylim(0,1)

        patches = []

        for interval in self.datafile.adapter[feature]:

            patches.append(ax.hlines(0.8, interval.start, interval.stop, lw=4))
            if interval.name is not None:
                ax.text(interval.start, 0.2, interval.name)

        return { 'patches' : patches ,
               }

