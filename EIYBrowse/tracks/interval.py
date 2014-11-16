from .base import FileTrack


class GenomicIntervalTrack(FileTrack):

    """Track for displaying a discrete signal 
    (e.g. a bed file of binding peaks) accross a genomic region"""

    def __init__(self, datafile,
                 color='#000000', colors=None, fontsize=10,
                 jitter=0.0,
                 name=None, name_rotate=False):

        super(GenomicIntervalTrack, self).__init__(datafile,
                                                   name, name_rotate)

        self.color, self.colors, self.fontsize = color, colors, fontsize
        self.jitter = jitter

    def get_config(self, region, browser_config):

        return {'rows': 1}

    def _plot(self, ax, region):

        ax.set_axis_off()

        ax.set_xlim(region.start, region.end)
        ax.set_ylim(0, 1)

        patches = []

        for i, interval in enumerate(self.datafile.adapter[region]):

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
