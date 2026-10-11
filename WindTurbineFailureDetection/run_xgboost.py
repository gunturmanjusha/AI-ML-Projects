import json, numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from xgboost import XGBClassifier
S=42
d=pd.read_csv('wind_turbine_detection.csv');d.timestamp=pd.to_datetime(d.timestamp,format='%m/%d/%Y %H:%M');d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
d['hour_sin']=np.sin(2*np.pi*d.timestamp.dt.hour/24);d['hour_cos']=np.cos(2*np.pi*d.timestamp.dt.hour/24);d['power_utilisation']=d.power_output_kW/d.rated_power_kW;d['gearbox_temp_rise_C']=d.gearbox_bearing_temp_C-d.ambient_temp_C
i,j=int(.7*len(d)),int(.85*len(d));tr,va,te=d[:i],d[i:j],d[j:];f=[x for x in d if x not in ['failure','timestamp','turbine_id']]
im=SimpleImputer(strategy='median');Xtr=pd.DataFrame(im.fit_transform(tr[f]),columns=f);Xv=pd.DataFrame(im.transform(va[f]),columns=f)
def score(X,y):
 p=m.predict_proba(X)[:,1];q=(p>=.5).astype(int);z=confusion_matrix(y,q,labels=[0,1]);return {'model':'XGBoost','accuracy':accuracy_score(y,q),'precision':precision_score(y,q,zero_division=0),'recall':recall_score(y,q,zero_division=0),'f1':f1_score(y,q,zero_division=0),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1])}
m=XGBClassifier(n_estimators=120,max_depth=5,learning_rate=.07,subsample=.8,colsample_bytree=.8,scale_pos_weight=(tr.failure==0).sum()/(tr.failure==1).sum(),random_state=S,n_jobs=4,eval_metric='logloss')
m.fit(Xtr,tr.failure);r=score(Xv,va.failure);json.dump(r,open('outputs/xgboost_baseline_metrics.json','w'),indent=2);print(r)

