"""The core module defines classes that set up the plotting space
before the plotting is actually done by the individual panels.

:class:`Plot` handles everything that needs to be done to
visualise a specific genomic region.

:class:`Browser` handles everything that is persistent between
different genomic regions.
"""

import matplotlib.pyplot as plt


def make_frame(panel, total_lines, frame_lines, line_index):
    """Make a new frame to add to the current plot.

    Uses matplotlib's gridspec to create two new subplots. label_ax
    is the subplot which will contain the label for this frame, whilst
    data_ax is the subplot which will contain the genomic data (e.g.
    The ChIP-seq signal). self.panel handles fetching
    the data and plotting it to the data_ax.

    :param panel: The :class:`~EIYBrowse.panels.base.Panel` instance
        which will control plotting to this frame.
    :type panel: Subclass of :class:`~EIYBrowse.panels.base.Panel`.
    :param int total_lines: The total number of horizontal lines in
        the current plot.
    :param int frame_lines: The number of horizontal lines occupied by
        this frame
    :param int line_index: The 0-based index of the first horizontal
        line occupied by this frame.

    :returns: Dictionary containing the panel and the
        newly created plotting axes.
    :rtype: dict

    """

    label_ax = plt.subplot2grid((total_lines, 10), (line_index, 0),
                                rowspan=frame_lines,)

    data_ax = plt.subplot2grid((total_lines, 10), (line_index, 1),
                               rowspan=frame_lines, colspan=9)

    frame_dict = {'panel': panel,
                  'axes': (label_ax, data_ax)}

    return frame_dict


class Plot(object):
    """Plot holds all the panels and frames for one browser query,
    as well as any return values from the plotting event.

    Each time the browser's :meth:`~EIYBrowse.core.Browser.plot`
    method is called, a new Plot object is generated to hold
    references to all of the output."""

    def __init__(self, figwidth, total_lines, lineheight):
        """Create a new plot object:

        :param int figwidth: Width of the plotting figure
        :param int total_lines: Total number of horizontal lines
            required by all the panels.
        :param int lineheight: Height of each horizontal line

        """

        super(Plot, self).__init__()

        self.frames = []
        self.line_index = 0

        self.total_lines = total_lines
        self.figwidth = figwidth
        self.lineheight = lineheight

        self.figure = self._make_figure()

    def _make_figure(self):
        """Create a new Figure instance to plot to."""

        figheight = self.total_lines * self.lineheight

        return plt.figure(figsize=(self.figwidth, figheight))

    def add_frame(self, panel, panel_config):
        """Add a new frame to the current figure.

        :param panel: :class:`~EIYBrowse.panels.base.Panel` instance which
            will handle plotting to the new frame.
        :type panel: Subclass of :class:`~EIYBrowse.panels.base.Panel`
        :param dict panel_config: Dictionary containing configuration
            information for the new frame, including for example it's height.

        """

        new_frame = make_frame(panel,
                               self.total_lines, panel_config['lines'],
                               self.line_index)

        self.frames.append(new_frame)
        self.line_index += panel_config['lines']

    def do_plot(self, interval):
        """Plot the data for all frames over a region specified by interval.

        :param interval: Genomic region to plot data for.
        :type interval: :class:`pybedtools.Interval`

        """

        for frame in self.frames:

            frame['results'] = frame['panel'].plot(frame['axes'], interval)


class Browser(object):
    """Browser stores the plotting panels and controls panel position/style"""

    def __init__(self, panels=None,
                 width=16, lineheight=.5):
        """Create a new EIYBrowse Browser.

        :param list panels: A list of :class:`~EIYBrowse.panels.base.Panel`
            objects to handle the plotting.
        :param float width: Width of the browser window
        :param float lineheight: Height of each horizontal line in the browser.
        """

        super(Browser, self).__init__()

        # If panels param is not None, use that. Else use emtpy list.
        self.panels = panels or []

        self.width, self.lineheight = width, lineheight


    def setup_plot(self, panel_configs):
        """Create a new plotting area.

        Work out the correct dimensions of the plotting area and all
        of its sub-plots, then create a :class:`Plot` object.

        :param dict panel_configs: Dictionary of configuration values
            for all of the panels.

        :returns: :class:`Plot` object ready to
            handle plotting of a specific genomic region.
        :rtype: :class:`Plot`
        """

        total_lines = sum([p['lines'] for p in panel_configs])

        plot = Plot(self.width,
                    total_lines, self.lineheight)

        for panel, panel_config in zip(self.panels, panel_configs):

            plot.add_frame(panel, panel_config)

        return plot

    def plot(self, interval):
        """Plot all panels given a interval object for window size

        :param interval: Genomic region to plot data for.
        :type interval: :class:`pybedtools.Interval`

        """

        panel_configs = [p.get_config(interval, self)
                         for p in self.panels]

        plot = self.setup_plot(panel_configs)

        plot.do_plot(interval)

        return plot
