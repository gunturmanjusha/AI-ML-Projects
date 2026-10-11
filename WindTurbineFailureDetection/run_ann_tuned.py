import os,json,numpy as np,pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense,Dropout,BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
S=42;np.random.seed(S);tf.keras.utils.set_random_seed(S)
d=pd.read_csv('wind_turbine_detection.csv');d.timestamp=pd.to_datetime(d.timestamp,format='%m/%d/%Y %H:%M');d=d.sort_values(['timestamp','turbine_id']).reset_index(drop=True)
d['hour_sin']=np.sin(2*np.pi*d.timestamp.dt.hour/24);d['hour_cos']=np.cos(2*np.pi*d.timestamp.dt.hour/24);d['power_utilisation']=d.power_output_kW/d.rated_power_kW;d['gearbox_temp_rise_C']=d.gearbox_bearing_temp_C-d.ambient_temp_C
i,j=int(.7*len(d)),int(.85*len(d));tr,va,te=d[:i],d[i:j],d[j:];f=[x for x in d if x not in ['failure','timestamp','turbine_id']]
im=SimpleImputer(strategy='median');a=im.fit_transform(tr[f]);b=im.transform(va[f]);c=im.transform(te[f]);sc=StandardScaler();a=sc.fit_transform(a);b=sc.transform(b);c=sc.transform(c)
m=Sequential([Dense(64,activation='relu',input_shape=(a.shape[1],)),BatchNormalization(),Dropout(.3),Dense(24,activation='relu'),Dropout(.15),Dense(1,activation='sigmoid')]);m.compile(optimizer='adam',loss='binary_crossentropy')
m.fit(a,tr.failure,validation_data=(b,va.failure),epochs=25,batch_size=256,class_weight={0:1,1:float((tr.failure==0).sum()/(tr.failure==1).sum())},callbacks=[EarlyStopping(monitor='val_loss',patience=4,restore_best_weights=True)],verbose=0)
p=m.predict(b,verbose=0).ravel();q=(p>=.5).astype(int);z=confusion_matrix(va.failure,q,labels=[0,1]);r={'model':'Artificial Neural Network (tuned)','accuracy':accuracy_score(va.failure,q),'precision':precision_score(va.failure,q,zero_division=0),'recall':recall_score(va.failure,q,zero_division=0),'f1':f1_score(va.failure,q,zero_division=0),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1]),'parameters':'64/24 ReLU layers, BatchNorm, dropout 0.30/0.15, Adam, early stopping'}
p=m.predict(c,verbose=0).ravel();q=(p>=.5).astype(int);z=confusion_matrix(te.failure,q,labels=[0,1]);test={'model':'Artificial Neural Network (tuned)','accuracy':accuracy_score(te.failure,q),'precision':precision_score(te.failure,q,zero_division=0),'recall':recall_score(te.failure,q,zero_division=0),'f1':f1_score(te.failure,q,zero_division=0),'tn':int(z[0,0]),'fp':int(z[0,1]),'fn':int(z[1,0]),'tp':int(z[1,1])}
fi=pd.DataFrame({'feature':f,'importance':np.abs(m.layers[0].get_weights()[0]).mean(axis=1)}).sort_values('importance',ascending=False).head(12)
json.dump({'validation':r,'test':test,'feature_importance':fi.to_dict('records')},open('outputs/ann_tuned_metrics.json','w'),indent=2);print({'validation':r,'test':test})
