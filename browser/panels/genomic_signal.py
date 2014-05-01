from .base import Panel
from metaseq._genomic_signal import genomic_signal

class GenomicSignalPanel(Panel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) accross a genomic region"""
    def __init__(self, gsignal_path, gsignal_type, bins=800, color='#377eb8'):
        super(GenomicSignalPanel, self).__init__()

        self.bins, self.color = bins, color
        
        self.genomic_signal = genomic_signal(gsignal_path, gsignal_type)

    def get_config(self, feature):

        return { 'lines' : 2 }

    def _plot(self, ax, feature):

        ax.axis('off')
        sig_x, sig_y = self.genomic_signal.local_coverage(feature, bins=self.bins)
        patches = ax.fill_between(sig_x, sig_y, color=self.color)
        ax.set_xlim(feature.start, feature.stop)
        return patches
