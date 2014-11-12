from .base import FilePanel
import numpy as np


class GenomicSignalPanel(FilePanel):

    """Panel for displaying a continuous signal accross a genomic region"""

    def __init__(self, file_path, file_type,
                 bins=800, height=4,
                 color='#377eb8', negative_color=None,
                 ymin=None, ymax=None,
                 name=None, name_rotate=False):

        super(GenomicSignalPanel, self).__init__(file_path, file_type, name_rotate)

        self.bins, self.height = bins, height
        self.color, self.negative_color = color, negative_color
        self.ymin, self.ymax = ymin, ymax

    def get_config(self, feature, browser_config):

        return {'lines': self.height}

    def _plot(self, ax, feature):

        ax.set_axis_off()

        sig_x, sig_y = self.datafile.local_coverage(
            feature, bins=self.bins)

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

        ax.set_xlim(feature.start, feature.stop)
        bottom, top = ax.get_ylim()
        if not self.ymin is None:
            bottom = self.ymin
        if not self.ymax is None:
            top = self.ymax
        ax.set_ylim(bottom, top)

        return {'patches': patches,
                'data': (sig_x, sig_y),
                }
