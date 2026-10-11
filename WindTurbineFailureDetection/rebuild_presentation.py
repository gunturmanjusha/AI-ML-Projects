import json,os
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
r=json.load(open('outputs/results.json'));o='outputs'
prs=Presentation('AIML_Project_1_Low_Code_Presentation_Template.pptx')
while len(prs.slides):prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])
slides=[
('Wind Turbine Failure Detection',['Aeolus Renewables','Low-Code machine learning assignment','Drivetrain early-warning decision support']),
('Executive Summary',[f"Selected model: {r['final_model']}",f"Untouched test recall: {r['test_metrics']['recall']:.2%} | F1: {r['test_metrics']['f1']:.2%}",f"Detected {r['test_metrics']['tp']} of {r['test_metrics']['tp']+r['test_metrics']['fn']} failures",'Use staged review to manage false alarms']),
('Business Problem',['Detect drivetrain faults from 10-minute SCADA data','Missed failures create downtime and repair risk','Primary decision metric: recall; precision limits technician burden']),
('Data and EDA',[f"{r['overview']['records']:,} records across {r['overview']['turbines']} turbines",f"Failure prevalence: {r['overview']['failure_rate']:.2%}",'Thermal, vibration and oil-condition readings differ by fault status','Turbine rates support asset-level maintenance planning'],'outputs/charts/eda_failure_signals.png'),
('Data Quality',['Duplicate rows: 0','Missing readings: 645 gearbox-oil temperatures; 690 generator-bearing temperatures; 636 oil-pressure readings','Training-median imputation avoids leakage','Missingness is retained in the data-quality narrative']),
('Preprocessing',['Chronological 70% / 15% / 15% train-validation-test split','Timestamp and turbine ID excluded from model input','Engineered hour cycles, power utilisation and gearbox temperature rise','Scaling fitted only on training rows for ANN']),
('Baseline Models',['Decision Tree: recall 47.93%, F1 35.50%','Random Forest: recall 18.86%, F1 30.34%','Gradient Boosting: recall 38.31%, F1 48.63%','XGBoost: recall 59.67%, F1 67.10%','ANN: recall 71.41%, F1 56.02%']),
('Tuning Approach',['Two strongest recall baselines: Gradient Boosting and ANN','Gradient Boosting: time-ordered validation search','ANN: 64/24 hidden units, BatchNorm, dropout, Adam and early stopping','No test data used for model selection']),
('Tuned Validation Results',['Tuned Gradient Boosting: recall 91.43%, F1 74.60%','Tuned ANN: recall 93.36%, F1 67.04%','ANN selected because recall is the stated priority and is higher','This corrects the prior inconsistent selection claim']),
('Final Model Test Result',[f"Accuracy {r['test_metrics']['accuracy']:.2%} | Precision {r['test_metrics']['precision']:.2%}",f"Recall {r['test_metrics']['recall']:.2%} | F1 {r['test_metrics']['f1']:.2%}",f"TN {r['test_metrics']['tn']} | FP {r['test_metrics']['fp']} | FN {r['test_metrics']['fn']} | TP {r['test_metrics']['tp']}",f"Matrix total {sum(r['test_metrics'][k] for k in ['tn','fp','fn','tp']):,} matches test size {r['splits']['test']:,}"],'outputs/charts/final_test_confusion_matrix.png'),
('Feature Drivers',['ANN input-weight importance highlights condition-monitoring variables','Use top vibration, oil, temperature and loading signals as inspection prompts','Importance is directional support; it does not prove causation'],'outputs/charts/feature_importance.png'),
('Operational Recommendations',['Prioritize persistent high-risk alerts for remote review','Dispatch technicians when signals persist or multiple condition indicators agree','Track missed faults, false alarms, lead time, downtime avoided and workload','Recalibrate thresholds after field feedback']),
('Limitations and Next Steps',['This is a retrospective proof of concept','Test period is chronologically later, reducing temporal leakage','Validate on additional farms and maintenance work-order outcomes','Do not use model output as an automatic shutdown command'])]
def add(title,bullets,img=None):
 s=prs.slides.add_slide(prs.slide_layouts[6]);fill=s.background.fill;fill.solid();fill.fore_color.rgb=RGBColor(11,28,50)
 h=s.shapes.add_textbox(Inches(.65),Inches(.4),Inches(12),Inches(.6)).text_frame;h.text=title;h.paragraphs[0].font.size=Pt(29);h.paragraphs[0].font.bold=True;h.paragraphs[0].font.color.rgb=RGBColor(75,205,196)
 t=s.shapes.add_textbox(Inches(.8),Inches(1.3),Inches(6 if img else 11.4),Inches(5.7)).text_frame;t.clear()
 for i,x in enumerate(bullets):
  p=t.paragraphs[0] if i==0 else t.add_paragraph();p.text=x;p.level=0;p.font.size=Pt(18);p.font.color.rgb=RGBColor(242,245,248);p.space_after=Pt(16)
 if img:s.shapes.add_picture(img,Inches(7),Inches(1.45),width=Inches(5.5))
for x in slides:add(*x)
prs.save(o+'/AIML_Project_1_Low_Code_Final_Presentation.pptx')
with PdfPages(o+'/AIML_Project_1_Low_Code_Final_Presentation.pdf') as pdf:
 for title,bullets,*im in slides:
  fig=plt.figure(figsize=(13.333,7.5));fig.patch.set_facecolor('#0b1c32');plt.axis('off');plt.text(.05,.9,title,fontsize=25,color='#4bcdc4',weight='bold',transform=fig.transFigure)
  for i,x in enumerate(bullets):plt.text(.08,.76-i*.095,'• '+x,fontsize=16,color='white',transform=fig.transFigure)
  if im:ax=fig.add_axes([.57,.08,.37,.48]);ax.imshow(plt.imread(im[0]));ax.axis('off')
  pdf.savefig(fig);plt.close(fig)
print(len(slides))
