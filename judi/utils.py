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

def get_cfg_str_unsrt(x):
  # json.dumps(r.to_dict(), sort_keys=True, separators = (',', '~'))[1:-1]
  # It seems DoIt does not allow equal (=) char in task name
  return ",".join(['{}~{}'.format(k,v) for (k,v) in x.to_dict().items() if k not in ['JUDI', 'name']])


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


######################################################
############## COMBINE PDF PAGES #####################
######################################################

from PyPDF2 import PdfFileMerger

def merge_pdfs_base(infiles, outfile):
  print(infiles)
  print(outfile)
  merger = PdfFileMerger()
  if isinstance(infiles, str): infiles = [infiles]
  for pdf in infiles:
    print(pdf)
    merger.append(open(pdf, 'rb'))
  with open(outfile, 'wb') as fout:
    merger.write(fout)


def merge_pdfs(big, small):
  infiles = big['path'].tolist()
  outfile = small['path'].tolist()[0]
  merge_pdfs_base(infiles, outfile)


######################################################
### COMBINE PDF IMAGES HORIZONTALLY IN SINGLE PAGE  ##
######################################################

import pdf2image
from pdf2image import convert_from_path
from PIL import Image

def tile_pdfs_base(infiles, outfile):
  images = []
  if isinstance(infiles, str): infiles = [infiles]
  for infile in infiles:
    images += convert_from_path(infile, dpi=300)
  widths, heights = zip(*(i.size for i in images))
  total_width = sum(widths)
  max_height = max(heights)
  new_im = Image.new('RGB', (total_width, max_height))
  x_offset = 0
  for im in images:
    new_im.paste(im, (x_offset, 0))
    x_offset += im.size[0] 
  new_im.save(outfile)

def tile_pdfs(*arg, **kw):
  inpaths = arg[0:-1]
  outpath = arg[-1]
  tile_pdfs_base(inpaths, outpath)


######################################################
##### COMBINE PDFS HORIZONTALLY IN SINGLE PAGE  ######
######################################################

from pylatex import Document, TikZ, TikZNode, TikZCoordinate
from pylatex.utils import italic, NoEscape
from pylatex.package import Package
import os, re

def paste_pdfs_base(inpaths, outpath, title=''):
  if isinstance(inpaths, str): inpaths = [inpaths]
  prefix = os.path.splitext(outpath)[0]
  def latex_tolerate(s):
    s = re.sub(',', '\string,', s)
    s = re.sub('~', '\string~', s)
    return s
  infiles = [latex_tolerate(os.path.abspath(path)) for path in inpaths]
  doc = Document(documentclass='standalone')
  doc.preamble.append(NoEscape(r'\usetikzlibrary{chains}'))
  with doc.create(TikZ(options=NoEscape('start chain = going right, node distance=0'))) as pic:
    for infile in infiles:
      pic.append(TikZNode(text=NoEscape(f'\includegraphics{{{infile}}}'), options='on chain'))
    top = TikZNode(text=NoEscape('\\large\\bfseries '+latex_tolerate(title)), options='above', at=TikZCoordinate(0,0))
    top._position = '(current bounding box.north)'
    pic.append(top)
  doc.generate_pdf(NoEscape(prefix), clean_tex=False)

def paste_pdfs(*arg, **kw):
  inpaths = arg[0:-1]
  outpath = arg[-1]
  paste_pdfs_base(inpaths, outpath)
