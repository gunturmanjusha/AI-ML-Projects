import json,os
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
r=json.load(open('outputs/results.json'));p=Presentation('AIML_Project_1_Low_Code_Presentation_Template.pptx');o='outputs'
def texts(slide):
 return [x for x in slide.shapes if hasattr(x,'text_frame')]
def put(slide,title,body):
 z=texts(slide);z[0].text=title
 if len(z)<2:
  slide.shapes.add_textbox(Inches(.8),Inches(1.6),Inches(11),Inches(3)).text_frame.text=body
  z=texts(slide)
 else:z[1].text=body
 for shp in z[:2]:
  for para in shp.text_frame.paragraphs:
   para.font.size=Pt(20 if shp==z[1] else 30)
def addpic(slide,path,left=7.0,top=1.6,w=5.6):
 if os.path.exists(path):slide.shapes.add_picture(path,Inches(left),Inches(top),width=Inches(w))
def table(slide,rows,cols,data,left,top,w,h):
 sh=slide.shapes.add_table(rows,cols,Inches(left),Inches(top),Inches(w),Inches(h));t=sh.table
 for i,row in enumerate(data):
  for j,v in enumerate(row):
   c=t.cell(i,j);c.text=str(v)
   for para in c.text_frame.paragraphs:para.font.size=Pt(10 if rows>5 else 12);para.alignment=PP_ALIGN.CENTER
   if i==0:
    c.fill.solid();c.fill.fore_color.rgb=RGBColor(16,86,118)
    for x in c.text_frame.paragraphs:x.font.color.rgb=RGBColor(255,255,255)
 return t
