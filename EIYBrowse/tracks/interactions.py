"""The tracks.interactions module contains a panel for displaying heatmaps
of interactions data. This is best for dense interaction data, where many
loci are measured against many loci e.g. 5C or Hi-C data.
"""

from .base import FileTrack
from PIL import Image
import numpy as np
from math import ceil
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize, LogNorm, SymLogNorm, BoundaryNorm


def rotate_heatmap(data, flip=False):

    """Rotate a symmetrical matrix 45 degrees and move diagonal to the x-axis

    After this transformation, the heatmap will appear as a triangle, with
    genomic location on the x-axis only.

    These heatmaps can be easier to line up with other genomic data
    (e.g. gene positions or ChIP-seq peaks).

    :param data: Input array heatmap
    :type data: :class:`~numpy.array`
    :param bool flip: Whether the triangle should point downwards from the
        axis (default is upwards).
    """

    # The width will be equal to the diagonal of the rotated square

    # Make a PIL image from a copy of the array (due to a PIL 2to3 bug)
    # When we rotate, the new background will be at 0.0 - add 100 to
    # everything so that we can distinguish bins that were 0 to start
    # with.
    _image = Image.fromarray(data.copy() + 100)

    # Resize the data so that the diagonal = width
    _image = _image.resize((800, 800))

    # Rotate the data and expand to fit the new diagonal
    rot = _image.rotate(45, expand=True)

    new_width = rot.size[0]

    # Crop the bottom half of the triangle
    rot = rot.crop((0, 0, new_width, new_width / 2))

    if flip:
        rot = rot.transpose(Image.FLIP_TOP_BOTTOM)

    rot = np.array(rot)

    # Any 0's are actually the image background, so set them to NAN
    rot[rot == 0.] = np.NAN

    # Now take off the 100 we added before:
    rot -= 100.

    return rot


def colormap_from_config_dict(name='jet',
                              over_color=None, under_color=None):

    cmap = get_cmap(name)

    return cmap


normalizers = {'linear': Normalize,
               'log': LogNorm,
               'symmetric_log': SymLogNorm,
               'boundary': BoundaryNorm}

try:
    from matplotlib.colors import PowerNorm
    normalizers['power_law'] = PowerNorm
except ImportError:
    pass

def get_quantile_scaled_normalizer(norm_class, quantile):

    qmin, qmax = sorted([quantile, 100. - quantile])

    class QuantileScaled(norm_class):

        def autoscale_None(self, A):
            ' autoscale only None-valued vmin or vmax'

            if np.size(A) > 0:
                self.vmin = np.percentile(A[np.isfinite(A)], qmin)

            if np.size(A) > 0:
                self.vmax = np.percentile(A[np.isfinite(A)], qmax)

            super(QuantileScaled, self).autoscale_None(A)

    return QuantileScaled


def normalizer_from_config_dict(method='linear', quantile_scaled=None,
                                **norm_args):

    norm_class = normalizers[method]

    if not quantile_scaled is None:
        norm_class = get_quantile_scaled_normalizer(norm_class, quantile_scaled)

    norm = norm_class(**norm_args)

    return norm


