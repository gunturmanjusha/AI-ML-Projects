import json,pandas as pd
p='outputs/results.json';r=json.load(open(p));d=pd.read_csv('wind_turbine_detection.csv');d['timestamp']=pd.to_datetime(d['timestamp'],format='%m/%d/%Y %H:%M');times=sorted(d.timestamp.unique());a,b=int(.7*len(times)),int(.85*len(times))
r['split_metadata']={}
for name,ts in [('train',times[:a]),('validation',times[a:b]),('test',times[b:])]:
 q=d[d.timestamp.isin(ts)];r['split_metadata'][name]={'rows':int(len(q)),'timestamps':int(q.timestamp.nunique()),'start':str(q.timestamp.min()),'end':str(q.timestamp.max()),'failure_count':int(q.failure.sum()),'failure_rate':float(q.failure.mean())}
json.dump(r,open(p,'w'),indent=2,allow_nan=False);print(json.dumps(r['split_metadata'],indent=2))

