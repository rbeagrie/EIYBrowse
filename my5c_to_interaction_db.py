import argparse
import logging
from browser.importers.Interactions import HiCLoader

parser = argparse.ArgumentParser(description='Import My5C files into an sqlite3 database')
parser.add_argument('-m','--my5c-file-paths', metavar='MY5C_PATH', required=True, nargs='+', help='One or more input My5C files.')
parser.add_argument('-d','--database-path', metavar='DATABASE_PATH', help='Database path to write to')
parser.add_argument('--debug',
    help='Print lots of debugging statements',
    action="store_const",dest="loglevel",const=logging.DEBUG,
    default=logging.WARNING
)
parser.add_argument('--verbose',
    help='Be verbose',
    action="store_const",dest="loglevel",const=logging.INFO
)

if __name__ == '__main__':

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    HiCLoader(args.my5c_file_paths, args.database_path).add_matrices_to_db()

