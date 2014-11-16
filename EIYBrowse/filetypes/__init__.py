"""This module provides some helper functions for opening
the correct file handler given a string representation
of the file type to open.

Available filetypes are found through setuptools
`automatic plugin discovery feature
<https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins>`_.

EIYBrowse defines available filetype plugins under the
EIYBrowse.filetypes entry point. This module also adds gffutils FeatureDB
class, and the file classes defined by the metaseq package, if they are
available.

To define a new filetype which can be used by EIYBrowse, any package
just needs to define it in the entry_points section of the
package's setup.py. For example::

    setup(
        name = "EIYBrowse_ChIA_PET_plugin",
        packages=['chiapet_plugin'],
        entry_points = {'EIYBrowse.filetypes': [
                            'chia_pet = chiapet_plugin.plugin_module:ChiaPETPluginClass',
                        ]
                       },
    )

"""


from pkg_resources import iter_entry_points


def get_file_opener(file_type):

    import os
    on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

    if not on_rtd:
        defined_filetypes = {
            ep.name: ep.load()
            for ep in iter_entry_points('EIYBrowse.filetypes')}

        from metaseq._genomic_signal import _registry
        defined_filetypes.update(_registry)

    else:
        defined_filetypes = {}

    return defined_filetypes[file_type]


def open_file(file_path, file_type):
    file_opener = get_file_opener(file_type)
    return file_opener(file_path)
