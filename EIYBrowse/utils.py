class Config(dict):
    def init(self):
        super(Config, self).__init__()
        
    def __getattr__(self, key):
        return self[key]
        
    def __setattr__(self, key, value):
        self[key] = value

def format_genomic_distance(distance, precision=1):
    """Turn an integer genomic distance into a pretty string"""

    formatting_string = '{{0:.{0}f}}'.format(precision)
    
    if distance < 1000:
        return '{0:d}bp'.format(int(distance))
    elif distance < 1000000:
        fmt_string = formatting_string + 'kb'
        return fmt_string.format(float(distance) / 1000)
    else:
        fmt_string = formatting_string + 'Mb'
        return fmt_string.format(float(distance) / 1000000)

