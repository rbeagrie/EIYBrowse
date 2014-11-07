from pkg_resources import iter_entry_points

import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    defined_panels = {ep.name: ep.load()
                      for ep in iter_entry_points('EIYBrowse.panels')}
else:
    defined_panels = {}

globals().update(defined_panels)
