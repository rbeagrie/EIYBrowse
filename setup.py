import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "EIYBrowse",
    version = "0.0.1",
    author = "Rob Beagrie",
    author_email = "rob@beagrie.com",
    description = ("A genome browser written in python."),
    packages=['EIYBrowse',
              'EIYBrowse.tracks',
              'EIYBrowse.importers',
              'EIYBrowse.filetypes'],
    entry_points = {'EIYBrowse.tracks': [
                        'genes = EIYBrowse.tracks.genes:GeneTrack',
                        'signal = EIYBrowse.tracks.genomic_signal:GenomicSignalTrack',
                        'intervals = EIYBrowse.tracks.interval:GenomicIntervalTrack',
                        'interactions = EIYBrowse.tracks.interactions:InteractionsTrack',
                        'location = EIYBrowse.tracks.location:LocationTrack',
                        'scale_bar = EIYBrowse.tracks.scale_bar:ScaleBarTrack',
                        ],
                    'EIYBrowse.filetypes': [
                        'interactions_db = EIYBrowse.filetypes.interactions_db:InteractionsDbFile',
                        'gffutils_db = EIYBrowse.filetypes.gffutils_db:GffutilsDb',
                        'my5c_folder = EIYBrowse.filetypes.my5c_folder:My5CFolder',
                    ]
                   },
    install_requires = ["matplotlib", "pybedtools","numpy"],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
