import json,pandas as pd
r=json.load(open('outputs/results.json'));x=json.load(open('outputs/xgboost_tuning.json'))
r['tuned_validation']=[q for q in r['tuned_validation'] if not q['model'].startswith('XGBoost')]+[x['validation']]
r['tuning']={'xgboost':x['search'],'ann':{'method':'architecture/regularization tuning with early stopping on validation loss','parameters':r['final_hyperparameters']}}
r['selection_rule']='Select highest validation recall; use F1 then precision only for a recall tie. Test metrics do not participate in selection.'
r['final_model']='Artificial Neural Network (tuned)'
json.dump(r,open('outputs/results.json','w'),indent=2,allow_nan=False)
pd.DataFrame(r['baseline_validation']).to_csv('outputs/baseline_validation_metrics.csv',index=False)
pd.DataFrame(r['tuned_validation']).to_csv('outputs/tuned_validation_metrics.csv',index=False)
print(pd.DataFrame(r['tuned_validation'])[['model','recall','f1','precision']])

