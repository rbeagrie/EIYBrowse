from .base import Track
from ..utils import format_genomic_distance
import numpy as np


class ScaleBarTrack(Track):

    """Track for displaying a scale bar"""

    def __init__(self, color='#000000', fontsize=10,
                 name=None, name_rotate=False):

        super(ScaleBarTrack, self).__init__(name, name_rotate)

        self.color, self.fontsize = color, fontsize

    def get_config(self, region, browser_config):

        return {'rows': 1}

    def get_scale_bar_size(self, region_size):

        digits = int(np.floor(np.log10(abs(region_size))))

        round_number_starting_1 = 10 ** digits
        round_number_starting_5 = 5 * round_number_starting_1

        if round_number_starting_5 < 0.75 * region_size:
            scale_bar_size = round_number_starting_5
        elif round_number_starting_1 < 0.75 * region_size:
            scale_bar_size = round_number_starting_1
        else:
            scale_bar_size = (10 ** (digits - 1)) * 5

        return scale_bar_size

    def get_scale_bar_limits(self, region):

        region_size = region.end - region.start

        scale_bar_size = self.get_scale_bar_size(region_size)

        scale_bar_start = region.start + (region_size * 0.2)

        scale_bar_stop = scale_bar_start + scale_bar_size

        return scale_bar_start, scale_bar_stop

    def _plot(self, ax, region):

        start, stop = self.get_scale_bar_limits(region)

        ax.set_axis_off()

        ax.set_xlim(region.start, region.end)
        ax.set_ylim(0, 1)
        ax.hlines(0.8, start, stop, lw=4)

        label = format_genomic_distance(stop - start, precision=0)

        ax.text(start, 0.1, label)

        return {'patches': None,
                'data': None,
                }
