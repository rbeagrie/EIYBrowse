from pkg_resources import iter_entry_points

defined_panels = {ep.name: ep.load()
                  for ep in iter_entry_points('EIYBrowse.panels')}
globals().update(defined_panels)
