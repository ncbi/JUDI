# This JUDI pipeline is to evaluate EvoGeneX tool to infer evolution of gene
# expression as in preprint: https://doi.org/10.1101/2020.01.06.895615
# The pipeline is summarized in Figure 1

from judi import File, Task, ParamDb
from judi.utils import combine_csvs
from io import StringIO

metadata_dir      = '../metadata'
sim_data_dir      = '../simdata/data'
sim_fitted_dir    = '../simdata/fitted'
final_results_dir = '../results'

# Define all high level parameters and their possible values
thetas       = [1000]
sigmasqs     = [0.025, 0.50, 1, 2, 4, 8, 16, 32]
gammatildes  = [1, 0.5, 0.25, 0.125, 0.0625, 0.03125, 1/64]
alphas       = [1/8, 1/4, 1/2, 1, 2, 4, 8, 16, 32, 64, 128, 256]
num_genes    = [1000]
num_reps     = [4]
sim_models   = ['OU1', 'OU2', 'BM']
tree_sizes   = ['small', 'big']
adapt_folds  = [0.1, 0.2, 0.5, 0.67, 1.5, 2, 5, 10]
sim_regs     = ['global', 'fruitveg']
fit_models   = ['hansen.re', 'brown.re', # from EvoGeneX package
                'hansen.av', 'brown.mv', # from OUCH package
                'hansen.av', 'brown.av', # again from OUCH package
               ]
fit_regs     = ['global', 'fruitveg']  # we need separate parameters for
                                       # simulation and fitting
fit_reps     = ['all', 'av']

# Not all simulation parameters are relevant evolutionary models.
# Do adjustment using dataframes with rows subset of Cartesian product 

# ATTN.1a: restricting parameter combinations

# Parameter alpha is relevant only for Ornstein-Uhlenbeck model
# For Brownian Motion model set alpha = 0
restrict_alphas = pd.DataFrame([[ou, alpha] for ou in ['OU1', 'OU2'] for alpha in alphas]
                  + [['BM', 0]], columns = ['model', 'alpha'])

# Parameter adaptive-fold is relevant only two regime Ornstein-Uhlenbeck model
# For Brownian Motion model and single regime OU set fold = 1
restrict_folds = pd.DataFrame([['OU2', fold] for fold in adapt_folds]
                  + [['BM', 1], ['OU1', 1]], columns = ['model', 'fold'])

# ATTN.1b: restricting parameter combinations

# Restrict regime for BM and OU1 to use only global regime 
# And for OU2 to regime that separates fruit and vegetable eating flies
reg_string = """model,modreg
BM,global
OU1,global
OU2,fruitveg
"""

# Restrict fitting models to replicates  
# hansen.re (in EvoGeneX) and hansen.mv (in OUCH) can use all replicates
# but hansen.av (in OUCH) can use only single replicate (use average)
replicate_string = """fitmodel,replicate
hansen.re,all
brown.re,all
hansen.av,av
brown.av,av
hansen.mv,all
brown.mv,all
"""


hypothesis_string = """hypo,fitmodel,regime,null,nullreg
OU2vBM,hansen.re,fruitveg,brown.re,global
OU2vOU,hansen.re,fruitveg,hansen.re,global
OUvBM,hansen.re,global,brown.re,global
OU2vBM,hansen.av,fruitveg,brown.av,global
OU2vOU,hansen.av,fruitveg,hansen.av,global
OUvBM,hansen.av,global,brown.av,global
#OU2vBM,hansen.mv,fruitveg,brown.mv,global
#OU2vOU,hansen.mv,fruitveg,hansen.mv,global
#OUvBM,hansen.mv,global,brown.mv,global
"""

#############################################################################
# Task1: Simulate Gene Expression
#############################################################################

# First define parameter databases required for task: simulate 

pdb_tree = ParamDb("tree")
pdb_tree.add_param(tree_sizes, "tree")

pdb_sim = ParamDb('simulate')
pdb_sim.add_param(sim_models, 'model')
pdb_sim.add_param(thetas, 'theta')
pdb_sim.add_param(sigmasqs, 'sigmasq')
pdb_sim.add_param(gammatildes, 'gammatilde')
pdb_sim.add_param(tree_sizes, 'tree')
pdb_sim.add_param(restrict_alphas)
pdb_sim.add_param(pd.read_csv(StringIO(reg_string), comment='#'))
pdb_sim.add_param(restrict_folds)

pdb_regime = ParamDb("regime")
pdb_regime.add_param(sim_regs, 'regime')

# Next define JUDI files associated with task: simulate 

jf_reg = File('regime', param=pdb_regime, root=metadata_dir,
              path=lambda x: 'regime_{}.csv'.format(x['regime']))
jf_modreg = jf_reg.copy().rename({'regime':'modreg'})

jf_tree = File('newick', param=pdb_tree, root=metadata_dir,
               path=lambda x: 'drosophila{}.newick'.format(48 if x['tree'] == 'big' else 9))
