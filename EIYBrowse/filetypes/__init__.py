from pkg_resources import iter_entry_points


def get_file_opener(file_type):

    import os
    on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

    if not on_rtd:
        defined_filetypes = {
            ep.name: ep.load() for ep in iter_entry_points('EIYBrowse.filetypes')}

        import gffutils
        defined_filetypes.update({'gffutils_db': gffutils.FeatureDB})

        from metaseq._genomic_signal import _registry
        defined_filetypes.update(_registry)

    else:
        defined_filetypes = {}

    return defined_filetypes[file_type]


def open_file(file_path, file_type):
    file_opener = get_file_opener(file_type)
    return file_opener(file_path)
