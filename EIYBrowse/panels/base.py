from ..filetypes import open_file
from ..exceptions import ImproperlyConfigured

class Panel(object):
    """Base class for browser panels"""
    def __init__(self):
        super(Panel, self).__init__()
        
    def get_config(self, feature):

        return {}

    def plot(self, ax, feature):

        label_ax, plot_ax = ax

        label_ax.set_axis_off()

        if 'name_rotate' in self.config.keys() and self.config.name_rotate:
            name_rotate = True
        else:
            name_rotate = False

        if hasattr(self, 'name') and not self.name is None:
            if name_rotate:
                label_ax.text(0.5, 0.5,self.name, horizontalalignment='center',
                      verticalalignment='center', fontsize=12, rotation=90)
            else:
                label_ax.text(0.5, 0.5,self.name, horizontalalignment='center',
                      verticalalignment='center', fontsize=12)


        return self._plot(plot_ax, feature)
    
    def _plot(self, ax, feature):
        pass

class FilePanel(Panel):
    """Base class for browser panels that need external data"""

    def __init__(self, **config):
        super(FilePanel, self).__init__()

        missing_keys = []

        for check_key in ['file_path', 'file_type']:
            if not check_key in config:
                missing_keys.append(check_key)

        if len(missing_keys):
            raise ImproperlyConfigured(
                'The configuration for {0} is missing the following keys: {1}'.format(
                    type(self).__name__, ', '.join(missing_keys)))
        
        self.datafile = open_file(config['file_path'],
                                  config['file_type'])

