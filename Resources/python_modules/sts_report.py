# -*- coding: utf-8 -*-
"""sts_report.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zlgjJVmCuZO-DGG86JjTUVs41M-RSUa9
"""

# Import the dependecies
import requests
import pandas as pd
import json
import numpy as np
from requests.structures import CaseInsensitiveDict
import time
import subprocess
import re
import fnmatch
import csv
from google.colab import files
from google.colab import drive
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_reports(links,num_reports,first,last):
    results=[]
    total_reports = 0
    for i in range(first,last):
        url = links[i]
        try:
            response = requests.get(url)
            raw_data = response.json()["results"]  
            results.extend(raw_data)
            total_reports = total_reports + len(raw_data)
            print(f"Qty of reports received : {total_reports} Qty of reports left {num_reports - total_reports}....")
        except Exception as err:
            print(type(err))
            print(err)
        time.sleep(4)
    return results

def clean_reports(reports,DRUGNAME):
  def install(name):
    subprocess.call(['pip', 'install', name])

  install('flatten_json')

  from flatten_json import flatten
  
  # Completely flatten the json data into a dictionary
  reports_flattened = [flatten(d) for d in reports]
  
  print(f'number of reports flattended {len(reports_flattened)}')
  
  # define patterns to remove non-relevant fields
  patterns = ['patient_reaction_[0-9]*_reactionoutcome',
  'safetyreportversion',
  'receivedateformat',
  'receivedate',
  'transmissiondateformat',
  'primarysource_reportercountry',
  'patient_patientonsetageunit',
  'patient_drug_[0-9]*_drugauthorizationnumb',
  'patient_drug_[0-9]*_drugdosagetext',
  'patient_reaction_[0-9]*_reactionmeddraversionpt',
  'patient_drug_[0-9]*_drugcumulativedosagenumb',
  'patient_drug_[0-9]*_drugintervaldosagedefinition',
  'patient_drug_[0-9]*_drugseparatedosagenumb',
  'patient_drug_[0-9]*_drugintervaldosageunitnumb',
  'patient_drug_[0-9]*_drugintervaldosagedefinition',
  'patient_drug_[0-9]*_drugcumulativedosageunit',
  'patient_drug_[0-9]*_drugrecurreadministration',
  'patient_drug_[0-9]*_activesubstance_activesubstancename',
  'patient_drug_[0-9]*_drugrecurrence_[0-9]*_drugrecuraction',
  'patient_drug_drugrecurrence_',
  'reportduplicate*',
  'authoritynumb',
  'patient_patientagegroup',
  'patient_summary_narrativeincludeclinical',
  'patient_drug_[0-9]*_drugadditional',
  'primarysource_literaturereference',
  'patient_drug_[0-9]*_openfda_application_number_[0-9]*',
  'patient_drug_[0-9]*_openfda_product_ndc_[0-9]*',
  'patient_drug_[0-9]*_openfda_product_type_[0-9]*',
  'patient_drug_[0-9]*_openfda_rxcui_[0-9]*',
  'patient_drug_[0-9]*_openfda_nui_[0-9]*',
  'patient_drug_[0-9]*_openfda',
  'patient_drug_[0-9]*_openfda_generic_name_[1-9]*',
  'patient_drug_[0-9]*_openfda_brand_name_[1-9]*',
  'patient_drug_[0-9]*_openfda_manufacturer_name_[0-9]*',
  'patient_drug_[0-9]*_openfda_unii_[0-9]*',
  'patient_drug_[0-9]*_openfda_pharm_class_epc_[0-9]*',
  'patient_drug_[0-9]*_openfda_pharm_class_moa_[0-9]*',
  'patient_drug_[0-9]*_openfda_package_ndc_[0-9]*',
  'patient_drug_[0-9]*_openfda_spl_set_id_[0-9]*',
  'patient_drug_[0-9]*_openfda_spl_id_[0-9]*',
  'patient_drug_[0-9]*_drugbatchnumb',
  'reportduplicate_duplicatesource',
  'reportduplicate_duplicatenumb',
  'receiptdateformat',
  'receiptdate',
  'fulfillexpeditecriteria',
  'sender_sendertype',
  'sender_senderorganization',
  'receiver_receivertype',
  'receiver_receiverorganization',
  'duplicate'
  ]
 
 # Compile the patterns
  pat_compile = []
  for pattern in patterns:
    pat_compile.append(re.compile(pattern))

  # Remove any fields that match the patterns           
  for i in reports_flattened:
      for key in i.copy():
        for pattern in pat_compile:
          if pattern.match(key):
              i.pop(key, None)
  
  print(len(reports_flattened))

  # Find the number of concomitant drugs and interacting drugs in each report
  k = 0
  ditc_drugRem = {}
  for i in reports_flattened:
    nb_concomitant = 0
    nb_interacting = 0
    ditc_drugRem[k] = []    
    for key in i.copy():
          if 'drugcharacterization' in key:
            if i[key] == '2':
              nb_concomitant =  nb_concomitant + 1
              ditc_drugRem[k].append(key)
            elif i[key] == '3':
              nb_interacting =  nb_interacting + 1
              ditc_drugRem[k].append(key)
    i['nb_concomitant'] = nb_concomitant
    i['nb_interacting'] = nb_interacting
    k = k + 1
  
  
  # Find reports that have intereacting and concomitant drugs
  dict_drug2 = {}
  for key in ditc_drugRem:
    if len(ditc_drugRem[key]) > 0:
      dict_drug2[key] = []
      for i in ditc_drugRem[key]:
        num = i.split('_')[2]
        dict_drug2[key].append(f'patient_drug_{num}')

  
  # remove concomitant and interacting drug from reports
  for key in dict_drug2:
    for drug in dict_drug2[key]:
      for field in reports_flattened[key].copy():
        if drug in field:
          reports_flattened[key].pop(field,None)
  
  print(len(reports_flattened))

  # Find the number of reports that have Atorvastatin as one the suspected drugs of the reactions
  rep_num = 0
  found = False
  for report in reports_flattened:
    for field in report:
      drug_name = report[field]
      if ('drug' in field) and (DRUGNAME.lower() in str(drug_name).lower()) and not found:
        rep_num = rep_num + 1
        found = True
    found = False

  print(f'number of cleaned reports {rep_num}')
    
  # Define any fields that could have the drug name
  name_codes = [
  "medicinalproduct",
  "openfda_brand_name",
  "generic_name",
  "activesubstance_activesubstancename",
  "openfda_substance_name"]
 
  # Create a dictionary of drugs in each report that is Atorvastatin
  dict_drug = {}
  k = 0
  for report in reports_flattened:
    dict_drug[k] = []
    for field in report.copy():
      for name in name_codes:
        if (name in field) and (DRUGNAME.lower() in str(report[field]).lower()):
          num = field.split('_')[2]
          dict_drug[k].append(f"patient_drug_{num}")
    k = k + 1

  len(dict_drug)
  # Remove any entry in the drug dictionary that is null
  for i in dict_drug.copy():
    if len(dict_drug[i]) == 0:
      dict_drug.pop(i,None)
    else:
      dict_drug[i] = list(set(dict_drug[i]))
  len(dict_drug)
  dict_drug.keys()
  len(reports_flattened)
  
  #Create a dictionary of reports that has atorvastatin as one of the suspected drug
  dict_to_keep = []
  for index in range(len(reports_flattened)):
    if index in dict_drug.keys():
      dict_to_keep.append(reports_flattened[index])
 
  len(dict_to_keep)
  dict_drug3 = {}
  k = 0
  for report in dict_to_keep:
    dict_drug3[k] = []
    for field in report.copy():
      for name in name_codes:
        if (name in field) and (DRUGNAME.lower() in str(report[field]).lower()):
          num = field.split('_')[2]
          dict_drug3[k].append(f"patient_drug_{num}")
    k = k + 1
  len(dict_drug3)
  for i in dict_drug3.copy():
    if len(dict_drug3[i]) == 0:
      dict_drug3.pop(i,None)
    else:
      dict_drug3[i] = list(set(dict_drug3[i]))
  dict_drug3[0]

  for key in dict_drug3:
    drugs = dict_drug3[key]
    for field in dict_to_keep[key].copy():
      if 'patient_drug' in field:
        drug_name = str(field)[0:14]
        if drug_name not in drugs:
          dict_to_keep[key].pop(field,None)
  
  dict_test = {}
  for key in dict_drug3:
    if len(dict_drug3[key]) > 1:
      dict_test[key] = {}
      for drug in dict_drug3[key]:
        dict_test[key][drug] = 0
        for field in dict_to_keep[key]:
          if drug in field:
            dict_test[key][drug] = dict_test[key][drug] + 1

  for key in dict_test:
    max_val = max(dict_test[key].values())
    for key1 in dict_test[key]:
      if dict_test[key][key1] != max_val:
        for field in dict_to_keep[key].copy():
          if str(key1) in field:
            dict_to_keep[key].pop(field)
  
  dict2 = dict_to_keep
  for report in dict2:
    replacement = {}
    for field in report:
      if "drug" in field:
        num = field.split('_')[2]
        name = field.split(num)[1]
        replacement[field] = f'patient_drug{name}'
    for k,v in list(report.items()):
      report[replacement.get(k,k)] = report.pop(k)
  
  df = pd.DataFrame(dict_to_keep)

  def fill_country(df, col_to_keep, col_for_filling):
      df[col_to_keep] = df.apply(
          lambda row: row[col_for_filling] if row[col_to_keep]== np.nan else row[col_to_keep]
          , axis=1)
      df.drop(columns=col_for_filling, inplace=True)
  fill_country(df,'primarysourcecountry','occurcountry')

  values_for_filling = {"seriousnessother": 0, "seriousnesshospitalization": 0, "seriousnesslifethreatening": 0, "seriousnesscongenitalanomali": 0,"seriousnessdisabling":0,"seriousnessdeath":0}
  
  df.fillna(values_for_filling,inplace=True)

  return df

def create_csv(df, num,DRUGNAME):
  df_name = f'df_{num}_{DRUGNAME}.csv'
  df.to_csv(df_name)
  files.download(df_name)