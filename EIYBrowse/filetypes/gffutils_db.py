"""The gffutils_db module provides a wrapper around the
:class:`gffutils.FeatureDB` class. Having a wrapper instead
of calling the class directly should make it easier to add
support for other methods of storing gene information
in the future.
"""

import gffutils

class GffutilsDb(object):

    """The GffutilsDb class handles the retrieval of gene
    level information from a :class:`gffutils.FeatureDB`
    database.
    """

    def __init__(self, db_path):

        """Create a new GffutilsDb object.

        :param str db_path: Path to gff_utils database
        """

        self.gene_db = gffutils.FeatureDB(db_path)

    def get_genes(self, feature):

        """Iterator returning information about genes in the genomic region
        specified by feature. For every gene in the identified region,
        the iterator should return a dictionary with two keys: 'gene' and
        'exons'. 'gene' should be a :class:`pybedtools.Interval` object
        giving the genomic span of the entire gene. 'exons' should be
        a list of :class:`pybedtools.Interval` objects giving the genomic
        span of each exon in the longest isoform of the gene.

        :param feature: Genomic region to convert to an index
        :type feature: :class:`pybedtools.Interval`
        """

        gene_information = self.gene_db.region(feature,
                                               completely_within=False,
                                               featuretype='gene')

        for gene in gene_information:

            mrnas = list(self.gene_db.children(gene.id, featuretype='mRNA'))

            longest_mrna = sorted(mrnas, key=lambda m: m.stop - m.start).pop()

            exons = self.gene_db.children(longest_mrna.id, featuretype='exon')

            yield {'gene': gene,
                   'exons': exons}

