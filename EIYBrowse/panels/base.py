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

    def plot(self, feature, plot_ax, label_ax=None):

        """Public method called when we need to plot the panel to an
        axis. Sets up the axes, plots the name label if specified, and
        passes the rest of the work to the :meth:`_plot` method.

        :param feature: Genomic region to plot.
        :type feature: :class:`pybedtools.Interval`
        :param plot_ax: Axis for plotting the data
        :type plot_ax: :class:`matplotlib.axes.AxesSubplot`
        :param label_ax: Axis for plotting the name label
        :type label_ax: :class:`matplotlib.axes.AxesSubplot`
        """

        if label_ax is not None:

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
    def _plot(self, plot_ax, feature):

        """Private method to handle actual plotting. To be overwritten
        by a subclass"""

    @classmethod
    def from_config_dict(cls, **kwargs):

        """Intantiating a panel object from the config file may require
        instantiating some other objects first (namely datafiles).

        For some panels, we don't need to do this, so we simpy return
        an object of type cls with the arguments in kwargs.

        Any subclass that needs some logic to be executed before
        it can be instatiated should put that logic here.
        """

        return cls(**kwargs)

class FilePanel(Panel):

    """Base class for browser panels that need external data"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, datafile,
                 name=None, name_rotate=False):

        """Create a new panel object with an attached datafile.

        Essentially this class does the same work as :class:`Panel` except that
        it first uses :func:`~EIYBrowse.filetypes.open_file` to create a
        new file object and then attaches that object to self.datafile.

        :param datafile: A datafile object which handles extracting
            the data to plot for any given genomic region.
        :param str name: Optional name label for the panel
        :param bool name_rotate: Whether the name label should be
            rotated 90 degrees
        """

        super(FilePanel, self).__init__(name, name_rotate)

        self.datafile = datafile

    @classmethod
    def from_config_dict(cls, file_path, file_type,
                               **kwargs):

        """Instead of instantiating a new panel object with an open
        datafile object, instead pass the path to the datafile and
        the file_type string specifiying the class which handles that
        file format. Open the datafile and instantiate the class with
        the newly created datafile object.

        :param str file_path: Path to the datafile location
        :param str file_type: String specifying the format of the datafile.
            The mapping between format specifiers and classes is defined by
            the EIYBrowse.filetypes entry point (see setuptools documentation
            or :mod:`EIYBrowse.filetypes` for more information.)
        """

        datafile = open_file(file_path, file_type)

        return cls(datafile, **kwargs)
