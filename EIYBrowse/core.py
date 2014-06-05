import matplotlib.pyplot as plt

class Browser(object):
    """Class that hold plotting panels and controls panel position/style"""

    def __init__(self, config={}):
        super(Browser, self).__init__()
        
        self.panels = []
        self.defaults = { 'width' : 16,
                          'lineheight' : .5 }
        self.defaults.update(config)

    def configure(self, panel_configs):

        return None

    def get_axes(self, panel_configs):

        total_lines = sum([ p['lines'] for p in panel_configs ])
        self.figure = plt.figure(figsize=(self.defaults['width']
                                          ,total_lines * self.defaults['lineheight']))
        axes = []
        line_index = 0

        for p_config in panel_configs:

            label_ax = plt.subplot2grid((total_lines,10), (line_index,0), 
                                       rowspan=p_config['lines'],)

            plot_ax = plt.subplot2grid((total_lines,10), (line_index,1), 
                                       rowspan=p_config['lines'],
                                       colspan=9)
            line_index += p_config['lines']
            axes.append((label_ax, plot_ax))

        return axes
        
    def plot(self, feature):
        """Plot all panels given a feature object for window size"""

        panel_configs = [ p.get_config(feature) for p in self.panels ]

        self.configure(panel_configs)

        axes = self.get_axes(panel_configs)

        results = [ p.plot(ax, feature) for p, ax in zip(self.panels, axes) ]

        return self.figure, axes, results
