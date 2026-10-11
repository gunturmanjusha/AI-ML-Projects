import os,json,random
os.environ['MPLBACKEND']='Agg';os.environ['TF_CPP_MIN_LOG_LEVEL']='2';os.makedirs('outputs/charts',exist_ok=True)
import numpy as np,pandas as pd,matplotlib.pyplot as plt,seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from sklearn.model_selection import RandomizedSearchCV,TimeSeriesSplit
from sklearn.inspection import permutation_importance
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,Dense,Dropout,BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
S=42;random.seed(S);np.random.seed(S);tf.keras.utils.set_random_seed(S);sns.set_theme(style='whitegrid')
d=pd.read_csv('wind_turbine_detection.csv');d['timestamp']=pd.to_datetime(d['timestamp'],format='%m/%d/%Y %H:%M');d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
overview={'records':len(d),'columns':len(d.columns),'turbines':int(d.turbine_id.nunique()),'date_start':str(d.timestamp.min()),'date_end':str(d.timestamp.max()),'duplicates':int(d.duplicated().sum()),'missing':{k:int(v) for k,v in d.isna().sum()[lambda x:x.gt(0)].items()},'failure_rate':float(d.failure.mean())}
d['hour_sin']=np.sin(2*np.pi*d.timestamp.dt.hour/24);d['hour_cos']=np.cos(2*np.pi*d.timestamp.dt.hour/24);d['dow_sin']=np.sin(2*np.pi*d.timestamp.dt.dayofweek/7);d['dow_cos']=np.cos(2*np.pi*d.timestamp.dt.dayofweek/7);d['power_utilisation']=d.power_output_kW/d.rated_power_kW;d['gearbox_temp_rise_C']=d.gearbox_bearing_temp_C-d.ambient_temp_C;d['generator_temp_rise_C']=d.generator_bearing_temp_C-d.ambient_temp_C
times=d['timestamp'].drop_duplicates().sort_values().to_numpy();a,b=int(.70*len(times)),int(.85*len(times));tr=d[d.timestamp.isin(times[:a])].copy();va=d[d.timestamp.isin(times[a:b])].copy();te=d[d.timestamp.isin(times[b:])].copy();features=[c for c in d.columns if c not in ['failure','timestamp','turbine_id']]
imp=SimpleImputer(strategy='median');Xtr=pd.DataFrame(imp.fit_transform(tr[features]),columns=features);Xv=pd.DataFrame(imp.transform(va[features]),columns=features);Xte=pd.DataFrame(imp.transform(te[features]),columns=features);sc=StandardScaler();Atr=sc.fit_transform(Xtr);Av=sc.transform(Xv);Ate=sc.transform(Xte)
def metrics(name,model,X,y,split='validation'):
 p=model.predict(X,verbose=0).ravel() if hasattr(model,'layers') else model.predict_proba(X)[:,1];q=(p>=.5).astype(int);z=confusion_matrix(y,q,labels=[0,1]);return {'model':name,'split':split,'accuracy':float(accuracy_score(y,q)),'precision':float(precision_score(y,q,zero_division=0)),'recall':float(recall_score(y,q,zero_division=0)),'f1':float(f1_score(y,q,zero_division=0)),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1])}
models={'Decision Tree':DecisionTreeClassifier(max_depth=8,min_samples_leaf=25,class_weight='balanced',random_state=S),'Random Forest':RandomForestClassifier(n_estimators=30,max_depth=14,min_samples_leaf=8,class_weight='balanced_subsample',n_jobs=4,random_state=S),'Gradient Boosting':GradientBoostingClassifier(n_estimators=10,learning_rate=.1,max_depth=3,random_state=S),'XGBoost':XGBClassifier(n_estimators=80,max_depth=5,learning_rate=.07,subsample=.8,colsample_bytree=.8,scale_pos_weight=(tr.failure==0).sum()/(tr.failure==1).sum(),random_state=S,n_jobs=4,eval_metric='logloss')}
base=[];fit={}
for name,m in models.items():m.fit(Xtr,tr.failure);fit[name]=m;base.append(metrics(name,m,Xv,va.failure))
def make_ann(tuned=False):
 m=Sequential([Input(shape=(Atr.shape[1],)),Dense(64 if tuned else 48,activation='relu')])
 if tuned:m.add(BatchNormalization());m.add(Dropout(.30));m.add(Dense(24,activation='relu'));m.add(Dropout(.15))
 else:m.add(Dropout(.20));m.add(Dense(16,activation='relu'))
 m.add(Dense(1,activation='sigmoid'));m.compile(optimizer='adam',loss='binary_crossentropy');return m
