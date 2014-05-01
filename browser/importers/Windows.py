import pandas as pd
import sqlite3
import os

def read_bed_windows(path):
    return pd.read_csv(path, delim_whitespace=True, header=False, names=['chrom', 'start', 'stop'])

def get_window_indexes(windows):
    windows['full_i'] = windows.index
    starts = windows.groupby('chrom').min()['full_i']
    def get_chr_index(row):
        return row['full_i'] - starts[row['chrom']]
    windows['i'] = windows.apply(get_chr_index, axis=1)
    windows = windows.drop('full_i', axis=1)
    return windows

def add_windows_to_db(db_path, windows_path):
    
    assert os.path.exists(db_path)
        
    con = sqlite3.connect(db_path)
    
    windows = get_window_indexes(read_bed_windows(windows_path))
    windows.to_sql('windows', con)
        
    con.close()
