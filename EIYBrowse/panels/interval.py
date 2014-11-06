from .base import FilePanel


class GenomicIntervalPanel(FilePanel):

    """Panel for displaying a discrete signal 
    (e.g. a bed file of binding peaks) accross a genomic region"""

    def __init__(self, **config):
        super(GenomicIntervalPanel, self).__init__(**config)

        self.config = {'name': None,
                       'color': '#000000',
                       'colors': None,
                       'fontsize': 10,
                       'alternate': False}

        self.config.update(config)

        self.name = self.config['name']

    def get_config(self, feature, browser_config):

        return {'lines': 1}

    def _plot(self, ax, feature):

        ax.set_axis_off()

        ax.set_xlim(feature.start, feature.end)
        ax.set_ylim(0, 1)

        patches = []

        for i, interval in enumerate(self.datafile.adapter[feature]):

            if self.config['alternate']:
                vertical_pos = 0.5 + ((i % 2) * 0.3)
            else:
                vertical_pos = 0.8

            if self.config['colors'] is not None:
                col = self.config['colors'].next()
            else:
                col = self.config['color']

            patches.append(
                ax.hlines(vertical_pos, 
                          interval.start, interval.stop,
                          color=col, lw=4))

            if interval.name is not '.':
                ax.text(interval.start, 0.2, interval.name, 
                        fontsize=self.config['fontsize'],
                        color=col)

        return {'patches': patches,
                }
