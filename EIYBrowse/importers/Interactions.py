import pandas as pd
import itertools
import os
import sqlite3
import re
import logging
import numpy as np


def chunker(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


class MatrixLoader(object):

    def __init__(self, matrix_paths, db_path, chrom_regex='chr[0-9X]{1,2}', **kwargs):

        assert not os.path.exists(db_path)

        self.matrix_paths = matrix_paths
        self.db = sqlite3.connect(db_path)
        self.chrom_regex = chrom_regex
        self.windows = None

    def get_chrom_string(self, matrix_path):

        return re.search(self.chrom_regex, matrix_path).group(0)

    def add_matrix_to_db(self, matrix_path):

        chrom_data = self.get_data(matrix_path)

        if self.windows:
            self.windows.add_windows(chrom_data)

        chrom_data = np.array(chrom_data)

        chrom = self.get_chrom_string(matrix_path)

        logging.debug('This chromosome is {0}'.format(chrom))
        logging.debug('Chromosome size is {0}x{1}'.format(*chrom_data.shape))

        all_indices = itertools.product(
            xrange(chrom_data.shape[0]), xrange(chrom_data.shape[1]))

        for indices in chunker(50000, all_indices):
            table_data = [(p, q, chrom_data[p, q]) for p, q in indices]
            df = pd.DataFrame.from_records(
                table_data, columns=['x', 'y', 'value'])
            df.to_sql(chrom, self.db, if_exists='append')

        logging.debug('Creating index on table {0}'.format(chrom))
        self.db.execute('CREATE INDEX Idx{0} ON {0}(x,y);'.format(chrom))

    def add_matrices_to_db(self):

        for matrix_path in self.matrix_paths:

            logging.info('Adding matrix: {0}'.format(matrix_path))

            self.add_matrix_to_db(matrix_path)


class HiCWindows(object):

    def __init__(self, db_con):

        self.db = db_con

    def add_windows(self, data):

        def unpack_index(ix):

            loc_string = ix.split('|')[-1]
            parts = loc_string.split(':')
            chrom = parts.pop(0)
            start, stop = map(int, parts[0].split('-'))

            return chrom, start, stop

        windows = pd.DataFrame(
            map(unpack_index, data.index), columns=['chrom', 'start', 'stop'])

        windows['i'] = windows.index

        windows.to_sql('windows', self.db, if_exists='append')


class HiCLoader(MatrixLoader):

    def __init__(self, *args, **kwargs):

        super(HiCLoader, self).__init__(*args, **kwargs)
        self.windows = HiCWindows(self.db)

    def get_data(self, matrix_path):

        return pd.read_csv(matrix_path, sep='\t', index_col=0)


class NpzLoader(MatrixLoader):

    def __init__(self, *args, **kwargs):

        super(NpzLoader, self).__init__(*args, **kwargs)
        self.key = kwargs.get('npz_key', 'score')

    def get_data(self, matrix_path):

        return np.load(matrix_path)[self.key]
