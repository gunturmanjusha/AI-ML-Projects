import os,json
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import numpy as np,pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.callbacks import EarlyStopping
S=42;np.random.seed(S);tf.keras.utils.set_random_seed(S)
d=pd.read_csv('wind_turbine_detection.csv');d.timestamp=pd.to_datetime(d.timestamp,format='%m/%d/%Y %H:%M');d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
d['hour_sin']=np.sin(2*np.pi*d.timestamp.dt.hour/24);d['hour_cos']=np.cos(2*np.pi*d.timestamp.dt.hour/24);d['power_utilisation']=d.power_output_kW/d.rated_power_kW;d['gearbox_temp_rise_C']=d.gearbox_bearing_temp_C-d.ambient_temp_C
i,j=int(.7*len(d)),int(.85*len(d));tr,va,te=d[:i],d[i:j],d[j:];f=[x for x in d if x not in ['failure','timestamp','turbine_id']]
im=SimpleImputer(strategy='median');Xtr=im.fit_transform(tr[f]);Xv=im.transform(va[f]);Xte=im.transform(te[f]);sc=StandardScaler();Xtr=sc.fit_transform(Xtr);Xv=sc.transform(Xv);Xte=sc.transform(Xte)
def score(X,y):
 p=model.predict(X,verbose=0).ravel();q=(p>=.5).astype(int);z=confusion_matrix(y,q,labels=[0,1]);return {'model':'Artificial Neural Network','accuracy':accuracy_score(y,q),'precision':precision_score(y,q,zero_division=0),'recall':recall_score(y,q,zero_division=0),'f1':f1_score(y,q,zero_division=0),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1])}
model=Sequential([Dense(48,activation='relu',input_shape=(Xtr.shape[1],)),Dropout(.2),Dense(16,activation='relu'),Dense(1,activation='sigmoid')]);model.compile(optimizer='adam',loss='binary_crossentropy')
model.fit(Xtr,tr.failure,validation_data=(Xv,va.failure),epochs=12,batch_size=256,class_weight={0:1,1:float((tr.failure==0).sum()/(tr.failure==1).sum())},callbacks=[EarlyStopping(monitor='val_loss',patience=3,restore_best_weights=True)],verbose=0)
r={'validation':score(Xv,va.failure),'test':score(Xte,te.failure),'split_sizes':{'train':len(tr),'validation':len(va),'test':len(te)}};json.dump(r,open('outputs/ann_metrics.json','w'),indent=2);print(r)

