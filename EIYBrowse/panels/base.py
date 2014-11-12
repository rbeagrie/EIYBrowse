from ..filetypes import open_file


class Panel(object):

    """Base class for browser panels"""

    def __init__(self, name_rotate=False):
        super(Panel, self).__init__()

        self.name_rotate = name_rotate

    def get_config(self, feature, browser_config):

        return {}

    def plot(self, ax, feature):

        label_ax, plot_ax = ax

        label_ax.set_axis_off()

        if hasattr(self, 'name') and not self.name is None:
            if self.name_rotate:
                label_ax.text(0.5, 0.5, self.name, 
                              horizontalalignment='center',
                              verticalalignment='center', 
                              fontsize=12, rotation=90)
            else:
                label_ax.text(0.5, 0.5, self.name, 
                              horizontalalignment='center',
                              verticalalignment='center', 
                              fontsize=12)

        return self._plot(plot_ax, feature)

    def _plot(self, ax, feature):
        pass


class FilePanel(Panel):

    """Base class for browser panels that need external data"""

    def __init__(self, file_path, file_type, name_rotate=False):
        super(FilePanel, self).__init__(name_rotate)

        self.datafile = open_file(file_path,
                                  file_type)
