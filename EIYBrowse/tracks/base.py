"""The tracks.base module defines abstract base classes, which
should be subclassed to create new tracks.

The :class:`Track` class should be chosen as a base class if
the track does not rely on any external data (e.g. if you want
to plot a scale bar.

The :class:`FileTrack` class should be chosen as a base class
if the track does rely on some external data file.
"""

from ..filetypes import open_file
import abc


class Track(object):

    """Base class for all browser tracks"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None, name_rotate=False):

        """Create a new track object.

        :param str name: Optional name label for the track
        :param bool name_rotate: Whether the name label should be
            rotated 90 degrees
        """

        super(Track, self).__init__()

        self.name = name
        self.name_rotate = name_rotate

    # Some classes won't need to do anything here, and can leave
    # this as it is. So we need to disable some warnings:
    # pylint: disable=unused-argument, no-self-use
    def get_config(self, region, browser_config):

        """Any subclass that needs to do setup before the axes
        are created should place that code here."""

        return {}

    def plot(self, region, plot_ax, label_ax=None):

        """Public method called when we need to plot the track to an
        axis. Sets up the axes, plots the name label if specified, and
        passes the rest of the work to the :meth:`_plot` method.

        :param region: Genomic region to plot.
        :type region: :class:`pybedtools.Interval`
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

        return self._plot(plot_ax, region)

    @abc.abstractmethod
    def _plot(self, plot_ax, region):

        """Private method to handle actual plotting. To be overwritten
        by a subclass"""

    @classmethod
    def from_config_dict(cls, **kwargs):

        """Intantiating a track object from the config file may require
        instantiating some other objects first (namely datafiles).

        For some tracks, we don't need to do this, so we simpy return
        an object of type cls with the arguments in kwargs.

        Any subclass that needs some logic to be executed before
        it can be instatiated should put that logic here.
        """

        return cls(**kwargs)

class FileTrack(Track):

    """Base class for browser tracks that need external data"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, datafile,
                 name=None, name_rotate=False):

        """Create a new track object with an attached datafile.

        Essentially this class does the same work as :class:`Track` except that
        it first uses :func:`~EIYBrowse.filetypes.open_file` to create a
        new file object and then attaches that object to self.datafile.

        :param datafile: A datafile object which handles extracting
            the data to plot for any given genomic region.
        :param str name: Optional name label for the track
        :param bool name_rotate: Whether the name label should be
            rotated 90 degrees
        """

        super(FileTrack, self).__init__(name, name_rotate)

        self.datafile = datafile

    @classmethod
    def from_config_dict(cls, file_path, file_type,
                               **kwargs):

        """Instead of instantiating a new track object with an open
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
