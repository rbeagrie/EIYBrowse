from pkg_resources import iter_entry_points


def get_file_opener(file_type):
    defined_filetypes = {}

    for ep in iter_entry_points('EIYBrowse.filetypes'):

        defined_filetypes[ep.name] = ep.load()

    try:
        import gffutils
        defined_filetypes.update({'gffutils_db': gffutils.FeatureDB})

    except ImportError:
        pass

    try:
        from metaseq._genomic_signal import _registry
        defined_filetypes.update(_registry)

    except ImportError:
        pass


    return defined_filetypes[file_type]

def open_file(file_path, file_type):
    file_opener = get_file_opener(file_type)
    return file_opener(file_path)
