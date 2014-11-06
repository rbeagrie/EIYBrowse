import yaml
from .exceptions import ImproperlyConfigured
from .panels import defined_panels
from .core import Browser


class Config(dict):

    def init(self):
        super(Config, self).__init__()

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def panel_from_panel_config(panel_config):

    if not len(panel_config) == 1:
        raise ImproperlyConfigured(
            'Panel definitions should be a dictionary with one key, got {0}'.format(
                panel_config))

    panel_type = panel_config.keys()[0]

    if not panel_type in defined_panels:
        raise ImproperlyConfigured(
            'Could not find panel of type "{0}". Valid panel types are: {1}'.format(
                panel_type, ', '.join(defined_panels)))

    panel_conf = panel_config.values()[0] or {}

    return defined_panels[panel_type](**panel_conf)


def panels_from_config(config_dict):

    return [panel_from_panel_config(p_conf) for p_conf in config_dict['panels']]


def browser_from_config_dict(config_dict):

    if 'browser' in config_dict:
        browser = Browser(**config_dict['browser'])
    else:
        browser = Browser()

    browser.panels = panels_from_config(config_dict)

    return browser


def browser_from_config_yaml(config_yaml):

    return browser_from_config_dict(yaml.load(config_yaml))
