import matplotlib.pyplot as plt
from .utils import Config

class PlotFrame(object):

    """PlotFrame holds the plotting output of a single panel."""

    def __init__(self, panel, total_lines, frame_lines, line_index):

        """Create a new frame in the current plot.

        :param panel: The :class:`EIYBrowse.panels.Panel` instance
        which will control plotting to this frame.
        :type panel: subclass of :class:`EIYBrowse.panels.Panel`.
        :param total_lines: The total number of horizontal lines
        in the current plot.
        :type total_lines: int.
        :param frame_lines: The number of horizontal lines
        occupied by this frame
        :type frame_lines: int.
        :param line_index: The 0-based index of the first horizontal
        line occupied by this frame.
        :type line_index: int.

        """

        self.label_ax = plt.subplot2grid((total_lines, 10), (line_index, 0),
                                    rowspan=frame_lines,)

        self.data_ax = plt.subplot2grid((total_lines, 10), (line_index, 1),
                                   rowspan=frame_lines, colspan=9)

        self.axes = self.label_ax, self.data_ax

        self.panel = panel
        self.results = None

    def do_plot(self, feature):

        self.results = self.panel.plot(self.axes, feature)

class Plot(object):

    """Class that represents a single plot and it's axes/data"""

    def __init__(self, figwidth, total_lines, lineheight,
                 frames=[]):

        super(Plot, self).__init__()

        self.frames = frames
        self.line_index = 0

        self.total_lines = total_lines
        self.figwidth = figwidth
        self.lineheight = lineheight

        self.figure = self.make_figure()

    def make_figure(self):

        figheight = self.total_lines * self.lineheight

        return plt.figure(figsize=(self.figwidth, figheight))

    def add_frame(self, panel, panel_config):

        new_frame = PlotFrame(panel,
                              self.total_lines, panel_config['lines'],
                              self.line_index)

        self.frames.append(new_frame)
        self.line_index += panel_config['lines']

    def do_plot(self, feature):

        for frame in self.frames:

            frame.do_plot(feature)


class Browser(object):

    """Class that hold plotting panels and controls panel position/style"""

    def __init__(self, panels=[], **config):
        super(Browser, self).__init__()

        self.panels = panels
        self.config = Config({'width': 16,
                              'lineheight': .5})
        self.config.update(config)

    def setup_plot(self, panel_configs):

        total_lines = sum([p['lines'] for p in panel_configs])

        plot = Plot(self.config.width, 
                    total_lines, self.config.lineheight)

        for panel, panel_config in zip(self.panels, panel_configs):

            plot.add_frame(panel, panel_config)

        return plot

    def plot(self, feature):
        """Plot all panels given a feature object for window size"""

        panel_configs = [p.get_config(feature, self.config)
                         for p in self.panels]

        plot = self.setup_plot(panel_configs)

        plot.do_plot(feature)

        return plot
