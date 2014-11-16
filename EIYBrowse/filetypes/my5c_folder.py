"""The my5c_folder module contains classes for working with individual
my5c output files, one per chromosome, arranged in folders. Each
file divides the chromosome into a number of bins, and the interaction
between all pairs of bins is represented as a tab-delimited matrix.

These folders of files can be used as input to the
:class:`~EIYBrowse.panels.interactions.InteractionsPanel` class.
"""

import os
import glob
import numpy as np
import pandas as pd
import pybedtools


class NoFilesError(Exception):
    """Exception to be raised if no files could be found"""
    pass


class TooManyFilesError(Exception):
    """Exception to be raised if more than one file was found
    for a single chromosome.
    """
    pass


class InvalidChromError(Exception):
    """Exception to be raised if interactions are requested
    from a non-existing chromosome."""
    pass


def format_window(window):
    """Given a my5c style location specifier, return the
    name of the chromosome and the genomic start and stop.

    :param str window: Genomic location in my5c format, e.g.
        HiC|mm9|chr7:7000000-7999999
    :returns: chromosome name, start position in bp, stop position
        in bp.
    """

    parts = window.split('|')
    location = parts[-1]
    chrom, pos = location.split(':')
    start, stop = [int(i) for i in pos.split('-')]
    return chrom, start, stop


def format_windows(windows):
    """Given an iterator of my5c style location specifiers,
    return a :class:`pandas.multiindex` with the chromosome name,
    genomic start and genomic stop positions as the levels.
    :param list windows: List (or other iterator) of my5c style
        location specifiers.
    :returns: :class:`pandas.multiindex`
    """

    return pd.MultiIndex.from_tuples([format_window(w) for w in windows],
                                     names=['chrom', 'start', 'stop'])


class My5cFile(object):

    """The My5cFile class handles extraction of interactions from
    an individual my5c file.

    The data is stored in the interactions attribute as a 2d numpy array,
    and must therefore be accessed by the index of the array cell. For
    example, if the data is at 50kb resolution, the region from 500kb to
    550kb corresponds to the 11th cell, which has the index of 10. To
    obtain the interaction between an object at 530kb and one at 590kb,
    you could therefore directly call my5cfile.interactions[10,11].

    Of course we want to obtain the interactions between different
    regions specified in genomic co-ordinates (i.e. base pairs). Most of
    the logic in this class is related to this conversion.

    To obtain the set of interactions for a region in genomic co-ordinates
    the :meth:`get_interactions` method is called with a
    :class:`pybedtools.Interval` object. :meth:`index_from_interval` is
    called to convert the interval into the correct index for the
    internal numpy array, and the corresponding cells of the array are
    returned.
    """

    def __init__(self, file_path):

        """Create a new My5cFile object. Stores the interactions data
        as a numpy array in the interactions attribute, and stores the
        genomic location for each bin in the windows attribute.

        :param str file_path: Path to the my5c file containing interaction
            data.
        """

        data = pd.read_csv(file_path,
                           sep='\t', index_col=0)

        self.interactions = np.array(data)
        self.windows = format_windows(data.index)

    def index_from_interval(self, region):

        """Convert a :class:`pybedtools.Interval` object into a start
        and stop index for the internal numpy array.

        We select all the bins overlapping the region from the windows
        :class:`~pandas.DataFrame` by searching for bins whose stop
        co-ordinate is larger than the start co-ordinate of the interval
        and whose start co-ordinate is less than the stop co-ordinate
        of the interval. We then return the index of the first covered
        window, and the last covered window + 1 (as slicing the numpy
        array will return up to but not including the last index).

        :param region: Genomic region to convert to an index
        :type region: :class:`pybedtools.Interval`
        :returns: Start and stop array indices as integers.
        """

        if not region.start < region.stop:
            raise ValueError(
                'Interval start {0} larger than interval end {1}'.format(
                    region.start, region.stop))

        window_in_region = (
            (self.windows.get_level_values('stop') > region.start) &
            (self.windows.get_level_values('start') < region.stop) &
            (self.windows.get_level_values('chrom') == region.chrom))

        covered_windows = np.nonzero(window_in_region)[0]

        if not len(covered_windows):
            if not region.chrom in self.windows.levels[0]:
                raise InvalidChromError(
                    '{0} not found in the list of windows'.format(
                        region.chrom))

        start_index = covered_windows[0]
        stop_index = covered_windows[-1] + 1

        return start_index, stop_index

    def get_interactions(self, region):

        """Get the interactions within a given genomic region.

        :param region: Genomic region to convert to an index
        :type region: :class:`pybedtools.Interval`
        :returns: numpy array containing the interaction data,
            and a :class:`pybedtools.Interval` object giving the genomic
            co-ordinates of the returned array.
        """

        start, stop = self.index_from_interval(region)

        return (self.interactions[start:stop, start:stop],
                self.indices_to_interval(start, stop))

    def indices_to_interval(self, start, stop):

        """Return the genomic co-ordinates of the interactions returned.

        Since this class will return a numpy array of interactions, the
        start and stop co-ordinates of the array may not exactly
        match with the region requested (for example, if interactions are
        required for the region from 34kb to 456kb from a matrix with 10kb
        resolution, the returned results will span from 30kb to 460kb.

        In order to adjust the size of the returned array to match the
        boundaries of the plotting window, the
        :class:`~EIYBrowse.panels.interactions.InteractionsPanel` must
        be given the exact start and stop of the region returned from the
        array. This method finds these values for a given pair of indices.

        :param int start: Starting index of the interaction array.
        :param int stop: Ending index of the interaction array.
        :returns: Genomic region spanned by the given slice of the internal
        numpy array.
        """

        start_window = self.windows[start]
        stop_window = self.windows[stop - 1]
        return pybedtools.Interval(start_window[0],
                                   start_window[1],
                                   stop_window[2])


