"""The interval module provides a track for displaying discrete
genomic features, or intervals, such as those you might find in
a bed file.

Whilst the UCSC browser treats genes as a specialized case of
intervals, we have a separate track for genes:
:class:`EIYBrowse.tracks.genes`.
"""

from .base import FileTrack


class GenomicIntervalTrack(FileTrack):

    """Track for displaying a discrete signal 
    (e.g. a bed file of binding peaks) accross a genomic region"""

    def __init__(self, datafile,
                 color='#000000', jitter=0.0,
                 text_kwargs=None, icon_kwargs=None,
                 name=None, name_rotate=False):

        """To create a new genomic interval track:

        :param datafile: Datafile object which will handles access to the
            genomic intervals across a specific region.
        :param color: Either a string or a list of strings specifying a color
            for the text and the interval bars.
        :param float jitter: Sequential items on the same row will be
            offset by this amount on the y-axis. This can help to distinguish
            many closely spaced intervals
        :param text_kwargs: If specified, a dictionary of additional arguments
            to pass to :func:`matplotlib.pyplot.text`
        :type text_kwargs: dict or None
        :param icon_kwargs: If specified, a dictionary of additional arguments
            to pass to :meth:`matplotlib.axes.AxesSubplot.hlines`
        :type icon_kwargs: dict or None
        :param str name: Optional name label
        :param bool name_rotate: Whether to rotate the name label 90 degrees
        """

        super(GenomicIntervalTrack, self).__init__(datafile,
                                                   name, name_rotate)

        self.jitter = jitter

        if text_kwargs is None: text_kwargs = {}
        if icon_kwargs is None: icon_kwargs = {}

        self.text_kwargs, self.icon_kwargs = text_kwargs, icon_kwargs

    def get_config(self, region, browser):

        """Calculate how many rows of height need to be requested.

        :param region: Genomic region to plot
        :type region: :class:`pybedtools.Interval`
        :param browser: Browser object calling get_config function
        :type browser: :class:`~EIYBrowse.core.Browser`
        """

        #TODO: At the moment we only request one row. The logic that guides
        # arrangement of genes in the genes track should be refactored so
        # that it can be used to arrange genomic intervals here.

        return {'rows': 1}

    def _plot(self, ax, region):

        """Handle plotting to the specified plotting axis. Get all the 
        intervals that overlap the requested region, then plot them.
        """

        ax.set_axis_off()

        ax.set_xlim(region.start, region.end)
        ax.set_ylim(0, 1)

        patches = []

        for i, interval in enumerate(self.datafile.adapter[region]):

            vertical_pos = 0.8 + ((i % 2 or -1) * self.jitter)

            if self.colors is not None:
                col = self.colors.next()
            else:
                col = self.color

            patches.append(
                ax.hlines(vertical_pos, 
                          interval.start, interval.stop,
                          color=col, lw=4))

            if interval.name is not '.':
                ax.text(interval.start, 0.2, interval.name, 
                        fontsize=self.fontsize,
                        color=col)

        return {'patches': patches,
                }
