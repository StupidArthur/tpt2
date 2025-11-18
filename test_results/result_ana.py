# encoding: utf-8


import os
import json
from data_process.formatter import conversation_analyze


path_saas = os.path.join(os.path.dirname(__file__), "ds_x86")
path_x86 = os.path.join(os.path.dirname(__file__), "ds_x86_1")

files_saas = os.listdir(path_saas)
files_x86 = os.listdir(path_x86)

print(len(files_saas), len(files_x86))

for file in files_saas:
    try:
        with open(os.path.join(path_saas, file), "r", encoding='utf-8') as f:
            raw_saas = json.load(f)
            data_saas = conversation_analyze(raw_saas)
        with open(os.path.join(path_x86, file), "r", encoding='utf-8') as f:
            raw_x86 = json.load(f)
            data_x86 = conversation_analyze(raw_x86)
        if data_saas.workflow != data_x86.workflow:
            print(file, 'diff')
    except Exception as e:
        print(file, e)
