"""The configuration module contains some helper functions for
generating :class:`~EIYBrowse.core.Browser` objects with all
the correct :class:`~EIYBrowse.tracks.base.Track` objects attached
starting from an external configuration file.

Currently only `YAML <http://en.wikipedia.org/wiki/YAML>`_ is
supported as a configuration file language, but other markup
flavours may be added at a later date.
"""

import yaml
from .exceptions import ImproperlyConfigured
from .tracks import defined_tracks
from .core import Browser


def track_from_track_config(track_config):

    """Create a new :class:`~EIYBrowse.tracks.base.Track` object
    from a dictionary of configuration parameters.

    :param dict track_config: Dictionary with a single key,
        which gives the name of the type of
        :class:`~EIYBrowse.tracks.base.Track` object. (e.g.
        "scale_bar"). The value of this key is another
        dictionary of key=value pairs to be passed as
        arguments to the new track's constructor method.
    :returns: New :class:`~EIYBrowse.tracks.base.Track` object
    :raises ImproperlyConfigured: If the dictionary is
        not constructed correctly, or if the top-level key
        does not match any currently installed tracks.
    """

    if not len(track_config) == 1:
        raise ImproperlyConfigured(
            ('Track definitions should be a dictionary '
             'with one key, got {0}').format(track_config))

    track_type = track_config.keys()[0]

    if not track_type in defined_tracks:
        raise ImproperlyConfigured(
            ('Could not find track of type "{0}". Valid '
             'track types are: {1}').format(
                 track_type, ', '.join(defined_tracks)))

    track_conf = track_config.values()[0] or {}

    track_class = defined_tracks[track_type]

    # Star args are a necessary evil here, as all the configuration
    # options have to be in dictionary form
    # pylint: disable=star-args
    return track_class.from_config_dict(**track_conf)


def tracks_from_config(config_dict):

    """Convert the tracks section of a configuration file into a list of
    :class:`~EIYBrowse.tracks.base.Track` objects

    :param dict config_dict: Dictionary representation of a configuration
        file containing the key 'tracks'. This key should point to a list
        of dictionaries, each of which defines the configuration
        parameters of a single :class:`~EIYBrowse.tracks.base.Track` instance.
    :returns: List of :class:`~EIYBrowse.tracks.base.Track` objects.
    """

    return [track_from_track_config(p_conf) for p_conf in config_dict['tracks']]


def browser_from_config_dict(config_dict):

    """Convert a parsed configuration file in dictionary format into a
    :class:`~EIYBrowse.core.Browser` object with a full list of
    :class:`~EIYBrowse.tracks.base.Track` objects.

    :param dict config_dict: Dictionary containing a 'tracks' key, defining
        the list of browser :class:`~EIYBrowse.tracks.base.Track` objects,
        and an optional 'browser' key, containing configuration options for
        the browser itself.
    :returns: :class:`~EIYBrowse.core.Browser` object ready to be used for
        plotting.
    """

    tracks = tracks_from_config(config_dict)

    if 'browser' in config_dict:

        # Star args are a necessary evil here, as all the configuration
        # options have to be in dictionary form
        # pylint: disable=star-args
        browser = Browser(tracks, **config_dict['browser'])
    else:
        browser = Browser(tracks)


    return browser


def browser_from_config_yaml(config_yaml):

    """Parse some configuration yaml and pass the resulting dictionary to
    :func:`browser_from_config_dict` to generate the correct
    :class:`~EIYBrowse.core.Browser` object.

    :param str config_yaml: String containing valid YAML to parse into a
        dictionary format.
    :returns: :class:`~EIYBrowse.core.Browser` object ready to be used for
        plotting.
    """

    return browser_from_config_dict(yaml.load(config_yaml))
