
class Panel(object):
    """Base class for browser panels"""
    def __init__(self):
        super(Panel, self).__init__()
        
    def get_config(self, feature):

        return {}

    def plot(self, ax, feature):

        return self._plot(ax, feature)
    
    def _plot(self, ax, feature):
        pass

