import argparse
import logging
from browser.importers.Windows import add_windows_to_db

parser = argparse.ArgumentParser(description='Import bed files into an sqlite3 database')
parser.add_argument('-b','--bed-file-path', metavar='BED_PATH', required=True, help='Input bed file')
parser.add_argument('-d','--database-path', metavar='DATABASE_PATH', required=True, help='Database path to write to')
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

    add_windows_to_db(args.database_path, args.bed_file_path)

