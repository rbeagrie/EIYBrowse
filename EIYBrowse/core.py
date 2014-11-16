"""The core module defines classes that set up the plotting space
before the plotting is actually done by the individual panels.

:class:`Plot` handles everything that needs to be done to
visualise a specific genomic region.

:class:`Browser` handles everything that is persistent between
different genomic regions.
"""

import matplotlib.pyplot as plt


def make_frame(panel, total_rows, frame_rows, row_index):
    """Make a new frame to add to the current plot.

    Uses matplotlib's gridspec to create two new subplots. label_ax
    is the subplot which will contain the label for this frame, whilst
    data_ax is the subplot which will contain the genomic data (e.g.
    The ChIP-seq signal). self.panel handles fetching
    the data and plotting it to the data_ax.

    :param panel: The :class:`~EIYBrowse.panels.base.Panel` instance
        which will control plotting to this frame.
    :type panel: Subclass of :class:`~EIYBrowse.panels.base.Panel`.
    :param int total_rows: The total number of horizontal rows in
        the current plot.
    :param int frame_rows: The number of horizontal rows occupied by
        this frame
    :param int row_index: The 0-based index of the first horizontal
        row occupied by this frame.

    :returns: Dictionary containing the panel and the
        newly created plotting axes.
    :rtype: dict

    """

    label_ax = plt.subplot2grid((total_rows, 10), (row_index, 0),
                                rowspan=frame_rows,)

    plot_ax = plt.subplot2grid((total_rows, 10), (row_index, 1),
                               rowspan=frame_rows, colspan=9)

    frame_dict = {'panel': panel,
                  'plot_ax': plot_ax,
                  'label_ax': label_ax}

    return frame_dict


class Plot(object):
    """Plot holds all the panels and frames for one browser query,
    as well as any return values from the plotting event.

    Each time the browser's :meth:`~EIYBrowse.core.Browser.plot`
    method is called, a new Plot object is generated to hold
    references to all of the output."""

    def __init__(self, figwidth, total_rows, rowheight):
        """Create a new plot object:

        :param int figwidth: Width of the plotting figure
        :param int total_rows: Total number of horizontal rows
            required by all the panels.
        :param int rowheight: Height of each horizontal row

        """

        super(Plot, self).__init__()

        self.frames = []
        self.row_index = 0

        self.total_rows = total_rows
        self.figwidth = figwidth
        self.rowheight = rowheight

        self.figure = self._make_figure()

    def _make_figure(self):
        """Create a new Figure instance to plot to."""

        figheight = self.total_rows * self.rowheight

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
                               self.total_rows, panel_config['rows'],
                               self.row_index)

        self.frames.append(new_frame)
        self.row_index += panel_config['rows']

    def do_plot(self, region):
        """Plot the data for all frames over a region specified by region.

        :param region: Genomic region to plot data for.
        :type region: :class:`pybedtools.Interval`

        """

        for frame in self.frames:

            frame['results'] = frame['panel'].plot(region,
                                                   frame['plot_ax'],
                                                   frame['label_ax'])


class Browser(object):
    """Browser stores the plotting panels and controls panel position/style"""

    def __init__(self, panels=None,
                 width=16, rowheight=.5):
        """Create a new EIYBrowse Browser.

        :param list panels: A list of :class:`~EIYBrowse.panels.base.Panel`
            objects to handle the plotting.
        :param float width: Width of the browser window
        :param float rowheight: Height of each horizontal row in the browser.
        """

        super(Browser, self).__init__()

        # If panels param is not None, use that. Else use emtpy list.
        self.panels = panels or []

        self.width, self.rowheight = width, rowheight


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

        total_rows = sum([p['rows'] for p in panel_configs])

        plot = Plot(self.width,
                    total_rows, self.rowheight)

        for panel, panel_config in zip(self.panels, panel_configs):

            plot.add_frame(panel, panel_config)

        return plot

    def plot(self, region):
        """Plot all panels given a interval object for window size

        :param region: Genomic region to plot data for.
        :type region: :class:`pybedtools.Interval`

        """

        panel_configs = [p.get_config(region, self)
                         for p in self.panels]

        plot = self.setup_plot(panel_configs)

        plot.do_plot(region)

        return plot
