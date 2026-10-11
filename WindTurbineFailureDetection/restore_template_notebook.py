import nbformat as n
p='outputs/AIML_Project_1_Low_Code_Notebook.original.ipynb';nb=n.read(p,4)
def cell(src): nb.cells.append(n.v4.new_code_cell(src))
nb.cells.append(n.v4.new_markdown_cell('# Audit Addendum — Authoritative Executed Results\nThe original 220-cell course template is preserved above. This addendum reports the reproducible metrics saved by the executed project scripts. It supersedes inconsistent earlier outputs.'))
cell("import json,pandas as pd\nfrom IPython.display import display,Image\nr=json.load(open('outputs/results.json'));display(pd.Series(r['overview']));display(pd.Series(r['splits']))")
nb.cells.append(n.v4.new_markdown_cell('## Baseline Model Comparison'))
cell("display(pd.DataFrame(r['baseline_validation']).sort_values(['recall','f1'],ascending=False))")
nb.cells.append(n.v4.new_markdown_cell('## Hyperparameter Tuning and Validation-only Selection'))
cell("display(pd.DataFrame(r['tuned_validation']).sort_values(['recall','f1'],ascending=False));print(r['selection_rationale'])")
nb.cells.append(n.v4.new_markdown_cell('## Final Untouched Test Evaluation and Feature Drivers'))
cell("display(pd.DataFrame([r['test_metrics']]));display(Image(filename='outputs/charts/final_test_confusion_matrix.png'));display(Image(filename='outputs/charts/feature_importance.png'));display(pd.DataFrame(r['feature_importance']))")
nb.cells.append(n.v4.new_markdown_cell('## Corrected Business Recommendations\nUse tuned ANN alerts as maintenance-priority decision support. It detects 1,339 of 1,440 test faults, while 1,595 false alarms require a remote review/alert-persistence gate before field dispatch. Monitor missed faults, false-alarm burden, lead time and avoided downtime after deployment.'))
n.write(nb,'AIML_Project_1_Low_Code_Notebook.ipynb');print(len(nb.cells))

