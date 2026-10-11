import os,json
os.environ['MPLBACKEND']='Agg';os.environ['MPLCONFIGDIR']='outputs/matplotlib';os.makedirs('outputs/charts',exist_ok=True)
import numpy as np,pandas as pd,matplotlib.pyplot as plt,seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from sklearn.model_selection import RandomizedSearchCV,TimeSeriesSplit
S=42
d=pd.read_csv('wind_turbine_detection.csv');d.timestamp=pd.to_datetime(d.timestamp,format='%m/%d/%Y %H:%M')
over={'records':len(d),'columns':len(d.columns),'turbines':int(d.turbine_id.nunique()),'duplicates':int(d.duplicated().sum()),'missing':d.isna().sum()[lambda x:x.gt(0)].to_dict(),'failure_rate':float(d.failure.mean())}
print(over)
sns.set_theme(style='whitegrid')
fig,ax=plt.subplots(1,2,figsize=(13,4));sns.countplot(data=d,x='failure',ax=ax[0]);ax[0].set_title('Drivetrain failure distribution');rr=d.groupby('turbine_id',as_index=False).failure.mean();sns.barplot(data=rr,x='turbine_id',y='failure',ax=ax[1]);ax[1].tick_params(axis='x',rotation=45);ax[1].set_title('Failure rate by turbine');plt.tight_layout();plt.savefig('outputs/charts/eda_target_turbines.png',dpi=180);plt.close()
fig,ax=plt.subplots(2,2,figsize=(12,8))
for a,c in zip(ax.ravel(),['wind_speed_mps','gearbox_bearing_temp_C','drivetrain_vibration_rms_mmps','oil_particle_count']):sns.boxplot(data=d,x='failure',y=c,showfliers=False,ax=a);a.set_title(c+' by condition')
plt.tight_layout();plt.savefig('outputs/charts/eda_failure_signals.png',dpi=180);plt.close()
cc=['failure','gearbox_oil_temp_C','gearbox_bearing_temp_C','generator_bearing_temp_C','drivetrain_vibration_rms_mmps','vib_fft_gearmesh','oil_particle_count','oil_pressure_bar','prior_fault_count','component_age_days'];plt.figure(figsize=(10,7));sns.heatmap(d[cc].corr(),annot=True,fmt='.2f',cmap='coolwarm',center=0);plt.tight_layout();plt.savefig('outputs/charts/eda_correlation.png',dpi=180);plt.close()
d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
for c,v in {'hour_sin':np.sin(2*np.pi*d.timestamp.dt.hour/24),'hour_cos':np.cos(2*np.pi*d.timestamp.dt.hour/24),'power_utilisation':d.power_output_kW/d.rated_power_kW,'gearbox_temp_rise_C':d.gearbox_bearing_temp_C-d.ambient_temp_C}.items():d[c]=v
n=len(d);i,j=int(.7*n),int(.85*n);tr,va,te=d[:i],d[i:j],d[j:];f=[c for c in d if c not in ['failure','timestamp','turbine_id']];ytr,yv,yte=tr.failure,va.failure,te.failure
im=SimpleImputer(strategy='median');Xtr=pd.DataFrame(im.fit_transform(tr[f]),columns=f);Xv=pd.DataFrame(im.transform(va[f]),columns=f);Xte=pd.DataFrame(im.transform(te[f]),columns=f)
def score(name,m,X,y):
 q=m.predict(X);z=confusion_matrix(y,q,labels=[0,1]);return {'model':name,'accuracy':accuracy_score(y,q),'precision':precision_score(y,q,zero_division=0),'recall':recall_score(y,q,zero_division=0),'f1':f1_score(y,q,zero_division=0),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1])}
mods={'Decision Tree':DecisionTreeClassifier(max_depth=8,min_samples_leaf=25,class_weight='balanced',random_state=S),'Random Forest':RandomForestClassifier(n_estimators=40,max_depth=14,min_samples_leaf=8,class_weight='balanced_subsample',n_jobs=-1,random_state=S),'Gradient Boosting':GradientBoostingClassifier(n_estimators=8,learning_rate=.07,max_depth=3,subsample=.8,random_state=S)}
fit={};base=[]
for name,m in mods.items():
 m.fit(Xtr,ytr,sample_weight=compute_sample_weight('balanced',ytr) if name=='Gradient Boosting' else None);fit[name]=m;base.append(score(name,m,Xv,yv));print(base[-1])
base=pd.DataFrame(base).sort_values(['recall','f1','precision'],ascending=False);base.to_csv('outputs/baseline_validation_metrics.csv',index=False)
spaces={'Decision Tree':{'max_depth':[4,6,8,12],'min_samples_leaf':[10,25,50]},'Random Forest':{'n_estimators':[60,80],'max_depth':[8,12],'min_samples_leaf':[3,8]},'Gradient Boosting':{'n_estimators':[15,20],'learning_rate':[.03,.07],'max_depth':[2,3],'subsample':[.65,.8]}}
names=base.head(2).model.tolist();tuned=[];search={}
for name in names:
 s=RandomizedSearchCV(fit[name],spaces[name],n_iter=1,scoring='recall',cv=TimeSeriesSplit(2),n_jobs=-1,random_state=S);s.fit(Xtr,ytr,**({'sample_weight':compute_sample_weight('balanced',ytr)} if name=='Gradient Boosting' else {}));search[name]=s;q=score(name+' (tuned)',s.best_estimator_,Xv,yv);q['cv_recall']=s.best_score_;q['parameters']=str(s.best_params_);tuned.append(q);print(q)
tuned=pd.DataFrame(tuned);comp=pd.concat([base,tuned],ignore_index=True,sort=False).sort_values(['recall','f1','precision'],ascending=False);comp.to_csv('outputs/model_comparison_validation.csv',index=False)
best=comp.iloc[0].model;obj=search[best.replace(' (tuned)','')].best_estimator_ if '(tuned)' in best else fit[best];final=score(best,obj,Xte,yte);print('FINAL',best,final)
z=[[final['tn'],final['fp']],[final['fn'],final['tp']]];plt.figure(figsize=(4,3));sns.heatmap(z,annot=True,fmt='d',cmap='Blues');plt.tight_layout();plt.savefig('outputs/charts/final_test_confusion_matrix.png',dpi=180);plt.close()
fi=pd.DataFrame({'feature':f,'importance':obj.feature_importances_}).sort_values('importance',ascending=False).head(12);plt.figure(figsize=(8,5));sns.barplot(data=fi,x='importance',y='feature');plt.tight_layout();plt.savefig('outputs/charts/feature_importance.png',dpi=180);plt.close()
json.dump({'overview':over,'splits':{'train':len(tr),'validation':len(va),'test':len(te)},'baseline_validation':base.to_dict('records'),'tuned_validation':tuned.to_dict('records'),'final_model':best,'test_metrics':final,'feature_importance':fi.to_dict('records'),'xgboost_status':'Unavailable: libomp runtime absent; system-level install prohibited outside project.','ann_status':'Unavailable: TensorFlow model did not complete within this execution window.'},open('outputs/results.json','w'),indent=2)