class My5CFolder(object):

    """The My5CFolder class provides an interface to a folder of my5c files.

    the :meth:`interactions` method is called with a
    :class:`pybedtools.Interval` object, and the chrom attribute is used to
    identify the my5c file in the folder containing the relevant
    interactions. The :class:`My5cFile` object corresponding to that
    chromosome is created and the :class:`pybedtools.Interval` is passed
    to it's :meth:`My5cFile.interactions` method.
    """

    def __init__(self, folder_path, file_class=My5cFile):

        """Create a new My5CFolder object.

        :param str folder_path: Path to the folder containing the my5c
            files.
        :param class file_class: Class to use for opening the returned file.
        """

        self.folder_path = folder_path
        self.file_class = file_class

    def find_chrom_file(self, chrom):

        """Find the path to the my5c file containing the data for the given
        chromosome.

        :param str chrom: Name of the chromosome to find.
        :returns: Path to the located my5cfile.
        :raises TooManyFilesError: If more than one file is found matching
            the given chromosome name.
        :raises NoFilesError: If no file is found matching the given
            chromosome name.
        """

        search_string = '*{0}_{0}*.my5c.txt'.format(chrom)

        found_files = glob.glob(os.path.join(self.folder_path, search_string))

        if len(found_files) > 1:
            raise TooManyFilesError(
                ('folder containing my5c files must have '
                 'only one my5c file per chromosome'))
        if not len(found_files):
            raise NoFilesError(
                'No npz file found matching {0} with '
                'search string "{1}"'.format(
                    chrom, search_string))

        return found_files[0]

    def get_my5c_file(self, chrom):

        """Return the filetype object holding the data for the given chromosome.

        We first call :meth:`find_chrom_file` to determine the path to the
        data file, then pass this path to whichever class is defined by
        the file_class attribute (which defaults to :class:`My5cFile`).

        :param str chrom: Chromosome to find data for.
        :returns: Object of the class specified by the file_class attribute.
        """

        my5c_path = self.find_chrom_file(chrom)

        return self.file_class(my5c_path)

    def interactions(self, region):

        """Return the interactions inside the specified region.

        First use the chrom attribute of the region to get a file object
        representing all the interactions for that chromosome. Then
        call the object's get_interactions method to obtain a numpy
        array of the interactions within the specified region.

        :param region: Genomic region to convert to an index
        :type region: :class:`pybedtools.Interval`
        :returns: numpy array containing the interaction data,
            and a :class:`pybedtools.Interval` object giving the genomic
            co-ordinates of the returned array.
        """

        my5c_file = self.get_my5c_file(region.chrom)

        return my5c_file.get_interactions(region)
