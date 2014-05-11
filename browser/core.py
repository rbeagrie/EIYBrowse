import matplotlib.pyplot as plt

class Browser(object):
    """Class that hold plotting panels and controls panel position/style"""

    def __init__(self):
        super(Browser, self).__init__()
        
        self.panels = []

    def configure(self, panel_configs):

        return None

    def get_axes(self, panel_configs):

        total_lines = sum([ p['lines'] for p in panel_configs ])
        self.figure = plt.figure(figsize=(16,total_lines / 2.))
        axes = []
        line_index = 0

        for p_config in panel_configs:

            ax = plt.subplot2grid((total_lines,1), (line_index,0), rowspan=p_config['lines'])
            line_index += p_config['lines']
            axes.append(ax)

        return axes
        
    def plot(self, feature):
        """Plot all panels given a feature object for window size"""

        panel_configs = [ p.get_config(feature) for p in self.panels ]

        self.configure(panel_configs)

        axes = self.get_axes(panel_configs)

        results = [ p.plot(ax, feature) for p, ax in zip(self.panels, axes) ]

        return results
