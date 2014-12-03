"""The genes module defines a track for plotting the position of genes"""

from .base import FileTrack
import matplotlib.pyplot as plt


def get_start_stop_on_axes(axes, interval):

    """Given a set of axes and a genomic interval, return
    the start and stop of the interval in axes co-ordinates

    :param plot_ax: Axes to plot the gene name label on
    :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
    :param interval: Genomic interval for which to determine the extent
        in axis co-ordinates
    :type interval: :class:`pybedtools.Interval`
    :returns: interval start and stop in axes co-ordinates (pair of floats)
    """

    xstart, xstop = axes.get_xlim()
    xspan = xstop - xstart

    if interval.start <= xstart:
        iv_start = 0.0
    else:
        dist_from_start = interval.start - xstart
        iv_start = dist_from_start / xspan
    if interval.stop >= xstop:
        iv_stop = 1.0
    else:
        dist_from_end = xstop - interval.stop
        iv_stop = 1.0 - (dist_from_end / xspan)

    return iv_start, iv_stop


class GeneTrack(FileTrack):

    """Track for displaying the position of genes and their introns/exons.

    The genes track needs to have enough vertical space to display all
    of the genes over the requested region. Therefore, the list of genes
    and their positions must be retrieved *before* the figure axes are
    set up. The track therefore makes use of the :meth:`get_config`
    method, which is always called before the plot is initiated.

    Once the list of genes is retrieved, we need to decide how to arrange
    them without them overlapping. The most difficult part of this
    is ensuring that the name labels don't overlap.
    """

    def __init__(self, datafile,
                 color='#377eb8',
                 name=None, name_rotate=False,
                 **kwargs):

        """To create a new gene track:

        :param datafile: Object providing access to the names and locations
            of genes. At the moment only
            :class:`~EIYBrowse.filetypes.gffutils_db.GffutilsDb` objects are
            supported.
        :param str color: Color specifier for the gene icons
        :param str name: Optional name label
        :param bool name_rotate: Whether to rotate the name label 90 degrees
        """

        super(GeneTrack, self).__init__(datafile,
                                        name, name_rotate)

        self.color, self.kwargs = color, kwargs

        self.gene_rows = GeneRows()

    def get_config(self, region, browser):

        """Calculate the number of vertial rows needed in the axis that will
        be assigned to this track.

        Genes are retrieved from the backend by calling the
        :meth:`EIYBrowse.filetypes.gffutils_db.GffutilsDb.get_genes` method of
        the backend. The private :meth:`_get_gene_extents` method then iterates
        over the found genes and returns the start/stop of the gene when
        plotted (including the name label). Each gene is added to
        self.gene_rows, which is a :class:`GeneRows` object that assigns each
        gene to a vertical row, making sure that none of them overlap.

        Once all the rows are added, we return the total number of rows needed
        to arrange the genes without overlaps by calling :meth:`total_rows`.

        :param region: Genomic interval to
            plot genes over.
        :type region: :class:`pybedtools.Interval`
        :param browser: Parent browser
            object that will create the new plotting axis.
        :type browser: :class:`~EIYBrowse.core.Browser`
        """

        self.gene_rows.rows = []

        genes = self.datafile.get_genes(region)

        # TODO: Here we use the browser's width to determine overlaps, but
        # if we were passed a gridspec to plot to then the browser's width
        # is irrelevant.
        for gene, start, stop in self._get_gene_extents(region, genes, browser):

            self.gene_rows.add_gene(gene, start, stop)

        return {'rows': self.total_rows()}

    def total_rows(self):

        """The number of rows needed to plot the current set of genes.

        If there is no current set of genes, just return 1 (as we can't
        take up 0 vertical space).
        """

        return len(self.gene_rows.rows) or 1

    def _get_gene_extents(self, region, genes, browser):

        """Private method that iterates over genes and calculates the
        axis space that they will need to occupy, including their name label.

        At the moment, this calls :meth:`_get_gene_extent` and actually plots
        the gene, then queries the space used. This is of course highly
        inefficient as we have to plot every gene twice (once to figure out
        how big it is, and then again once we have assigned it to the correct
        vertical line) and should be replaced with something a bit more clever
        ASAP.
        """

        old_figure = plt.gcf()
        _figure = plt.figure(figsize=(browser.width, 1))
        _plot_axis = _figure.add_subplot(111)
        _plot_axis.set_xlim(region.start, region.stop)
        _renderer = _figure.canvas.get_renderer()

        for gene in genes:

            start, stop = self._get_gene_extent(gene, _plot_axis, _renderer)
            yield gene, start, stop

        plt.close(_figure)
        plt.figure(old_figure.number)

    def _get_gene_extent(self, gene, _plot_axis, _renderer):

        """Plot the gene to _plot_axis, then ask _renderer how big the gene is.
        """

        gene_line, gene_label = self.plot_gene_dict(_plot_axis, gene,
                                                    plot_exons=False)

        line_bounds = gene_line.get_window_extent(_renderer)
        label_bounds = gene_label.get_window_extent(_renderer)

        start = line_bounds.x0
        stop = max([line_bounds.x1, label_bounds.x1])
        stop = stop * 1.1

        return start, stop

    def plot_name(self, plot_ax, start, name, row_index=0):

        """Plot the name label of the gene.

        :param plot_ax: Axes to plot the gene name label on
        :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
        :param float start: Start position of the gene in axis co-ordinates
        :param str name: Name of the gene to be plotted
        :param float row_index: Vertical position of the row which the gene
            is to be plotted to.
        """

        span = 1. / self.total_rows()

        return plot_ax.text(start, row_index - span, name, **self.kwargs)

    def plot_gene_body(self, plot_ax, gene, row_index=0):

        """Plot the body of the gene to the plotting axes.

        First we get the extent of the gene in axis co-ordinates.

        We then determine the vertial position of the gene . First the vertial
        span of each row is calculated by dividing the extent of the whole
        axis (which is always 1) by the total number of rows. The position of
        the current gene is then given by the top position of the current row
        (given by row_index) minus two fifths of the row span.

        :param plot_ax: Axes to plot the gene name label on
        :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
        :param gene: Gene object to be plotted
        :type gene: :class:`pybedtools.Interval`
        :param float row_index: Vertical position of the row which the gene
            is to be plotted to.
        """

        start, stop = get_start_stop_on_axes(plot_ax, gene)

        span = 1. / self.total_rows()

        gene_height = row_index - 2 * span / 5.

        line_patch = plot_ax.axhline(
            gene_height, start, stop, linewidth=1, color='r')

        return line_patch

    def plot_exon(self, plot_ax, exon, row_index=0):

        """Plot the exon to the plotting axes.

        First we get the extent of the exon in axis co-ordinates.

        We then determine the vertial position of the exon . First the vertial
        span of each row is calculated by dividing the extent of the whole
        axis (which is always 1) by the total number of rows. The top of
        the current exon is then given by the top position of the current row
        (row_index) minus one fifth of the row span, and the bottom
        is given by the row_index minus three fifths of the row span.

        :param plot_ax: Axes to plot the gene name label on
        :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
        :param exon: Exon object to be plotted
        :type exon: :class:`pybedtools.Interval`
        :param float row_index: Vertical position of the row which the gene
            is to be plotted to.
        """

        start, stop = get_start_stop_on_axes(plot_ax, exon)

        span = 1. / self.total_rows()

        exon_top = row_index - (span / 5.)
        exon_bottom = row_index - (3 * span / 5.)

        plot_ax.axhspan(exon_top, exon_bottom,
                        start, stop,
                        color='r')

    def plot_gene_dict(self, plot_ax, gene_dict, row_index=0,
                       plot_exons=True):

        """Plot the gene dictionary to the plotting axes.

        The 'gene' key of gene_dict should contain a
        :class:`pybedtools.Interval` representing the entire gene, which is
        passed to :meth:`plot_gene_body`.

        The 'exons' key should contain a list of :class:`pybedtools.Interval`
        objects representing each individual exon of the gene's longest
        isoform, which are passed to :meth:`plot_exon` if plot_exons is True.

        Finally, the name label of the gene is plotted by :meth:`plot_name`.

        :param plot_ax: Axes to plot the gene name label on
        :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
        :param dict gene_dict: Dictionary containing the details of the gene
            to be plotted
        :param float row_index: Vertical position of the row on which the gene
            is to be plotted
        :param bool plot_exons: Whether to plot the exons
        """

        gene = gene_dict['gene']
        gene_body_patch = self.plot_gene_body(plot_ax, gene, row_index)

        if plot_exons:
            for exon in gene_dict['exons']:

                self.plot_exon(plot_ax, exon, row_index)

        name_label_patch = self.plot_name(
            plot_ax, gene.start, gene.attributes['Name'][0], row_index)

        return gene_body_patch, name_label_patch

    def _plot(self, plot_ax, region):

        """Private method which plots all the genes over the specified
        interval.
        """

        plot_ax.axis('off')
        plot_ax.set_xlim(region.start, region.stop)
        plot_ax.set_ylim(0, 1)

        for i, gene_row in enumerate(self.gene_rows.rows):

            for gene_dict in gene_row['genes']:

                row_index = 1.0 - (i * (1.0 / self.total_rows()))

                self.plot_gene_dict(plot_ax, gene_dict, row_index)


class GeneRows(object):

    """Class for assigning genes to vertical rows without overlapping."""

    def __init__(self):

        """Create a new GeneRows object"""

        self.rows = []

    def add_gene(self, gene, start, stop):

        """Add a gene to the internal store.

        Calls the :meth:`get_gene_row` method to return the row we should
        add the gene to such that it doesn't overlap with any already
        added genes. Then adds the gene to the returned row and updates
        the 'stop' key to reflect the new rightmost position in the row.

        :param gene: Gene object to be plotted
        :type gene: :class:`pybedtools.Interval`
        :param float start: Start position of the gene in axis co-ordinates
        :param float stop: Stop position of the gene in axis co-ordinates
        """

        row = self.get_gene_row(start)
        row['genes'].append(gene)
        row['stop'] = stop

    def get_gene_row(self, start):

        """Go through all of the existing rows and return the first row where
        the start position of the new gene would not overlap the stop position
        of any existing genes in that row.

        If no existing row is found, make a new empty row and return that.

        :param float start: Start position of the gene in axis co-ordinates
        """

        for row in self.rows:
            if start > row['stop']:
                return row

        new_row = {'genes': [],
                   'stop': 0}
        self.rows.append(new_row)

        return new_row
