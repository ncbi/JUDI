import pandas as pd
from tqdm import tqdm
tqdm.pandas()

import os
def ensure_dir(file_path):
  directory = os.path.dirname(file_path)
  if directory and not os.path.exists(directory):
    print("Creating new directory", directory)
    os.makedirs(directory)


import json
def get_cfg_str(x, sort_keys=True, param_sep=','):
  # json.dumps(r.to_dict(), sort_keys=True, separators = (',', '~'))[1:-1]
  # It seems DoIt does not allow equal (=) char in task name
  key_vals = x.to_dict().items()
  if sort_keys:
    key_vals = sorted(key_vals)
  return param_sep.join(['{}~{}'.format(k,v) if isinstance(v, str) else '{0}~{1:g}'.format(k,v)
                    for (k,v) in key_vals if k not in ['JUDI', 'name']])

def get_cfg_str_unsrt(x):
  return(get_cfg_str(x, False))


######################################################
############## COMBINE CSV FILES #####################
######################################################

def combine_csvs_base_slow(params, infiles, outfile, sep=','):
  df = pd.DataFrame()
  for indx, r in params.assign(infile = infiles).iterrows():
    print(r['infile'])
    tmp = pd.read_csv(r['infile'], sep=sep, index_col=[0]).reset_index()
    for col in params.columns:
      tmp[col] = r[col]
    df = df.append(tmp, ignore_index=True)
  df.to_csv(outfile, sep=sep, index=False)


def combine_csvs_base(params, infiles, outfile, sep=','):
  old_cols = params.columns.values.tolist()
  df = params.reset_index().assign(infile = infiles)
  def read_infile(x):
      infile = x.iloc[0,:]['infile']
      print(infile)
      return(pd.read_csv(infile, sep=sep, index_col=[0]).reset_index())
  df = df.groupby(old_cols).progress_apply(read_infile)
  # groupby creates one extra level of index, we need to remove that
  df.index = df.index.droplevel(df.index.nlevels-1)
  df = df.reset_index()
  df.to_csv(outfile, sep=sep, index=False)


def combine_csvs(big, small, sep=','):
  #print(big)
  #print(small)
  infiles = big['path'].tolist()
  outfile = small['path'].tolist()[0]
  print(infiles)
  print(outfile)
  params = big.drop(columns=['name', 'path'])
  combine_csvs_base(params, infiles, outfile, sep)

def combine_csvs_new(*arg, **kw):
  infiles = []
  params = pd.DataFrame()
  # all but last positional paramdb give input files
  for big in arg[:-1]:
    infiles += big['path'].tolist()
    params = params.append(big.drop(columns=['name', 'path']), ignore_index=True)
  # the last positional paramdb gives output file
  outfile = arg[-1]['path'].tolist()[0]
  combine_csvs_base(params, infiles, outfile, kw['sep'])


######################################################
####### GET SUBSET OF ROWS FROW CSVS       ###########
######################################################


def subset_csv(infile, outfile, params, sep=',', filt=None):
    """Subset rows of dataframe from <infile> and save in <outfile>.
    Other arguments:
    params -- JUDI parameters as a dictionary
    filt   -- a dictionary of dictionaries, filt[col][param] should
              contain the pandas query string to subset rows by applying
              rule param to column col
    """
    new_colnames = {} # to handle conflict of columns with same name as in params
    query_str = [] # query string parts to be combined using AND
    df = pd.read_csv(infile, sep=sep, index_col=[0]).reset_index()
    columns = df.columns.values.tolist()
    # to support query strings containing values from parameter settings
    # we add the parameter values as columns; later those will be deleted
    extra_cols = list(set(params.keys()) - set(columns))
    for ec in extra_cols:
        df[ec] = params[ec]
    #print('params', params)
    #print('columns', columns)
    #print('filt', filt)
    for pname, pval in params.items():
        if pval == 'all':
            # do nothing
            pass
        elif (pname in filt) and (pval in filt[pname]):
                query_str.append(f'({filt[pname][pval]})')
        else:
            if isinstance(pval, str): pval = f'"{pval}"'
            query_str.append(f'({pname} == {pval})')

    #for col in filt.keys():
    #    if (col in columns) and (col in params):
    #        param_val = params[col]
    #        if (param_val != 'all'):
    #            if (param_val in filt[col]):
    #                query_str.append(f'({filt[col][param_val]})')
    #            else:
    #                query_str.append(f'({col} == {param_val})')
    #        new_colnames[col] = f'{col}_old'
    print('query_str:', query_str)
    print(df)
    if (query_str):
        query_str = ' & '.join(query_str)
        print('query_str:', query_str)
        df = df.query(query_str)
        print(df)
    df = (df.drop(columns=extra_cols)
          .rename(columns=new_colnames)
         )
    print(df)
    print(outfile)
    df.to_csv(outfile, sep=sep, index=False)


######################################################
####### PUT MULTIPLE CSVS IN AN MSEXCEL    ###########
######################################################

