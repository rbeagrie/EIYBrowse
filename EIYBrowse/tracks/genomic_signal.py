from .base import FileTrack
import numpy as np


class GenomicSignalTrack(FileTrack):

    """Track for displaying a continuous signal accross a genomic region"""

    def __init__(self, datafile,
                 bins=800, height=4,
                 color='#377eb8', negative_color=None,
                 ymin=None, ymax=None,
                 name=None, name_rotate=False):

        super(GenomicSignalTrack, self).__init__(datafile,
                                                 name, name_rotate)

        self.bins, self.height = bins, height
        self.color, self.negative_color = color, negative_color
        self.ymin, self.ymax = ymin, ymax

    def get_config(self, region, browser_config):

        return {'rows': self.height}

    def _plot(self, ax, region):

        ax.set_axis_off()

        sig_x, sig_y = self.datafile.local_coverage(
            region, bins=self.bins)

        if self.negative_color is not None:
            pos_y = sig_y.copy()
            pos_y[pos_y <= 0.] = np.NAN

            pos_patches = ax.fill_between(
                sig_x, pos_y, color=self.color)

            neg_y = sig_y.copy()
            neg_y[neg_y >= 0.] = np.NAN

            neg_patches = ax.fill_between(
                sig_x, neg_y, color=self.negative_color)

            patches = [pos_patches, neg_patches]

        else:

            patches = ax.fill_between(sig_x, sig_y, color=self.color)

        ax.set_xlim(region.start, region.stop)
        bottom, top = ax.get_ylim()
        if not self.ymin is None:
            bottom = self.ymin
        if not self.ymax is None:
            top = self.ymax
        ax.set_ylim(bottom, top)

        return {'patches': patches,
                'data': (sig_x, sig_y),
                }
