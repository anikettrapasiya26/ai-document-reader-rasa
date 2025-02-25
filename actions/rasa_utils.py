import boto3
from pdfminer.high_level import extract_text
from io import BytesIO
import re
import docx2txt
from boto3 import Session
import string
import random
import uuid
from fpdf import FPDF
import spacy
import os

access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

textract = boto3.client('textract', region_name=os.environ.get("AWS_REGION"), aws_access_key_id = access_key, aws_secret_access_key = secret_key)
s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key= secret_key)
ses = Session(aws_access_key_id=access_key,
              aws_secret_access_key=secret_key,
              region_name=os.environ.get("AWS_REGION"))
client = ses.client('s3')
s3BucketName = os.environ.get("AWS_BUCKET_NAME")

# Text Extraction from pdf and Docx file
def TextExtraction(files):
  try:
    text = ''
    if type(files)== list:
      for file in files:
        if file.endswith('.pdf'):
          documentName = file
          obj = s3.Object(s3BucketName,documentName)
          fs = obj.get()['Body'].read()
          text = extract_text(BytesIO(fs))
          text = re.sub(r'\n+', ' ', text) 
          text = re.sub(r'\s+', ' ', text)
        elif file.endswith(('.docx', '.doc')):
          documentName = file
          obj = s3.Object(s3BucketName,documentName)
          fs = obj.get()['Body'].read()
          text = docx2txt.process(BytesIO(fs))
          text = re.sub(r'\n+', ' ', text) 
          text = re.sub(r'\s+', ' ', text)
    return text
  except Exception as e:
    raise Exception(f'Unable to extract text from "{file}". ErrorMessage : {e}.') 

#Img2pdf OCR CODE
def TextOcr(files, name):
  folder = os.environ.get("AWS_S3_FOLDER")

  dev_userid = re.search(folder/r'(\d+)', name).group(1)
  try:
    text = ''
    if type(files)== list:
      for file in files:
        if file.endswith(('.png', '.jpg', '.jpeg')):
          documentName = file
          response = textract.detect_document_text(
              Document={
                  'S3Object': {
                      'Bucket': s3BucketName,
                      'Name': documentName
                  }
              })
          for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
              text += (item["Text"] + '\n')
      if text == '':
        return 'No text Found in the Image'
      else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_xy(16,9 )
        pdf.set_font('arial', size = 15.0)
        pdf.multi_cell(h=8.0, align='J', w=0, txt=text, border=0)
        filename = str(uuid.uuid4())
        filename = filename+".pdf"
        pdf.output('PDF/'+filename, 'F')
        
        # Upload the PDF file to S3
        file = filename 
        content_type = 'application/pdf'
        s3 = ses.resource('s3')
        key = f'{dev_userid}/Documents/{file}'
        s3.Bucket(s3BucketName).put_object(Key=key, Body=open('PDF/'+file, 'rb'), ContentType=content_type)
        return key
    del key, filename
    
  except Exception as e:
    raise Exception(f'Unable to extract text from "{file}". ErrorMessage : {e}.') 
 
NER = spacy.load("en_core_web_lg")  
def ner(text):
  text1= NER(text)
  entities = 'NER Tags : \n \n'
  DATE = []
  ORG = []
  GPE = []
  PERSON = []
  CARDINAL = []
  WORK_OF_ART = []
  EVENT = []
  LAW = []
  for word in text1.ents:
    if word.label_ == "DATE":
      DATE.append(word.text)
    elif word.label_ == "ORG":
      ORG.append(word.text)
    elif word.label_ == "GPE":
      GPE.append(word.text)
    elif word.label_ == "PERSON":
      PERSON.append(word.text)
    elif word.label_ == "CARDINAL":
      CARDINAL.append(word.text)
    elif word.label_ == "WORK_OF_ART":
      WORK_OF_ART.append(word.text)
    elif word.label_ == "EVENT":
      EVENT.append(word.text)
    elif word.label_ == "LAW":
      LAW.append(word.text)
    else:
      pass
  entities += ' • DATE : ' + ', '.join(DATE) + ' \n • ORG : ' +', '.join(ORG) + ' \n • GPE : ' + ', '.join(GPE) + ' \n • PERSON : ' + ', '.join(PERSON) + ' \n • CARDINAL : ' + ', '.join(CARDINAL) + ' \n • WORK_OF_ART : ' + ', '.join(WORK_OF_ART) + ' \n • EVENT : ' + ', '.join(EVENT) + ' \n • LAW : ' + ', '.join(LAW)
  return entities
  # for word in text1.ents:
  #     entities += (f"• {word.label_:10s} : {word.text}\n")
  