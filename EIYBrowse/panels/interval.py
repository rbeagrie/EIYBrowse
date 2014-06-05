from .base import Panel
from metaseq._genomic_signal import genomic_signal
import itertools
import pybedtools

class GenomicIntervalPanel(Panel):
    """Panel for displaying a discrete signal (e.g. a bed file of binding peaks) accross a genomic region"""
    def __init__(self, gsignal_path, gsignal_type, name=None, color='#377eb8'):
        super(GenomicIntervalPanel, self).__init__()

        self.name, self.color = name, color
        
        if gsignal_type == 'bigBed':
            self.interval_reader = bigBedReader(gsignal_path)
        elif gsignal_type == 'bed':
            self.interval_reader = bedReader(gsignal_path)
        else:
            raise NotImplementedError('Only bigBed is currently supported for the interval panel')

    def get_config(self, feature):

        return { 'lines' : 1 }

    def _plot(self, ax, feature):

        ax.set_axis_off()

        ax.set_xlim(feature.start, feature.end)
        ax.set_ylim(0,1)

        patches = []

        for interval in self.interval_reader.get_contained_features(feature):

            patches.append(ax.hlines(0.8, interval.start, interval.stop, lw=4))
            if interval.name is not None:
                ax.text(interval.start, 0.2, interval.name)

        return { 'patches' : patches ,
               }

class bigBedReader(object):

    def __init__(self, bigBed_path):
        super(bigBedReader, self).__init__()

        self.genomic_intervals = genomic_signal(bigBed_path, 'bigBed')

    def bigbed_iterator(self, interval, chunk_size=2000000):
        
        def _internal_chunker():
            for start in range(interval.start, interval.end, chunk_size):
                
                end = start + chunk_size
                if end > interval.end:
                    end = interval.end
                    
                sub_interval = pybedtools.Interval(interval.chrom, start, end)
                
                chunk_x, chunk_y = self.genomic_intervals.local_coverage(sub_interval)
                
                yield chunk_x[chunk_y.astype(bool)]
                
        return itertools.chain.from_iterable(_internal_chunker())

    def get_interval_limits(self, positions):
        
        # Chunk the iterable of positions into groups of consecutive numbers
        # see http://stackoverflow.com/questions/2361945
        for k, g in itertools.groupby(enumerate(positions), lambda (i,x):i-x):
            
            z = list(g)
            
            yield z[0][1], z[-1][1] 

    def get_contained_features(self, feature):

        for start, stop in self.get_interval_limits(self.bigbed_iterator(feature)):

            yield pybedtools.Interval(feature.chrom, start, stop)

class bedReader(object):

    def __init__(self, bed_path):
        super(bedReader, self).__init__()

        self.genomic_intervals = genomic_signal(bed_path, 'bed')

    def get_contained_features(self, feature):

        return self.genomic_intervals.adapter[feature]
