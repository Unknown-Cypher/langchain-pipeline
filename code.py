
from dotenv import load_dotenv
import openai
from llama_index import SimpleDirectoryReader
from llama_index import ServiceContext
import os
from llama_index.indices.document_summary import DocumentSummaryIndex
from llama_index.llms import OpenAI
from llama_index import GPTVectorStoreIndex
import getpass

#unpacks zip files
import shutil
from zipfile import ZipFile

load_dotenv()

path = os.environ["INPUT_PATH"]
dest = os.environ["OUTPUT_PATH"]
openai.api_key = os.environ["OPENAI_API_KEY"]

temp = 'temp'
data = 'data'
file_list = []
os.mkdir(data)
for file in os.listdir(path):
  if file.split('.')[-1] == 'zip':
    with ZipFile(os.path.join(path,file), 'r') as zObject:
      zObject.extractall(path=temp)

for root, dirs, files in os.walk(temp):
  for file1 in files :
    if '.'.join(file1.split('.')[:-1]) not in file_list:
      os.rename(os.path.join(root,file1), os.path.join(data,file1))
      file_list.append('.'.join(file1.split('.')[:-1]))

shutil.rmtree(temp,ignore_errors=True)
print('--------unzip-----------------------------')

# converts excel to csv
import pandas as pd
for file in os.listdir(path):
  if file.split('.')[-1] == 'xlsx' and '.'.join(file.split('.')[:-1]) not in file_list:
    file_name = os.path.join(path,file)
    df = pd.read_excel (file_name ,sheet_name = None)
    sheets = df.keys()
    for i,sheet_name in enumerate(sheets):
      df[sheet_name].to_csv('.'.join(os.path.join(data,file).split('.')[:-1])+ '[%s].csv' %sheet_name, index=False,header=True)
      file_list.append('.'.join(file.split('.')[:-1]))
print('--------csv-----------------------------')
#Removing unusable documents
extensions = ['txt', 'docx', 'pdf', 'pptx', 'csv']
for file in os.listdir(path) :
  if file.split('.')[-1] in extensions and '.'.join(file.split('.')[:-1]) not in file_list:
    shutil.copy2(os.path.join(path,file),os.path.join(data,file))
    file_list.append('.'.join(file.split('.')[:-1]))
print('--------loaded document-----------------------------')
# shutil.rmtree('index')

documents = SimpleDirectoryReader(data).load_data()
shutil.rmtree(data)
print('--------documented-----------------------------')

if "OPENAI_API_KEY" not in os.environ:
  openai.api_key = getpass.getpass("Enter your OpenAI API key: ")
chatgpt = OpenAI(temperature=0.5, model="gpt-3.5-turbo")
service_context = ServiceContext.from_defaults(chunk_size=1000,llm=chatgpt)
index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
index.storage_context.persist(dest)

