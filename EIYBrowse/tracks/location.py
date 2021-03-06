"""The location module contains the LocationTrack class,
which defines a track for showing an axis with genomic
position in basepair co-ordinates.
"""

from .base import Track
from ..utils import format_genomic_distance
from matplotlib import pyplot as plt


class LocationTrack(Track):

    """Track for displaying location in genomic co-ordinates."""

    def __init__(self, color='#000000', fontsize=10,
                 name_rotate=False):

        super(LocationTrack, self).__init__(name_rotate=name_rotate)

        self.color, self.fontsize = color, fontsize
        self.name = None

    def get_config(self, region, browser):

        return {'rows': 1}

    def _plot(self, ax, region):

        """Private method to actually do the plotting."""

        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.xaxis.set_ticks_position('top')
        ax.yaxis.set_ticks_position('none')
        plt.setp(ax.get_yticklabels(), visible=False)

        ax.tick_params(direction='in', pad=-15)

        ax.set_xlim(region.start, region.end)
        tick_locations = ax.xaxis.get_ticklocs()
        precision = 0
        while True:
            new_labels = [
                format_genomic_distance(l, precision) for l in tick_locations]
            if len(set(new_labels)) != len(tick_locations):
                precision += 1
            else:
                break

        ax.xaxis.set_ticklabels(new_labels)
        ax.tick_params(labelsize=self.fontsize)

        for label in ax.get_xticklabels():
            label.set_horizontalalignment('left')

        return {'patches': None,
                'data': None}

    def plot(self, region, plot_ax, label_ax=None):

        """Public method that sets the name of the track to the chromosome
        and calls the parent classes plot method (which in turn calls
        the private _plot function"""

        self.name = region.chrom

        super(LocationTrack, self).plot(region, plot_ax, label_ax)
