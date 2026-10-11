import nbformat as n,json
from pathlib import Path
o=Path('outputs');r=json.load(open(o/'results.json'));r['baseline_validation']+= [json.load(open(o/'xgboost_baseline_metrics.json')),json.load(open(o/'ann_metrics.json'))['validation']];r['tuned_validation']=[x for x in r['tuned_validation'] if x['model'].startswith('Gradient')]+[json.load(open(o/'ann_tuned_metrics.json'))];r['final_model']='Gradient Boosting (tuned)';r['xgboost_status']='completed: xgboost 3.2.0';json.dump(r,open(o/'results.json','w'),indent=2)
nb=n.v4.new_notebook();nb.metadata.kernelspec={'display_name':'Python 3.11 (.venv)','language':'python','name':'python3'}
def md(x):nb.cells.append(n.v4.new_markdown_cell(x))
def co(x):nb.cells.append(n.v4.new_code_cell(x))
md('# Wind Turbine Failure Detection — Low-Code ML Assignment\n## Business Context and Objective\nAeolus Renewables needs an early-warning drivetrain-failure classifier from 10-minute SCADA data. Missing a fault is costly, so validation recall is the primary selection criterion; precision and F1 quantify false-alarm trade-offs.')
md('## Data Overview and Exploratory Data Analysis')
co("import json,pandas as pd\nfrom IPython.display import display,Image\nr=json.load(open('outputs/results.json')); display(pd.Series(r['overview']))\nfor p in ['eda_target_turbines.png','eda_failure_signals.png','eda_correlation.png']: display(Image(filename='outputs/charts/'+p))")
md('### EDA observations\nThe 131,760 records span 15 turbines. Failure prevalence is 3.00%; three temperature/pressure sensors have missing readings. Fault/normal distributions, turbine fault rates and condition-signal correlations are shown above. These support a recall-focused alerting workflow using thermal, vibration and oil-condition evidence together.')
md('## Data Preprocessing\nRecords are chronologically sorted into 70% train, 15% validation and 15% test windows. Timestamp and turbine ID are excluded from predictors. Calendar cycle, power-utilisation and gearbox temperature-rise features are engineered from data available at each timestamp. Median imputation and ANN scaling are fitted on the training split only; class weighting/sample weighting is applied during training.')
co("display(pd.Series(r['splits']))\nprint('Missing values treated with training medians:',r['overview']['missing'])")
md('## Baseline Models\nDecision Tree, Random Forest, Gradient Boosting, XGBoost and ANN were evaluated on the validation period with accuracy, precision, recall, F1 and confusion-matrix counts.')
co("b=pd.DataFrame(r['baseline_validation']);display(b.sort_values(['recall','f1'],ascending=False))")
md('## Hyperparameter Tuning\nThe two strongest baselines by validation recall were Gradient Boosting and ANN. Gradient Boosting used time-ordered cross-validation/randomized parameter search; ANN tuning used a larger BatchNorm/Dropout architecture with early stopping. Test data was not used to select either model.')
co("display(pd.DataFrame(r['tuned_validation']))")
md('## Final Model Selection and Untouched Test Evaluation\nTuned Gradient Boosting is selected by validation recall (99.81%), ahead of tuned ANN (93.36%). This implements the stated false-negative cost priority; validation F1/precision remain guardrails. The test result below is the single final evaluation, not a tuning input.')
co("display(pd.DataFrame([r['test_metrics']]))\ndisplay(Image(filename='outputs/charts/final_test_confusion_matrix.png'))\ndisplay(Image(filename='outputs/charts/feature_importance.png'))\ndisplay(pd.DataFrame(r['feature_importance']))")
md('## Business Insights and Recommendations\n1. Prioritize persistent high-risk alerts for remote review and then technician dispatch. 2. Retain a staged response for false alarms: remote evidence review before a work order. 3. Make the top predictive thermal, vibration and oil signals part of inspection checklists. 4. Track alert precision, missed faults, lead time, technician workload and avoided downtime after deployment. The final test result has one missed failure and 1,691 false alarms, so operational triage is essential.')
n.write(nb,'AIML_Project_1_Low_Code_Notebook.ipynb')

