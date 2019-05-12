import pandas as pd

import os
def ensure_dir(file_path):
  directory = os.path.dirname(file_path)
  if directory and not os.path.exists(directory):
    print("Creating new directory", directory)
    os.makedirs(directory)


import json
def get_cfg_str(x):
  # json.dumps(r.to_dict(), sort_keys=True, separators = (',', '~'))[1:-1]
  # It seems DoIt does not allow equal (=) char in task name
  return ",".join(['{}~{}'.format(k,v) for (k,v) in sorted(x.to_dict().items()) if k not in ['JUDI', 'name']])


def combine_csvs_base(params, infiles, outfile):
  df = pd.DataFrame()
  for indx, r in params.assign(infile = infiles).iterrows():
    tmp = pd.read_csv(r['infile'])
    for col in params.columns:
      tmp[col] = r[col]
    df = df.append(tmp, ignore_index=True)
  df.to_csv(outfile, index=False)


def combine_csvs(big, small):
  infiles = big['path'].tolist()
  outfile = small['path'].tolist()[0]
  params = big.drop(columns=['name', 'path'])
  combine_csvs_base(params, infiles, outfile)


from PyPDF2 import PdfFileMerger

def merge_pdfs_base(infiles, outfile):
  merger = PdfFileMerger()
  for pdf in infiles:
    merger.append(open(pdf, 'rb'))
  with open(outfile, 'wb') as fout:
    merger.write(fout)


def merge_pdfs(big, small):
  infiles = big['path'].tolist()
  outfile = small['path'].tolist()[0]
  merge_pdfs_base(infiles, outfile)