jf_sim = File('sim_data.tsv', param=pdb_sim, root=sim_data_dir)


class Simulate(Task):
  param = pdb_sim
  inputs = {'tre': jf_tree}
  targets = {'dat': jf_sim}
  actions = [("./simulate.R {} {} {} {} {} {} {} {} {} {}",
              ['$tre', '$dat', '#model', '#theta', '#sigmasq', '#gammatilde',
               1000, 10, '#fold', '#alpha'])]


#############################################################################
# Task2: Fit algorithms (EvoGeneX and OUCH) to simulated gene expression data
#############################################################################

# parameter database

pdb_fit = pdb_sim.copy("fit")
pdb_fit.add_param(pd.read_csv(StringIO(replicate_string), comment='#'))
pdb_fit.add_param(num_genes, 'numgene')
pdb_fit.add_param(num_reps, 'numrep')
pdb_fit.add_param(fit_regs, 'regime')
# ATTN.1c : Another way of restricting parameter combinations
pdb_fit.query('~(fitmodel in ["brown", "brown.av", "brown.mv", "brown.re"] & regime != "global")')
pdb_fit.show()

# JUDI files

jf_model_stats = File('model_stats.tsv', param=pdb_fit, root=sim_fitted_dir)


class FitModel(Task):
  param = pdb_fit
  inputs = {'exp': jf_sim, 'tre': jf_tree, 'reg': jf_reg}
  targets = {'out': jf_model_stats}
  actions = [('./fit_model.R {} {} {} {} {} {} {} {} {} {}',
              ['$exp', '$tre', '$out', '#fitmodel', '$reg', 0, '#numrep',
               '#replicate', 'norm', '#numgene'])]


#############################################################################
# Task3: Test Hypothesis using log likelihood ratio test
#############################################################################

pdb_hypothesis = pdb_sim.copy("hypothesis")
pdb_hypothesis.add_param(pd.read_csv(StringIO(hypothesis_string), comment='#'))

# ATTN.2 : Use the same file as both alternative (h1) and null hypothesis (h0)
#          Which of tests OU vs BM, OU2 vs BM and OU2 vs OU1 use which h1 and
#          h0 are controlled using the parameter database of the task
jf_null_stats = jf_model_stats.copy('null_stats')
jf_null_stats.rename({'fitmodel':'null', 'regime':'nullreg'})

jf_hypo_test = File('hypo_test_stats.tsv', param=pdb_hypothesis, root=sim_fitted_dir)


class TestHypothesis(Task):
  param = pdb_hypothesis
  inputs = {'h1': jf_model_stats, 'h0': jf_null_stats}
  targets = {'out': jf_hypo_test}
  actions = [('./compute_pval.R {} {} {} {}',
              ['$h1', '$h0', '$out', '#parcfg'])]


#############################################################################
# Task4: Combine results of hypothesis testing of the same data to
#        be used to infer mode of evolution (neutral/constained/adaptive)
#############################################################################

pdb_combine_hypo = pdb_hypothesis.copy('combine_hypo')
pdb_combine_hypo.mask("hypo regime null nullreg".split())

jf_hypo_combined = File('hypo_combined.tsv', param=pdb_combine_hypo,
                        root=sim_fitted_dir)

# ATTN.3 : Note that here we do not combine all the hypothesis tests
#          into a single file. Rather we combine only the results that
#          correspond to a particular simulated dataset and a fitmodel

class CombineHypotheses(Task):
  param = pdb_combine_hypo
  inputs = {'inp': jf_hypo_test}
  targets = {'out': jf_hypo_combined}
  actions = [(combine_csvs, ['#inp', '#out', "\t"])]


#############################################################################
# Task5: Identify constrained/neutral genes
#############################################################################

pdb_constrained = pdb_hypothesis.copy('constrained')
pdb_constrained.query("hypo == 'OUvBM'")
pdb_constrained.mask("hypo regime null nullreg".split())

jf_constrained = File('constrained_score.tsv', param=pdb_constrained,
                      root=sim_fitted_dir)

class IdentifyConstrained(Task):
  param = pdb_constrained
  inputs = {'inp': jf_hypo_combined}
  targets = {'out': jf_constrained}
  actions = [('./compute_constrained_score.R {} {}', ['$inp', '$out'])]

#############################################################################
# Task6: Combine constrained genes of all models ti compute ROC later 
#############################################################################

pdb_constrained_all_models = pdb_constrained.copy("constrained_all_models")
pdb_constrained_all_models.mask(['model', 'modreg', 'fitmodel', 'alpha',
                                 'sigmasq', 'gammatilde'])

jf_constrained_all_models = File('constrained_score_all_models.tsv',
                                 param=pdb_constrained_all_models,
                                 root=sim_fitted_dir)

class CombineConstrained(Task):
  param = pdb_constrained_all_models
  inputs = {'inp': jf_constrained}
  targets = {'out': jf_constrained_all_models}
  actions = [(combine_csvs, ["#inp", '#out'], {'sep':'\t'})]

