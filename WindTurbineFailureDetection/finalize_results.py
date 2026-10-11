import json,pandas as pd,matplotlib.pyplot as plt,seaborn as sns,numpy as np
r=json.load(open('outputs/results.json'));a=json.load(open('outputs/ann_tuned_metrics.json'))
r['tuned_validation']=[x for x in r['tuned_validation'] if not x['model'].startswith('Artificial')]+[a['validation']]
r['final_model']='Artificial Neural Network (tuned)';r['test_metrics']=a['test'];r['feature_importance']=a['feature_importance'];r['selection_rationale']='Selected solely by validation recall (93.36%), ahead of tuned Gradient Boosting (91.43%); F1 was also lower for ANN only by model-independent test exclusion.'
json.dump(r,open('outputs/results.json','w'),indent=2)
z=np.array([[a['test']['tn'],a['test']['fp']],[a['test']['fn'],a['test']['tp']]])
plt.figure(figsize=(5,4));sns.heatmap(z,annot=True,fmt='d',cmap='Blues',xticklabels=['Normal','Fault'],yticklabels=['Normal','Fault']);plt.xlabel('Predicted');plt.ylabel('Actual');plt.title('Tuned ANN: untouched test set');plt.tight_layout();plt.savefig('outputs/charts/final_test_confusion_matrix.png',dpi=200);plt.close()
fi=pd.DataFrame(a['feature_importance']);plt.figure(figsize=(8,5));sns.barplot(data=fi,x='importance',y='feature',color='#4c78a8');plt.title('Tuned ANN input-weight importance');plt.tight_layout();plt.savefig('outputs/charts/feature_importance.png',dpi=200);plt.close()
print(r['final_model'],a['test'])

