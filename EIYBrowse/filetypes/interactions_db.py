import sqlite3
import pybedtools
import numpy as np
from pandas.io import sql


class InteractionsDbFile(object):

    """Panel for displaying a continuous signal across a genomic region"""

    def __init__(self, interactions_db):
        super(InteractionsDbFile, self).__init__()

        self.db = sqlite3.connect(interactions_db)

        self.pos_query = """SELECT i FROM windows
                            WHERE chrom = '{chrom}' AND start <= {start}
                            ORDER BY start DESC LIMIT 1;"""

        self.loc_query = """SELECT start, stop FROM windows
                            WHERE i = '{i}' AND chrom = '{chrom}'
                            LIMIT 1;"""

    def get_data_from_bins(self, chrom, start, stop):

        query_string = """select x, y, value from {chrom}
                          where x >= '{start}' and x <= '{stop}'
                          and y >= '{start}' and y <= '{stop}';"""

        query = query_string.format(start=start, stop=stop,
                                    chrom=chrom)

        data_array = np.array(
            sql.read_sql(query, self.db).set_index(['x', 'y']).unstack())

        N = data_array.shape[0]

        data_array.flat[0:N ** 2:N + 1] = np.NAN

        return data_array

    def get_bin_from_location(self, chrom, location):
        pos = sql.read_sql(
            self.pos_query.format(chrom=chrom, start=location), self.db)
        return pos.values[0, 0]

    def get_location_from_bin(self, chrom, i):
        loc = sql.read_sql(self.loc_query.format(chrom=chrom, i=i), self.db)
        return tuple(loc.values[0])

    def bins_from_feature(self, feature):

        start_bin = self.get_bin_from_location(feature.chrom, feature.start)
        stop_bin = self.get_bin_from_location(feature.chrom, feature.stop)

        return feature.chrom, start_bin, stop_bin

    def feature_from_bins(self, chrom, start_bin, stop_bin):

        lstart, lstop = self.get_location_from_bin(chrom, start_bin)
        rstart, rstop = self.get_location_from_bin(chrom, stop_bin)

        return pybedtools.Interval(chrom, lstart, rstop)

    def interactions(self, feature):

        chrom, start, stop = self.bins_from_feature(feature)

        data = self.get_data_from_bins(chrom, start, stop)
        new_feature = self.feature_from_bins(chrom, start, stop)

        return data, new_feature