def merge_csvs_base(params, infiles, outfile, sep=','):
  writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
  par_cols = list(params.columns)
  params['sheet'] = ['Sheet{}'.format(i+2) for i in range(params.shape[0])]
  params.to_excel(writer, 'Sheet1')
  for indx, r in params.assign(infile = infiles).iterrows():
    tmp = pd.read_csv(r['infile'], sep=sep, index_col=[0]).reset_index()
    for col in par_cols:
      tmp[col] = r[col]
    tmp.to_excel(writer, r['sheet'])
  writer.save()


def merge_csvs_excel(big, small, sep=','):
  infiles = big['path'].tolist()
  outfile = small['path'].tolist()[0]
  params = big.drop(columns=['name', 'path'])
  merge_csvs_base(params, infiles, outfile, sep)


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


def merge_pdfs_new(*arg, **kw):
  infiles = []
  # all but last positional paramdb give input files
  if kw['collate']:
    infiles = [z for y in zip(*[x['path'].tolist() for x in arg[:-1]]) for z in y]
  else:
    for big in arg[:-1]:
      infiles += big['path'].tolist()
  # the last positional paramdb gives output file
  outfile = arg[-1]['path'].tolist()[0]
  print(infiles)
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


def latex_tolerate(s):
  print("=============", s, "==============")
  print(s)
  s = re.sub(',', '\\\\string,', s)
  s = re.sub('~', '\\\\string~', s)
  s = re.sub('_', '\\\\string_', s)
  return s

def paste_pdfs_base(inpaths, outpath, title='', flow='below'):
  print("--------", title, "-----------")
  if isinstance(inpaths, str): inpaths = [inpaths]
  print("--------", inpaths, "-----------")
  prefix = os.path.splitext(outpath)[0]
  infiles = [latex_tolerate(os.path.abspath(path)) for path in inpaths]
  doc = Document(documentclass='standalone')
  doc.preamble.append(NoEscape(r'\usetikzlibrary{chains}'))
  with doc.create(TikZ(options=NoEscape(f'start chain = going {flow}, node distance=0'))) as pic:
    for infile in infiles:
      pic.append(TikZNode(text=NoEscape(f'\includegraphics{{{infile}}}'), options='on chain'))
    top = TikZNode(text=NoEscape('\\large\\bfseries '+latex_tolerate(title)), options='above', at=TikZCoordinate(0,0))
    top._position = '(current bounding box.north)'
    pic.append(top)
  doc.generate_pdf(NoEscape(prefix), clean_tex=False)


def pdf_matrix(big, small, title='', row=None, col=None):
  prefix = os.path.splitext(small['path'].tolist()[0])[0]
  if isinstance(row, str): row=[row]
  if isinstance(col, str): col=[col]
  df = big[row+col+['path']].set_index(row+col)
  for cl in col:
      df = df.unstack(cl)
  df = df['path']
  df = df.applymap(os.path.abspath)
  df = df.applymap(latex_tolerate)
  doc = Document(documentclass='standalone')
  doc.preamble.append(NoEscape(r'\usetikzlibrary{matrix}'))
  with doc.create(TikZ()) as pic:
    mbody = """\\tikzset{mylabel/.style={color=blue, font=\\large \\bfseries \\ttfamily}}
               \\matrix (m) [matrix of nodes, row sep = 2ex] {
            """
    mbody += ' \\\\\n'.join([r' & '.join([f'\includegraphics{{{df.iloc[r,c]}}}'
                                          for c in range(df.shape[1])])
                             for r in range(df.shape[0])])
    mbody += '\\\\\n};\n'
    for r in range(df.shape[0]):
      for c in range(df.shape[1]):
        tmp = df.iloc[r:r+1,c:c+1]
        names = tmp.index.names + tmp.columns.names
        vals = tmp.index.values.tolist() + tmp.columns.values.tolist()
        label = ','.join([f'{k}~{v}' for k,v in zip(names,vals)])
        label = latex_tolerate(label)
        mbody += f'\\node[above, mylabel] at (m-{r+1}-{c+1}.north) {{{label}}};\n'
    pic.append(NoEscape(mbody))
    top = TikZNode(text=NoEscape(latex_tolerate(title)),
                   options=['above', 'mylabel'],
                   at=TikZCoordinate(0,0))
    top._position = '(current bounding box.north)'
    pic.append(top)
  doc.generate_pdf(NoEscape(prefix), clean_tex=False)

def paste_pdfs(*arg, **kw):
  inpaths = arg[0:-1]
  outpath = arg[-1]
  paste_pdfs_base(inpaths, outpath, kw['title'])



######################################################
##### CREATE MULTI-INDEX MATRIX FROM DATAFRAME  ######
######################################################
# inpath: input csv/tsv file
# outpath: output MS xlsx file
# idx_spec: specification of the columns of input df
# in the form of 'row-idx-cols|col-idx-cols|remain-cols'
# the cols in the parts in between '|' are separated by space
# sep: separator in the input csv/tsv file
def df_to_multi_idx_excel(inpath, outpath, idx_spec, sep=','):
  parts = idx_spec.split('|')
  rowmidx = parts[0].strip().split()
  colmidx = parts[1].strip().split()
  cols = parts[2].strip().split()
  df = pd.read_csv(inpath, sep=sep)
  df = df[rowmidx + colmidx + cols]
  df = df.set_index(rowmidx + colmidx)
  for cx in colmidx:
    df = df.unstack(cx)
  print(df)
  df.to_excel(outpath)
