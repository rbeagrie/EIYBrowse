from metaseq._genomic_signal import _registry
import gffutils
from pkg_resources import iter_entry_points

defined_filetypes = { ep.name : ep.load() for ep in iter_entry_points('EIYBrowse.filetypes') }

defined_filetypes.update({'gffutils_db': gffutils.FeatureDB})

defined_filetypes.update(_registry)

globals().update(defined_filetypes)

def open_file(file_path, file_type):
    return defined_filetypes[file_type](file_path)