#############################################################################
# Task7: Compute ROC 
#############################################################################

pdb_constrained_roc = pdb_constrained_all_models.copy("constrained_roc")
pdb_constrained_roc.add_param(alphas, 'alpha')
pdb_constrained_roc.add_param(['all', 'valid']+gammatildes, 'gammatilde')
pdb_constrained_roc.add_param(['all']+sigmasqs, 'sigmasq')
pdb_constrained_roc.query("~((gammatilde in ['all', 'valid']) & (sigmasq != 'all'))")
pdb_constrained_roc.query("~((gammatilde not in ['all', 'valid']) & (sigmasq == 'all'))")


jf_const_roc_pdf = File('const_roc.pdf', param=pdb_constrained_roc,
                        root=sim_fitted_dir)
jf_const_roc_csv = File('const_roc.csv', param=pdb_constrained_roc,
                        root=sim_fitted_dir)


class ComputeConstrainedPrecisionRecallPlot(Task):
  param = pdb_constrained_roc
  inputs = {'inp': jf_constrained_all_models}
  targets = {'out': jf_const_roc_csv, 'plt': jf_const_roc_pdf}
  actions = [('./precision_recall.R {} {} {} {} {} {} {} {} {}',
              ['$inp', '#alpha', '#fold', '#sigmasq', '#gammatilde', '$out',
               '$plt', 'OU1', 'TRUE'])]


#############################################################################
# Task8: Combine all ROC results to produce final report
#############################################################################

class MergeConstrainedPrecisionRecall(Task):
  inputs = {'inp': jf_const_roc_csv}
  targets = {'out': File('sim_precision_recall_single_reg.tsv', root = final_results_dir)}
  actions = [(combine_csvs, ['#inp', '#out', '\t'])]



#############################################################################
# Task9: Identify adaptive genes
#############################################################################

pdb_adaptive = pdb_hypothesis.copy('adaptive')
pdb_adaptive.query("hypo == 'OU2vBM'")

jf_adaptive = File('adaptive_score.tsv', param=pdb_adaptive,
                   root=sim_fitted_dir)

class IdentifyAdaptive(Task):
  param = pdb_adaptive
  inputs = {'inp': jf_hypo_combined}
  targets = {'out': jf_adaptive}
  actions = [('./compute_adaptive_score.R {} {} {}',
              ['$inp', '#regime', '$out'])]


#############################################################################
# Task10: Combine all adaptive genes
#############################################################################

pdb_adaptive_all_models = pdb_adaptive.copy("adaptive_all_models")
pdb_adaptive_all_models.mask(['model', 'modreg', 'fitmodel', 'alpha',
                              'sigmasq', 'gammatilde', 'fold'])

jf_adaptive_all_models = File('adaptive_score_all_models.tsv',
                              param=pdb_adaptive_all_models,
                              root=sim_fitted_dir)

class CombineAdaptive(Task):
  param = pdb_adaptive_all_models
  inputs = {'inp': jf_adaptive}
  targets = {'out': jf_adaptive_all_models}
  actions = [(combine_csvs, ["#inp", '#out'], {'sep':'\t'})]


#############################################################################
# Task10: Compute ROC for adaptive genes
#############################################################################

pdb_adaptive_roc = pdb_adaptive_all_models.copy("adaptive_roc")
pdb_adaptive_roc.add_param(alphas, 'alpha')
pdb_adaptive_roc.add_param(adapt_folds, 'fold')
pdb_adaptive_roc.add_param(['all', 'valid']+gammatildes, 'gammatilde')
pdb_adaptive_roc.add_param(['all']+sigmasqs, 'sigmasq')
pdb_adaptive_roc.query("~((gammatilde in ['all', 'valid']) & (sigmasq != 'all'))")
pdb_adaptive_roc.query("~((gammatilde not in ['all', 'valid']) & (sigmasq == 'all'))")

jf_roc_pdf = File('adaptive_roc.pdf', param=pdb_adaptive_roc,
                  root=sim_fitted_dir)

jf_roc_csv = File('adaptive_roc.csv', param=pdb_adaptive_roc,
                  root=sim_fitted_dir)


class ComputeAdaptivePrecisionRecallPlot(Task):
  param = pdb_adaptive_roc
  inputs = {'inp': jf_adaptive_all_models}
  targets = {'out': jf_roc_csv, 'plt': jf_roc_pdf}
  actions = [('./precision_recall.R {} {} {} {} {} {} {} {} {}',
              ['$inp', '#alpha', '#fold', '#sigmasq', '#gammatilde', '$out',
               '$plt', 'OU2', 'FALSE'])]

#############################################################################
# Task11: Combine ROC results for all adaptive genes
#############################################################################

class MergeAdaptivePrecisionRecall(Task):
  inputs = {'inp': jf_roc_csv}
  targets = {'out': File('sim_precision_recall_multi_reg.tsv', root = final_results_dir)}
  actions = [(combine_csvs, ['#inp', '#out', '\t'])]