cw={0:1,1:float((tr.failure==0).sum()/(tr.failure==1).sum())}
ann=make_ann();ann.fit(Atr,tr.failure,validation_data=(Av,va.failure),epochs=8,batch_size=256,class_weight=cw,callbacks=[EarlyStopping(monitor='val_loss',patience=2,restore_best_weights=True)],verbose=0);base.append(metrics('Artificial Neural Network',ann,Av,va.failure))
# Timestamp-grouped forward validation folds for XGBoost tuning
folds=[(np.arange(0,int(.50*len(tr))),np.arange(int(.50*len(tr)),int(.75*len(tr)))),(np.arange(0,int(.75*len(tr))),np.arange(int(.75*len(tr)),len(tr)))]
xgb_grid={'n_estimators':[80,120,180],'max_depth':[3,4,5],'learning_rate':[.03,.07,.12],'subsample':[.7,.85,1.0],'colsample_bytree':[.7,.85,1.0]}
search=RandomizedSearchCV(models['XGBoost'],xgb_grid,n_iter=1,scoring='recall',cv=folds,n_jobs=1,random_state=S,refit=True);search.fit(Xtr,tr.failure);tx=search.best_estimator_;xgb_tuned=metrics('XGBoost (tuned)',tx,Xv,va.failure);xgb_tuned['parameters']={k:(int(v) if isinstance(v,np.integer) else float(v) if isinstance(v,np.floating) else v) for k,v in search.best_params_.items()};xgb_tuned['cv_recall']=float(search.best_score_)
tann=make_ann(True);tann.fit(Atr,tr.failure,validation_data=(Av,va.failure),epochs=15,batch_size=256,class_weight=cw,callbacks=[EarlyStopping(monitor='val_loss',patience=3,restore_best_weights=True)],verbose=0);ann_tuned=metrics('Artificial Neural Network (tuned)',tann,Av,va.failure);ann_tuned['parameters']={'layers':[64,24,1],'dropout':[.30,.15],'batch_normalization':True,'optimizer':'adam','early_stopping':True}
tuned=[xgb_tuned,ann_tuned];winner=max(tuned,key=lambda x:(x['recall'],x['f1'],x['precision']));final_model=tann if winner['model'].startswith('Artificial') else tx;finalX=Ate if winner['model'].startswith('Artificial') else Xte;test=metrics(winner['model'],final_model,finalX,te.failure,split='test')
if winner['model'].startswith('Artificial'):
 rng=np.random.default_rng(S);sample_idx=rng.choice(len(Av),size=min(5000,len(Av)),replace=False);Av_pi=Av[sample_idx];yv_pi=va.failure.iloc[sample_idx];base_recall=recall_score(yv_pi,(final_model.predict(Av_pi,verbose=0).ravel()>=.5).astype(int));vals=[]
 for k in range(Av.shape[1]):
  drops=[]
  for _ in range(1):
   q=Av_pi.copy();q[:,k]=rng.permutation(q[:,k]);drops.append(base_recall-recall_score(yv_pi,(final_model.predict(q,verbose=0).ravel()>=.5).astype(int)))
  vals.append(np.mean(drops))
 fi=pd.DataFrame({'feature':features,'importance':vals}).sort_values('importance',ascending=False).head(12)
else:
 pi=permutation_importance(final_model,Xv,va.failure,n_repeats=3,scoring='recall',random_state=S,n_jobs=1);fi=pd.DataFrame({'feature':features,'importance':pi.importances_mean}).sort_values('importance',ascending=False).head(12)
for row,title,path in [(base,'Baseline validation recall','outputs/charts/baseline_recall.png')]:
 q=pd.DataFrame(row);plt.figure(figsize=(9,4));sns.barplot(data=q.sort_values('recall',ascending=False),x='recall',y='model',color='#4c78a8');plt.xlim(0,1);plt.title(title);plt.tight_layout();plt.savefig(path,dpi=220);plt.close()
z=np.array([[test['tn'],test['fp']],[test['fn'],test['tp']]]);plt.figure(figsize=(5,4));sns.heatmap(z,annot=True,fmt='d',cmap='Blues',xticklabels=['Normal','Fault'],yticklabels=['Normal','Fault']);plt.xlabel('Predicted');plt.ylabel('Actual');plt.title(winner['model']+' — test');plt.tight_layout();plt.savefig('outputs/charts/final_test_confusion_matrix.png',dpi=220);plt.close()
plt.figure(figsize=(8,5));sns.barplot(data=fi,x='importance',y='feature',color='#4c78a8');plt.title('Permutation importance on validation recall');plt.tight_layout();plt.savefig('outputs/charts/feature_importance.png',dpi=220);plt.close()
res={'overview':overview,'features':features,'split_sizes':{'train':len(tr),'validation':len(va),'test':len(te)},'preprocessing':{'imputation':'median fitted on training split only','scaling':'StandardScaler fitted on training split only for ANN','imbalance':'class weight for ANN; class weights/scale_pos_weight where supported','split':'chronological 70/15/15 by timestamp with all turbines at a timestamp kept together'},'baseline_validation':base,'tuned_validation':tuned,'selection_rule':'Select highest validation recall; break ties with F1 then precision. Test set is excluded from tuning and selection.','final_model':winner['model'],'final_hyperparameters':winner.get('parameters',{}),'final_test':test,'feature_importance_method':'Permutation importance on validation data, scored by recall; associations are not causal.','feature_importance':fi.to_dict('records')};json.dump(res,open('outputs/results.json','w'),indent=2,allow_nan=False);pd.DataFrame(base).to_csv('outputs/baseline_validation_metrics.csv',index=False);pd.DataFrame(tuned).to_csv('outputs/tuned_validation_metrics.csv',index=False);print(json.dumps({'baseline':base,'tuned':tuned,'winner':winner,'test':test},indent=2))
