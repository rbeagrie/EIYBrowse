from .interactions import InteractionsBasePanel
from GamTools import segmentation

class InteractionsGamPanel(InteractionsBasePanel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) across a genomic region"""
    def __init__(self, segmentation_file, flip, log, **kwargs):
        super(InteractionsGamPanel, self).__init__(flip, log, **kwargs)

        self.data = segmentation.open_segmentation(segmentation_file)
    
    def interactions(self, feature):
        
        interval = feature.chrom, feature.start, feature.stop
        ix_start, ix_stop = segmentation.index_from_interval(self.data, interval)
        region = self.data.iloc[ix_start:ix_stop,]
                
        return segmentation.get_matrix_from_regions(self.data, region), feature
