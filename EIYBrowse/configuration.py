"""The configuration module contains some helper functions for
generating :class:`~EIYBrowse.core.Browser` objects with all
the correct :class:`~EIYBrowse.panels.base.Panel` objects attached
starting from an external configuration file.

Currently only `YAML <http://en.wikipedia.org/wiki/YAML>`_ is
supported as a configuration file language, but other markup
flavours may be added at a later date.
"""

import yaml
from .exceptions import ImproperlyConfigured
from .panels import defined_panels
from .core import Browser


def panel_from_panel_config(panel_config):

    """Create a new :class:`~EIYBrowse.panels.base.Panel` object
    from a dictionary of configuration parameters.

    :param dict panel_config: Dictionary with a single key,
        which gives the name of the type of
        :class:`~EIYBrowse.panels.base.Panel` object. (e.g.
        "scale_bar"). The value of this key is another
        dictionary of key=value pairs to be passed as
        arguments to the new panel's constructor method.
    :returns: New :class:`~EIYBrowse.panels.base.Panel` object
    :raises ImproperlyConfigured: If the dictionary is
        not constructed correctly, or if the top-level key
        does not match any currently installed panels.
    """

    if not len(panel_config) == 1:
        raise ImproperlyConfigured(
            ('Panel definitions should be a dictionary '
             'with one key, got {0}').format(panel_config))

    panel_type = panel_config.keys()[0]

    if not panel_type in defined_panels:
        raise ImproperlyConfigured(
            ('Could not find panel of type "{0}". Valid '
             'panel types are: {1}').format(
                 panel_type, ', '.join(defined_panels)))

    panel_conf = panel_config.values()[0] or {}

    # Star args are a necessary evil here, as all the configuration
    # options have to be in dictionary form
    # pylint: disable=star-args
    return defined_panels[panel_type](**panel_conf)


def panels_from_config(config_dict):

    """Convert the panels section of a configuration file into a list of
    :class:`~EIYBrowse.panels.base.Panel` objects

    :param dict config_dict: Dictionary representation of a configuration
        file containing the key 'panels'. This key should point to a list
        of dictionaries, each of which defines the configuration
        parameters of a single :class:`~EIYBrowse.panels.base.Panel` instance.
    :returns: List of :class:`~EIYBrowse.panels.base.Panel` objects.
    """

    return [panel_from_panel_config(p_conf) for p_conf in config_dict['panels']]


def browser_from_config_dict(config_dict):

    """Convert a parsed configuration file in dictionary format into a
    :class:`~EIYBrowse.core.Browser` object with a full list of
    :class:`~EIYBrowse.panels.base.Panel` objects.

    :param dict config_dict: Dictionary containing a 'panels' key, defining
        the list of browser :class:`~EIYBrowse.panels.base.Panel` objects,
        and an optional 'browser' key, containing configuration options for
        the browser itself.
    :returns: :class:`~EIYBrowse.core.Browser` object ready to be used for
        plotting.
    """

    panels = panels_from_config(config_dict)

    if 'browser' in config_dict:

        # Star args are a necessary evil here, as all the configuration
        # options have to be in dictionary form
        # pylint: disable=star-args
        browser = Browser(panels, **config_dict['browser'])
    else:
        browser = Browser(panels)


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
