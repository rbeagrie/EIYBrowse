from .base import FilePanel


class GenomicIntervalPanel(FilePanel):

    """Panel for displaying a discrete signal 
    (e.g. a bed file of binding peaks) accross a genomic region"""

    def __init__(self, file_path, file_type,
                 color='#000000', colors=None, fontsize=10,
                 jitter=0.0,
                 name=None, name_rotate=False):

        super(GenomicIntervalPanel, self).__init__(file_path, file_type, name_rotate)

        self.color, self.colors, self.fontsize = color, colors, fontsize
        self.jitter = jitter

    def get_config(self, feature, browser_config):

        return {'lines': 1}

    def _plot(self, ax, feature):

        ax.set_axis_off()

        ax.set_xlim(feature.start, feature.end)
        ax.set_ylim(0, 1)

        patches = []

        for i, interval in enumerate(self.datafile.adapter[feature]):

            vertical_pos = 0.8 + ((i % 2 or -1) * self.jitter)

            if self.colors is not None:
                col = self.colors.next()
            else:
                col = self.color

            patches.append(
                ax.hlines(vertical_pos, 
                          interval.start, interval.stop,
                          color=col, lw=4))

            if interval.name is not '.':
                ax.text(interval.start, 0.2, interval.name, 
                        fontsize=self.fontsize,
                        color=col)

        return {'patches': patches,
                }
