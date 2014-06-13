from .base import Panel
from ..utils import format_genomic_distance
import numpy as np

class ScaleBarPanel(Panel):
    """Panel for displaying a scale bar"""
    def __init__(self, color='black'):
        super(ScaleBarPanel, self).__init__()

        self.color = color

    def get_config(self, feature, browser_config):

        return { 'lines' : 1 }

    def get_scale_bar_size(self, feature_size):


        digits = int(np.floor(np.log10(abs(feature_size))))

        round_number_starting_1 = 10 ** digits
        round_number_starting_5 = 5 * round_number_starting_1

        if round_number_starting_5 < 0.75 * feature_size:
            scale_bar_size = round_number_starting_5
        elif round_number_starting_1 < 0.75 * feature_size:
            scale_bar_size = round_number_starting_1
        else:
            scale_bar_size = (10 ** (digits - 1)) * 5

        return scale_bar_size


    def get_scale_bar_limits(self, feature):

        feature_size = feature.end - feature.start

        scale_bar_size = self.get_scale_bar_size(feature_size)

        scale_bar_start = feature.start + (feature_size * 0.2)

        scale_bar_stop = scale_bar_start + scale_bar_size

        return scale_bar_start, scale_bar_stop


    def _plot(self, ax, feature):

        start, stop = self.get_scale_bar_limits(feature)

        ax.set_axis_off()

        ax.set_xlim(feature.start, feature.end)
        ax.set_ylim(0,1)
        ax.hlines(0.8, start, stop, lw=4)

        label = format_genomic_distance(stop - start, precision=0)


        ax.text(start, 0.1, label)

        return { 'patches' : None ,
                 'data' : None,
               }
