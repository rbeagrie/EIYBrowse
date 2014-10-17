from .base import Panel
from ..utils import format_genomic_distance, Config
from matplotlib import pyplot as plt

class LocationPanel(Panel):
    """Panel for displaying location information"""
    def __init__(self, **config):
        super(LocationPanel, self).__init__()

        self.config = Config({ 'color' : 'black',
                        'fontsize': 10})
        self.config.update(config)

    def get_config(self, feature, browser_config):

        return { 'lines' : 1,
                  }

    def _plot(self, ax, feature):

        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.xaxis.set_ticks_position('top')
        ax.yaxis.set_ticks_position('none')
        plt.setp(ax.get_yticklabels(), visible=False)

        ax.tick_params(direction='in', pad=-15)


        ax.set_xlim(feature.start, feature.end)
        tick_locations = ax.xaxis.get_ticklocs()
        precision = 0
        while True:
            new_labels = [format_genomic_distance(l, precision) for l in tick_locations]
            if len(set(new_labels)) != len(tick_locations):
                precision += 1
            else:
                break

        ax.xaxis.set_ticklabels(new_labels)
        ax.tick_params(labelsize=self.config['fontsize'])

        return { 'patches' : None ,
                 'data' : None,
               }

    def plot(self, ax, feature):

        self.name = feature.chrom

        super(LocationPanel, self).plot(ax, feature)

