import fitz
from PIL import Image,ImageDraw
doc=fitz.open('outputs/AIML_Project_1_Low_Code_Final_Presentation.pdf');print('pages',len(doc))
ims=[]
for i,p in enumerate(doc):
 pix=p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(f'/private/tmp/wind_slide_{i+1}.png');ims.append(im)
for g in range(4):
 subset=ims[g*4:(g+1)*4];cw,ch=600,338;sheet=Image.new('RGB',(cw*2,ch*2),'white')
 for k,im in enumerate(subset):
  q=im.copy();q.thumbnail((cw,ch));sheet.paste(q,((k%2)*cw,(k//2)*ch))
 sheet.save(f'/private/tmp/wind_contact_{g+1}.png')

