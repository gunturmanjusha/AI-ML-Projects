import json,numpy as np,pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from xgboost import XGBClassifier
S=42;d=pd.read_csv('wind_turbine_detection.csv');d.timestamp=pd.to_datetime(d.timestamp,format='%m/%d/%Y %H:%M');d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
d['hour_sin']=np.sin(2*np.pi*d.timestamp.dt.hour/24);d['hour_cos']=np.cos(2*np.pi*d.timestamp.dt.hour/24);d['dow_sin']=np.sin(2*np.pi*d.timestamp.dt.dayofweek/7);d['dow_cos']=np.cos(2*np.pi*d.timestamp.dt.dayofweek/7);d['power_utilisation']=d.power_output_kW/d.rated_power_kW;d['gearbox_temp_rise_C']=d.gearbox_bearing_temp_C-d.ambient_temp_C;d['generator_temp_rise_C']=d.generator_bearing_temp_C-d.ambient_temp_C
times=d.timestamp.drop_duplicates().sort_values().to_numpy();a,b=int(.7*len(times)),int(.85*len(times));tr=d[d.timestamp.isin(times[:a])];va=d[d.timestamp.isin(times[a:b])];te=d[d.timestamp.isin(times[b:])];f=[c for c in d if c not in ['failure','timestamp','turbine_id']]
im=SimpleImputer(strategy='median');x=im.fit_transform(tr[f]);v=im.transform(va[f]);z=im.transform(te[f])
folds=[(np.arange(0,46110),np.arange(46110,69165)),(np.arange(0,69165),np.arange(69165,92220))]
base=XGBClassifier(scale_pos_weight=(tr.failure==0).sum()/(tr.failure==1).sum(),random_state=S,n_jobs=4,eval_metric='logloss')
grid={'n_estimators':[80,120,160,200],'max_depth':[3,4,5,6],'learning_rate':[.02,.04,.07,.10],'subsample':[.70,.85,1.0],'colsample_bytree':[.70,.85,1.0],'min_child_weight':[1,3,5]}
s=RandomizedSearchCV(base,grid,n_iter=6,scoring='recall',cv=folds,n_jobs=1,random_state=S,refit=True,return_train_score=False);s.fit(x,tr.failure);m=s.best_estimator_
def score(X,y,split):
 p=m.predict_proba(X)[:,1];q=(p>=.5).astype(int);c=confusion_matrix(y,q,labels=[0,1]);return {'model':'XGBoost (tuned)','split':split,'accuracy':float(accuracy_score(y,q)),'precision':float(precision_score(y,q,zero_division=0)),'recall':float(recall_score(y,q)),'f1':float(f1_score(y,q)),'tn':int(c[0,0]),'fp':int(c[0,1]),'fn':int(c[1,0]),'tp':int(c[1,1])}
out={'search':{'method':'RandomizedSearchCV','n_iter':6,'cv':'two timestamp-grouped expanding-window folds: first 50%→next 25%, then first 75%→final 25% of training history','scoring':'recall','parameter_ranges':grid,'best_parameters':{k:(int(q) if isinstance(q,np.integer) else float(q) if isinstance(q,np.floating) else q) for k,q in s.best_params_.items()},'best_cv_recall':float(s.best_score_)},'validation':score(v,va.failure,'validation'),'test_if_selected':score(z,te.failure,'test')};json.dump(out,open('outputs/xgboost_tuning.json','w'),indent=2);print(json.dumps(out,indent=2))