class SquareInteractionsTrack(FileTrack):

    """Track for displaying 3D interactions data
    (e.g. Hi-C) across a genomic region as a square matrix"""

    def __init__(self, datafile,
                 name=None, name_rotate=False,
                 **imshow_kwargs):

        """Create a new interactions track

        :param datafile: Object providing access to the interactions data
        :param normalizer: Normalizer to scale the matrix data between 0 and 1
        :type normalizer: :class:`matplotlib.colors.Normalize`
        :param cmap: Colormap to convert matrix values into colors
        :type cmap: :class:`matplotlib.colors.`Colormap`
        :param imshow_kwargs: Optional keyword arguments to be passed to
            :func:`matplotlib.pylab.imshow`
        :param str name: Optional name label
        :param bool name_rotate: Whether to rotate the name label 90 degrees
        """

        super(SquareInteractionsTrack, self).__init__(datafile,
                                                      name, name_rotate)

        self.imshow_kwargs = imshow_kwargs


    def get_config(self, region, browser):

        """Calculate how many rows of height need to be requested.
        Since we will return a square matrix, we need to be the same height
        as our width.
        """

        width_in_rows = browser.width / browser.rowheight
        needed_rows = width_in_rows

        return {'rows': int(ceil(needed_rows))}

    def _plot(self, plot_ax, region):

        """Handle plotting of the matrix to the plotting axis.

        First get the interactions matrix from the datafile by calling the
        interactions method with the region, then mask the matrix diagonal
        and pass the masked matrix to :meth:`_plot_matrix`.
        """

        data, new_region = self.datafile.interactions(region)

        np.fill_diagonal(data, np.NaN)

        return self._plot_matrix(plot_ax, data)

    def _plot_matrix(self, plot_ax, data):

        """Hide the axes ticklabels and display the interaction matrix
        using :func:`~matplotlib.pyplot.imshow`
        """

        plot_ax.axis('off')

        plot_ax.imshow(data, interpolation='none', **self.imshow_kwargs)

    @classmethod
    def from_config_dict(cls, cmap=None, norm=None,
                         **kwargs):

        """Before calling parent's
        :meth:`~EIYBrowse.tracks.base.FileTrack.from_config_dict` method,
        check whether cmap or norm are parameters are dictionaries. If they
        are, handle them separately to create the appropriate objects to pass
        (eventually) to imshow.

        :param dict cmap: Dictionary of options which will be expanded and
            passed to :func:`colormap_from_config_dict` to create an object
            of type :class:`~matplotlib.colors.Colormap`
        :param dict norm: Dictionary of options which will be expanded and
            passed to :func:`normalizer_from_config_dict` to create an object
            of type :class:`~matplotlib.colors.Normalize`
        """

        if type(cmap) is dict:
            cmap = colormap_from_config_dict(**cmap)

        if not norm is None:
            if type(norm) is str:
                norm = normalizer_from_config_dict(method=norm)
            else:
                norm = normalizer_from_config_dict(**norm)

        kwargs['cmap'] = cmap
        kwargs['norm'] = norm

        return super(SquareInteractionsTrack, cls).from_config_dict(**kwargs)


class TriangularInteractionsTrack(SquareInteractionsTrack):

    """Track for displaying 3D interactions data
    (e.g. Hi-C) across a genomic region as a triangular matrix -
    i.e. by rotating the matrix by 45 degrees and moving the diagonal of the
    matrix to the x-axis.
    """

    def __init__(self, datafile,
                 name=None, name_rotate=False,
                 flip=False,
                 **imshow_kwargs):

        """Create a new interactions track

        :param datafile: Object providing access to the interactions data
        :param normalizer: Normalizer to scale the matrix data between 0 and 1
        :type normalizer: :class:`matplotlib.colors.Normalize`
        :param cmap: Colormap to convert matrix values into colors
        :type cmap: :class:`matplotlib.colors.`Colormap`
        :param imshow_kwargs: Optional keyword arguments to be passed to
            :func:`matplotlib.pylab.imshow`
        :param str name: Optional name label
        :param bool name_rotate: Whether to rotate the name label 90 degrees
        :param bool flip: Whether the matrix should extend downwards from the x
            axis (default is upwards from the axis).
        """

        super(TriangularInteractionsTrack,
              self).__init__(datafile,
                             name, name_rotate,
                             **imshow_kwargs)

        self.flip = flip

    def get_config(self, region, browser):

        """Calculate how many rows of height need to be requested.
        Since we will return a triangular matrix, we need to be half as high
        as our width.
        """

        width_in_rows = browser.width / browser.rowheight
        needed_rows = width_in_rows / 2.

        return {'rows': int(ceil(needed_rows))}

    def _plot_matrix(self, plot_ax, data):

        """Rotate the data (and flip if required), then pass it to parent's
        :meth:`~SquareInteractionsTrack._plot_matrix` method.
        """

        rotated_data = rotate_heatmap(data, self.flip)

        return super(TriangularInteractionsTrack,
                     self)._plot_matrix(plot_ax, rotated_data)
