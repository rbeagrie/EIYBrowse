from .base import Panel
from ..utils import format_genomic_distance
from matplotlib import pyplot as plt

class LocationPanel(Panel):
    """Panel for displaying location information"""
    def __init__(self, color='black'):
        super(LocationPanel, self).__init__()

        self.color = color

    def get_config(self, feature):

        return { 'lines' : 1 }

    def _plot(self, ax, feature):

        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.xaxis.set_ticks_position('top')
        ax.yaxis.set_ticks_position('none')
        plt.setp(ax.get_yticklabels(), visible=False)

        ax.tick_params(direction='in', pad=-15)


        ax.set_xlim(feature.start, feature.end)
        new_labels = [format_genomic_distance(l) for l in ax.xaxis.get_ticklocs()]
        ax.xaxis.set_ticklabels(new_labels)

        return { 'patches' : None ,
                 'data' : None,
               }

    def plot(self, ax, feature):

        self.name = feature.chrom

        super(LocationPanel, self).plot(ax, feature)

