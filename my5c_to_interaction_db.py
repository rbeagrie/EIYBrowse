import argparse
import logging
from browser.importers.Interactions import HiCLoader, NpzLoader

parser = argparse.ArgumentParser(description='Import matrix files into an sqlite3 database')
parser.add_argument('-m','--matrix-file-paths', metavar='MATRIX_PATH', required=True, nargs='+', help='One or more input My5C files.')
parser.add_argument('-d','--database-path', metavar='DATABASE_PATH', required=True, help='Database path to write to')
parser.add_argument('-t','--matrix-type', metavar='MATRIX_TYPE', default='my5c', help='Format of provided matrix files')
parser.add_argument('-k','--npz-key', metavar='NPZ_KEY', help='Key to use for retrieving data from .npz files')
parser.add_argument('--debug',
    help='Print lots of debugging statements',
    action="store_const",dest="loglevel",const=logging.DEBUG,
    default=logging.WARNING
)
parser.add_argument('--verbose',
    help='Be verbose',
    action="store_const",dest="loglevel",const=logging.INFO
)

loaders = { 'my5c' : HiCLoader,
            'npz'  : NpzLoader,
          }

if __name__ == '__main__':

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    logging.debug(vars(args))

    Loader = loaders[args.matrix_type]

    Loader(args.matrix_file_paths, args.database_path, **vars(args)).add_matrices_to_db()