z0=texts(p.slides[0]);z0[0].text='Wind Turbine Failure Detection';z0[1].text='Aeolus Renewables | Low-Code Machine Learning Assignment';z0[2].text='11 October 2026'
put(p.slides[1],'Contents / Agenda','Executive summary\nBusiness problem and approach\nEDA and preprocessing\nModel performance and final selection\nRecommendations\nAppendix: data, baselines, tuning and supporting results')
put(p.slides[2],'Executive Summary','Tuned ANN is selected using validation recall (92.49%).\nOn the untouched test period it identifies 1,245 of 1,441 recorded fault states (86.40% recall).\nFalse positives require a staged remote-review workflow before field dispatch.\nUse the model as condition-assessment decision support; it does not prove future-failure lead time.')
put(p.slides[3],'Business Problem Overview and Solution Approach','Objective: classify current recorded drivetrain condition from 10-minute SCADA signals.\nApproach: timestamp-grouped chronological 70/15/15 split; training-only preprocessing; five baselines; time-aware XGBoost tuning and ANN tuning; validation-based selection; one final test evaluation.')
put(p.slides[4],'EDA Results — Data and Fault Pattern','131,760 rows | 15 turbines | 8,784 timestamps | 3.00% failure rate.\nFault and normal observations differ across vibration, gearbox temperature and oil-particle signals.\nTurbine-level failure rates support asset-level prioritization.')
addpic(p.slides[4],'outputs/charts/eda_target_turbines.png',6.5,1.6,5.8)
put(p.slides[5],'Data Preprocessing and Leakage Prevention','Duplicate records: 0.\nMissing values: gearbox oil temperature 645; generator bearing temperature 690; oil pressure 636.\nMedian imputation and ANN scaling fit on training data only.\nEngineered time cycles, power utilisation and temperature-rise features.\nTimestamp groups remain intact across chronological partitions.')
put(p.slides[6],'Model Performance Summary and Final Model Selection','Selection rule: highest validation recall; F1 and precision resolve an exact recall tie.\nTuned ANN recall is 92.49%, exceeding tuned XGBoost at 69.10%.\nThe test set is excluded from candidate selection and threshold choice.')
table(p.slides[6],3,5,[['Model','Recall','F1','Precision','Decision'],['ANN tuned','92.49%','53.54%','37.67%','Selected'],['XGBoost tuned','69.10%','69.34%','69.57%','Alternative'] ],.7,3.3,11.5,1.4)
put(p.slides[7],'APPENDIX','Detailed data background, baseline comparison, tuning methodology and supporting evaluation charts follow.')
put(p.slides[8],'Data Background and Contents','Ten-minute SCADA records from 15 turbines, Jan–Mar 2024.\nInputs cover weather, power, rotational speeds, temperatures, vibration spectra, oil condition, operating history and maintenance context.\nTarget: failure is a recorded condition at the timestamp, not a future event label.')
put(p.slides[9],'Model Building — Baseline Validation Comparison','Five models use the same timestamp-grouped training and validation partitions. Recall emphasizes costly missed drivetrain conditions; precision quantifies field-workload burden.')
b=r['baseline_validation'];data=[['Model','Accuracy','Precision','Recall','F1']]+[[q['model'],f"{q['accuracy']:.1%}",f"{q['precision']:.1%}",f"{q['recall']:.1%}",f"{q['f1']:.1%}"] for q in b];table(p.slides[9],len(data),5,data,.55,3.0,12.0,2.6)
put(p.slides[10],'Model Improvement — Hyperparameter Tuning','XGBoost: six randomized configurations; two timestamp-grouped expanding folds; optimized recall.\nParameter ranges: 80–200 trees, depth 3–6, learning rate 0.02–0.10, subsample/column sample 0.70–1.00, min-child weight 1–5.\nBest CV recall: 48.45%. Holdout validation recall: 69.10%.\nANN: 64/24 hidden units, BatchNorm, dropout 0.30/0.15, Adam and early stopping.')
put(p.slides[11],'Final Model Test Performance','Tuned ANN on untouched test period:\nAccuracy 92.58% | Precision 49.48% | Recall 86.40% | F1 62.93%\nTN 17,058 | FP 1,271 | FN 196 | TP 1,245\n196 missed recorded fault states remain the key operational risk; 1,271 alerts require triage.')
addpic(p.slides[11],'outputs/charts/final_test_confusion_matrix.png',7,2.8,4.2)
put(p.slides[12],'Feature Interpretation and Recommendations','Permutation importance is measured by the validation-recall drop after shuffling each input; it describes association, not causality.\nPrioritize persistent multi-signal alerts. Review vibration, thermal, oil and maintenance context remotely before dispatch. Track missed states, false-alert workload, drift and downtime outcomes after deployment.')
addpic(p.slides[12],'outputs/charts/feature_importance.png',7,2.8,4.5)
# Add three supporting slides using the template blank layout
for title,body,img in [('EDA Supporting Views','Condition-signal distributions and correlation patterns provide operational context for the model.','outputs/charts/eda_failure_signals.png'),('Baseline Recall Comparison','ANN and XGBoost are the two strongest recall baselines; Random Forest trades recall for very high precision.','outputs/charts/baseline_recall.png'),('Operational Limitations','The target is concurrent recorded condition. Validate prospectively before claiming early-warning lead time or financial savings. Monitor data quality and changing failure prevalence.',None)]:
 s=p.slides.add_slide(p.slide_layouts[6]);tx=s.shapes.add_textbox(Inches(.6),Inches(.45),Inches(12),Inches(.65)).text_frame;tx.text=title;tx.paragraphs[0].font.size=Pt(28);tx.paragraphs[0].font.bold=True;bd=s.shapes.add_textbox(Inches(.7),Inches(1.4),Inches(5.6),Inches(4.8)).text_frame;bd.text=body
 for par in bd.paragraphs:par.font.size=Pt(19)
 if img:addpic(s,img,6.7,1.45,5.5)
p.save(o+'/AIML_Project_1_Low_Code_Final_Presentation.pptx')
# matching review PDF
with PdfPages(o+'/AIML_Project_1_Low_Code_Final_Presentation.pdf') as pdf:
 for s in p.slides:
  fig=plt.figure(figsize=(13.333,7.5));plt.axis('off');fig.patch.set_facecolor('white')
  ss=texts(s);title=ss[0].text if ss else '';body='\\n'.join(x.text for x in ss[1:])
  plt.text(.05,.9,title,fontsize=24,color='#105676',weight='bold',transform=fig.transFigure);plt.text(.06,.75,body,fontsize=15,color='#222',va='top',wrap=True,transform=fig.transFigure);pdf.savefig(fig);plt.close(fig)
print('slides',len(p.slides))
