from pkg_resources import iter_entry_points

import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    defined_tracks = {ep.name: ep.load()
                      for ep in iter_entry_points('EIYBrowse.tracks')}
else:
    defined_tracks = {}

globals().update(defined_tracks)
