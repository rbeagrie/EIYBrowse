"""The tracks.interactions module contains a panel for displaying heatmaps
of interactions data. This is best for dense interaction data, where many
loci are measured against many loci e.g. 5C or Hi-C data.
"""

from .base import FileTrack
from PIL import Image
import numpy as np


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


class InteractionsTrack(FileTrack):

    """Base track for displaying 3D interactions data 
    (e.g. Hi-C) across a genomic region"""

    def __init__(self, datafile,
                 flip=False, log=False, rotate=True,
                 clip=1., clip_hard=None,
                 name=None, name_rotate=False,
                 **kwargs):

        super(InteractionsTrack, self).__init__(datafile,
                                                name, name_rotate)

        self.flip, self.log, self.rotate = flip, log, rotate
        self.clip, self.clip_hard = clip, clip_hard
        self.kwargs = kwargs


    def get_config(self, region, browser):

        rows_wide = browser.width / browser.rowheight
        if self.rotate:
            needed_rows = rows_wide / 2.
        else:
            needed_rows = rows_wide

        return {'rows': int(needed_rows)}

    def clip_for_plotting(self, array, percentile=1.):

        clip_lower = np.percentile(array[np.isfinite(array)], percentile)
        clip_upper = np.percentile(
            array[np.isfinite(array)], (100. - percentile))
        if not self.clip_hard is None:
            array[array < self.clip_hard] = np.NAN
        return np.clip(array, clip_lower, clip_upper)

    def _plot(self, plot_ax, region):

        data, new_region = self.datafile.interactions(region)

        self.plot_matrix(plot_ax, data)

        return new_region

    def plot_matrix(self, ax, data):

        ax.axis('off')

        np.fill_diagonal(data, np.NaN)

        if self.clip:
            data = self.clip_for_plotting(data, self.clip)

        if self.rotate:
            rotated = rotate_heatmap(data, self.flip)
        else:
            rotated = data

        if self.log:
            rotated = np.log10(rotated)

        ax.imshow(rotated, interpolation='none', **self.kwargs)
