"""The interval module provides a track for displaying discrete
genomic features, or intervals, such as those you might find in
a bed file.

Whilst the UCSC browser treats genes as a specialized case of
intervals, we have a separate track for genes:
:class:`EIYBrowse.tracks.genes`.
"""

from .base import FileTrack
import itertools


class GenomicIntervalTrack(FileTrack):

    """Track for displaying a discrete signal
    (e.g. a bed file of binding peaks) accross a genomic region"""

    # I'm pretty sure there is no way to reduce these options any
    # further...
    # pylint: disable=too-many-arguments
    def __init__(self, datafile,
                 labels=None, glyphs=None,
                 name=None, name_rotate=False):

        """To create a new genomic interval track:

        :param datafile: Datafile object which will handles access to the
            genomic intervals across a specific region.
        :param labels: If specified, a dictionary of additional arguments
            to pass to :func:`matplotlib.pyplot.text`
        :type labels: dict or None
        :param glyphs: If specified, a dictionary of additional arguments
            to pass to :meth:`matplotlib.axes.AxesSubplot.hlines`
        :type glyphs: dict or None
        :param str name: Optional name label
        :param bool name_rotate: Whether to rotate the name label 90 degrees
        """

        super(GenomicIntervalTrack, self).__init__(datafile,
                                                   name, name_rotate)


        if labels is None:
            labels = {}
        if glyphs is None:
            glyphs = {}

        if 'colors' in glyphs:
            self.colors = itertools.cycle(glyphs['colors'])
            del glyphs['colors']
        else:
            self.colors = None

        if 'jitter' in glyphs:
            self.jitter = glyphs['jitter']
            del glyphs['jitter']
        else:
            self.jitter = 0

        self.labels, self.glyphs = labels, glyphs

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

            vertical_pos = 0.65 + ((i % 2 or -1) * self.jitter)

            if self.colors is not None:
                col = self.colors.next()
                self.labels['color'] = col
                self.glyphs['color'] = col

            patches.append(
                ax.hlines(vertical_pos,
                          interval.start, interval.stop,
                          lw=4, **self.glyphs))

            if interval.name is not '.':
                ax.text(interval.start, 0.2, interval.name,
                        **self.labels)

        return {'patches': patches}
