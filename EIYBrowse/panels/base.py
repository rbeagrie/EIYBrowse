"""The panels.base module defines abstract base classes, which
should be subclassed to create new panels.

The :class:`Panel` class should be chosen as a base class if
the panel does not rely on any external data (e.g. if you want
to plot a scale bar.

The :class:`FilePanel` class should be chosen as a base class
if the panel does rely on some external data file.
"""

from ..filetypes import open_file
import abc


class Panel(object):

    """Base class for all browser panels"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None, name_rotate=False):

        """Create a new panel object.

        :param str name: Optional name label for the panel
        :param bool name_rotate: Whether the name label should be
            rotated 90 degrees
        """

        super(Panel, self).__init__()

        self.name = name
        self.name_rotate = name_rotate

    # Some classes won't need to do anything here, and can leave
    # this as it is. So we need to disable some warnings:
    # pylint: disable=unused-argument, no-self-use
    def get_config(self, feature, browser_config):

        """Any subclass that needs to do setup before the axes
        are created should place that code here."""

        return {}

    def plot(self, ax, feature):

        """Public method called when we need to plot the panel to an
        axis. Sets up the axes, plots the name label if specified, and
        passes the rest of the work to the :meth:`_plot` method.

        :param ax: tuple of matplotlib axes to plot to. The first is the
            name label axis and the second is the main plotting axis.
        :param feature: Genomic region to plot.
        :type feature: :class:`pybedtools.Interval`
        """

        label_ax, plot_ax = ax

        label_ax.set_axis_off()

        if hasattr(self, 'name') and not self.name is None:
            if self.name_rotate:
                label_ax.text(0.5, 0.5, self.name,
                              horizontalalignment='center',
                              verticalalignment='center',
                              fontsize=12, rotation=90)
            else:
                label_ax.text(0.5, 0.5, self.name,
                              horizontalalignment='center',
                              verticalalignment='center',
                              fontsize=12)

        return self._plot(plot_ax, feature)

    @abc.abstractmethod
    def _plot(self, ax, feature):

        """Private method to handle actual plotting. To be overwritten
        by a subclass"""


class FilePanel(Panel):

    """Base class for browser panels that need external data"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, file_path, file_type,
                 name=None, name_rotate=False):

        """Create a new panel object with an attached datafile.

        Essentially this class does the same work as :class:`Panel` except that
        it first uses :func:`~EIYBrowse.filetypes.open_file` to create a
        new file object and then attaches that object to self.datafile.

        :param str file_path: Path to the datafile location
        :param str file_type: String specifying the format of the datafile.
            The mapping between format specifiers and classes is defined by
            the EIYBrowse.filetypes entry point (see setuptools documentation
            or :mod:`EIYBrowse.filetypes` for more information.)
        :param str name: Optional name label for the panel
        :param bool name_rotate: Whether the name label should be
            rotated 90 degrees
        """

        super(FilePanel, self).__init__(name_rotate)

        self.datafile = open_file(file_path,
                                  file_type)
