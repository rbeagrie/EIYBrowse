from .base import FilePanel
import itertools
import numpy as np
import matplotlib.pyplot as plt

class GenePanel(FilePanel):
    """Panel for displaying a continuous signal (e.g. ChIP-seq) accross a genomic region"""
    def __init__(self, **config):

        self.config = { 'color':'#377eb8',
                        'name' : None,
                        'fontsize':10,
                        'file_type':'gffutils_db'}

        self.config.update(config)

        super(GenePanel, self).__init__(**self.config)
        
        self.name = self.config['name']

    def get_config(self, feature, browser_config):

        self.index = itertools.cycle(np.arange(1,0,-0.25))

        self.levels = GeneLevels()

        self.genes = list(self.iter_features(self.datafile.region(feature, completely_within=False, featuretype='gene')))
        
        _fig = plt.figure(figsize=(16,1))
        _ax = _fig.add_subplot(111)
        _ax.set_xlim(feature.start, feature.stop)
        _r = _fig.canvas.get_renderer()

        for g in self.genes:

            line, text = self.plot_gene(_ax, g['gene'])

            l_bb, t_bb = line.get_window_extent(_r), text.get_window_extent(_r)
            start = l_bb.x0
            stop = max([ l_bb.x1, t_bb.x1 ])
            stop = stop * 1.1
            self.levels.add_gene(g, start, stop)

        self.total_levels = len(self.levels.levels)

        plt.close('all')

        return { 'lines' : self.total_levels }
        
    def iter_features(self, genes):
        
        gene_iterator = (gene for gene in genes)
        
        for gene in gene_iterator:
            mrnas = list(self.datafile.children(gene.id, featuretype='mRNA'))
            longest_mrna = sorted(mrnas, key=lambda m: m.stop - m.start).pop()
            exons = self.datafile.children(longest_mrna.id, featuretype='exon')
            yield { 'gene' : gene,
                    'mrna' : longest_mrna,
                    'exons': exons }
            
    def get_axis_start_stop(self, ax, interval):
        
        xstart, xstop = ax.get_xlim()
        xspan = xstop - xstart

        if interval.start <= xstart:
            iv_start = 0.0
        else:
            dist_from_start = interval.start - xstart
            iv_start = dist_from_start / xspan
        if interval.stop >= xstop:
            iv_stop = 1.0
        else:
            dist_from_end = xstop - interval.stop
            iv_stop = 1.0 - (dist_from_end / xspan)
            
        return iv_start, iv_stop
    
    def plot_name(self, ax, start, name, ix=(0,1)):

        span = 1. / ix[1]
        
        return ax.text(start, ix[0] - span, name, fontsize=self.config['fontsize'])
            
    def plot_gene(self, ax, gene, ix=(0,1)):
        
        start, stop = self.get_axis_start_stop(ax, gene)

        span = 1. / ix[1]

        line_patch = ax.axhline(ix[0] - 2*span/5., start, stop, linewidth=1, color='r')
        name_patch = self.plot_name(ax, gene.start, gene.attributes['Name'][0], ix)

        return line_patch, name_patch
            
    def plot_exon(self, ax, exon, ix=(0,1)):
        
        start, stop = self.get_axis_start_stop(ax, exon)

        span = 1. / ix[1]

        ax.axhspan(ix[0]-span/5., ix[0]-3*span/5., start, stop, color='r')
        
    def _plot(self, ax, feature):
        
        ax.axis('off')
        ax.set_xlim(feature.start, feature.stop)
        ax.set_ylim(0,1)
        
        
        for i, level in enumerate(self.levels.levels):

            for g in level.genes:
                
                ix = (1.0 - (i * (1.0 / self.total_levels)), self.total_levels)
                
                self.plot_gene(ax, g['gene'], ix)
                
                for e in g['exons']:
                    
                    self.plot_exon(ax, e, ix)

class GeneLevel(object):
    
    def __init__(self):
        
        self.genes = []
        self.stop = 0
        
    def add_gene(self, gene, stop):
        
        self.genes.append(gene)
        self.stop = stop
        
class GeneLevels(object):
    
    def __init__(self):
        
        self.levels = [ GeneLevel() ]
        
    def add_gene(self, gene, start, stop):
        
        lev = self.get_gene_level(start)
        lev.add_gene(gene, stop)
        
    def get_gene_level(self, start):
        
        for lev in self.levels:
            if start > lev.stop:
                return lev
        
        new_lev = GeneLevel()
        self.levels.append(new_lev)
        
        return new_lev
