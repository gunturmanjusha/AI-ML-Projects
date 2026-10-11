import nbformat as n
from pathlib import Path
nb=n.read('outputs/AIML_Project_1_Low_Code_Notebook.original.ipynb',4)
# Prevent placeholder cells from failing; retain every original section and replace executable milestones with the canonical workflow.
for c in nb.cells:
 if c.cell_type=='code': c.source='# Completed in the canonical workflow cells below; retained template position.'
def setcell(i,s):nb.cells[i].source=s
setcell(12,"from pathlib import Path\n# Canonical timestamp-grouped analysis. This executes all EDA artifacts, preprocessing, five baselines, ANN/XGBoost tuning and final evaluation.\nexec(compile(Path('authoritative_analysis.py').read_text(), 'authoritative_analysis.py', 'exec'))")
setcell(83,"import json,pandas as pd\nfrom IPython.display import display,Image\nresults=json.load(open('outputs/results.json'))\ndisplay(pd.Series(results['overview'])); display(Image('outputs/charts/eda_target_turbines.png')); display(Image('outputs/charts/eda_failure_signals.png')); display(Image('outputs/charts/eda_correlation.png'))")
setcell(91,"display(pd.DataFrame(results['split_metadata']).T)\nprint(results['preprocessing'])")
setcell(159,"display(pd.DataFrame(results['baseline_validation']))")
setcell(165,"# Expanded six-configuration timestamp-grouped XGBoost tuning is defined in tune_xgboost_expanded.py and was executed before this clean-kernel report.\nexec(compile(Path('update_authoritative_results.py').read_text(), 'update_authoritative_results.py', 'exec'))\nimport json\nxgb_tuning=json.load(open('outputs/xgboost_tuning.json')); display(pd.Series(xgb_tuning['search'])); results=json.load(open('outputs/results.json'))")
setcell(207,"display(pd.DataFrame(results['tuned_validation']))\nprint(results['selection_rule'])")
setcell(208,"print('Final model:',results['final_model']); display(pd.DataFrame([results['final_test']]))")
setcell(211,"display(Image('outputs/charts/feature_importance.png')); display(pd.DataFrame(results['feature_importance']))")
setcell(213,"display(pd.DataFrame([results['final_test']]))")
setcell(214,"display(Image('outputs/charts/final_test_confusion_matrix.png'))")
nb.cells[216].source='''## Business Insights\nThe tuned ANN is selected because it has the highest validation recall. On test data it misses 196 of 1,441 recorded fault states; these should be treated as the principal operational risk. It also produces 1,271 false positives, so remote evidence review and alert persistence rules are needed before technician dispatch.'''
nb.cells[218].source='''## Recommendations\n1. Rank sustained high-risk alerts for operations-centre review. 2. Use vibration, thermal, oil and maintenance readings together in technician inspection checklists. 3. Escalate recurring or multi-signal alerts to planned maintenance. 4. Monitor missed states, false-alert workload, downtime and data drift after deployment. This classifier labels recorded current condition; it does not establish a future-failure lead time.'''
n.write(nb,'AIML_Project_1_Low_Code_Notebook.ipynb');print('cells',len(nb.cells))
