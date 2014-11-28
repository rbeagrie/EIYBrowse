"""The core module defines classes that set up the plotting space
before the plotting is actually done by the individual tracks.

:class:`Plot` handles everything that needs to be done to
visualise a specific genomic region.

:class:`Browser` handles everything that is persistent between
different genomic regions.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def make_frame(track, gs, row_index):
    """Make a new frame to add to the current plot.

    Uses matplotlib's gridspec to create two new subplots. label_ax
    is the subplot which will contain the label for this frame, whilst
    data_ax is the subplot which will contain the genomic data (e.g.
    The ChIP-seq signal). self.track handles fetching
    the data and plotting it to the data_ax.

    :param track: The :class:`~EIYBrowse.tracks.base.Track` instance
        which will control plotting to this frame.
    :type track: Subclass of :class:`~EIYBrowse.tracks.base.Track`.
    :param int total_rows: The total number of horizontal rows in
        the current plot.
    :param int frame_rows: The number of horizontal rows occupied by
        this frame
    :param int row_index: The 0-based index of the first horizontal
        row occupied by this frame.

    :returns: Dictionary containing the track and the
        newly created plotting axes.
    :rtype: dict

    """

    fig = plt.gcf()

    label_ax = fig.add_subplot(gs[row_index, 0])

    plot_ax = fig.add_subplot(gs[row_index, 1])


    frame_dict = {'track': track,
                  'plot_ax': plot_ax,
                  'label_ax': label_ax}

    return frame_dict


class Plot(object):
    """Plot holds all the tracks and frames for one browser query,
    as well as any return values from the plotting event.

    Each time the browser's :meth:`~EIYBrowse.core.Browser.plot`
    method is called, a new Plot object is generated to hold
    references to all of the output."""

    def __init__(self, base_gridspec, track_configs):
        """Create a new plot object:

        :param int figwidth: Width of the plotting figure
        :param int total_rows: Total number of horizontal rows
            required by all the tracks.
        :param int rowheight: Height of each horizontal row

        """

        super(Plot, self).__init__()

        self.frames = []
        self.frame_index = 0

        self.track_configs = track_configs
        self.gs = self._make_gridspec(base_gridspec, track_configs)

    def _make_gridspec(self, base_gridspec, track_configs):
        """Create a new Figure instance to plot to."""

        height_ratios = [p['rows'] for p in track_configs]
        no_frames=len(height_ratios)

        return gridspec.GridSpecFromSubplotSpec(no_frames, 2,
                                                height_ratios=height_ratios,
                                                width_ratios=[1,9],
                                                wspace=0.0, hspace=0.0,
                                                subplot_spec=base_gridspec)

    def add_frame(self, track, track_config):
        """Add a new frame to the current figure.

        :param track: :class:`~EIYBrowse.tracks.base.Track` instance which
            will handle plotting to the new frame.
        :type track: Subclass of :class:`~EIYBrowse.tracks.base.Track`
        :param dict track_config: Dictionary containing configuration
            information for the new frame, including for example it's height.

        """

        new_frame = make_frame(track,
                               self.gs,
                               self.frame_index)

        self.frames.append(new_frame)
        self.frame_index += 1

    def do_plot(self, region):
        """Plot the data for all frames over a region specified by region.

        :param region: Genomic region to plot data for.
        :type region: :class:`pybedtools.Interval`

        """

        for frame in self.frames:

            frame['results'] = frame['track'].plot(region,
                                                   frame['plot_ax'],
                                                   frame['label_ax'])


class Browser(object):
    """Browser stores the plotting tracks and controls track position/style"""

    def __init__(self, tracks=None,
                 width=16, rowheight=.5):
        """Create a new EIYBrowse Browser.

        :param list tracks: A list of :class:`~EIYBrowse.tracks.base.Track`
            objects to handle the plotting.
        :param float width: Width of the browser window
        :param float rowheight: Height of each horizontal row in the browser.
        """

        super(Browser, self).__init__()

        # If tracks param is not None, use that. Else use emtpy list.
        self.tracks = tracks or []

        self.width, self.rowheight = width, rowheight


    def _make_base_gridspec(self, track_configs):

        """Make a figure of the appropriate size and add one subplot"""

        total_rows = sum([p['rows'] for p in track_configs])

        figheight = total_rows * self.rowheight

        plt.figure(figsize=(self.width, figheight))

        return gridspec.GridSpec(1, 1, wspace=0.0, hspace=0.0)[0]


    def setup_plot(self, base_gridspec, track_configs):
        """Create a new plotting area.

        Work out the correct dimensions of the plotting area and all
        of its sub-plots, then create a :class:`Plot` object.

        :param dict track_configs: Dictionary of configuration values
            for all of the tracks.

        :returns: :class:`Plot` object ready to
            handle plotting of a specific genomic region.
        :rtype: :class:`Plot`
        """

        plot = Plot(base_gridspec, track_configs)

        for track, track_config in zip(self.tracks, track_configs):

            plot.add_frame(track, track_config)

        return plot

    def plot(self, region):
        """Plot all tracks given a interval object for window size

        :param region: Genomic region to plot data for.
        :type region: :class:`pybedtools.Interval`

        """

        track_configs = [p.get_config(region, self)
                         for p in self.tracks]

        base_gridspec = self._make_base_gridspec(track_configs)

        plot = self.setup_plot(base_gridspec, track_configs)

        plot.do_plot(region)

        return plot

    def plot_to_ax(self, region, base_gridspec):
        """Plot all tracks given a interval object for window size

        :param region: Genomic region to plot data for.
        :type region: :class:`pybedtools.Interval`

        """

        track_configs = [p.get_config(region, self)
                         for p in self.tracks]

        plot = self.setup_plot(base_gridspec, track_configs)

        plot.do_plot(region)

        return plot

