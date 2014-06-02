
class Panel(object):
    """Base class for browser panels"""
    def __init__(self):
        super(Panel, self).__init__()
        
    def get_config(self, feature):

        return {}

    def plot(self, ax, feature):

        label_ax, plot_ax = ax

        label_ax.set_axis_off()

        if hasattr(self, 'name') and not self.name is None:
            label_ax.text(0.5, 0.5,self.name, horizontalalignment='center',
                      verticalalignment='center', fontsize=12)

        return self._plot(plot_ax, feature)
    
    def _plot(self, ax, feature):
        pass

