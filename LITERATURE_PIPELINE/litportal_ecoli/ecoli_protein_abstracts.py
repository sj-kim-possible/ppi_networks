#!/usr/bin/env python

# This script takes 2 files: -p a protein file (2-column .csv with column 0: uniprot entry number, column 1: protein names in 
# order of most common to least (this ordering is the default when downloaded from UniProt))
# and -a an abstract file (.csv) which is a list of abstracts downloaded from LitPortal - preprocessed in R (intact_uniprot_comparison.Rmd)
# and finds the number of times any of the protein names are mentioned in the abstract, and how many times per abstract. 
# writes out a file with the UniProt ID, number of times it was encountered in the abstracts file, and the synonyms for the ID.

# LATEST RUN COMMAND:
# ./ecoli_protein_abstracts.py -p 562_ecoli_proteins.csv -a ecoli_osti_abstracts_7.csv 

### [ port ] ###
import argparse
import math
import re
import csv

def get_args():
    parser = argparse.ArgumentParser(description="This script constructs a synonym table for E.coli proteins and searches through a list of abstracts to find mentions/matches.")
    parser.add_argument("-p", "--proteinFile", help="Two-column .csv file with UP entry number and protein names, downloaded from UniProt.", required=True, type=str)
    parser.add_argument("-a", "--abstractsFile", help="List of abstracts downloaded from LitPortal.", required=True, type=str)
    return parser.parse_args()
args = get_args()

def extract_proteins_from_abstract(abstract_id: int, abstract: str, journal_name: str, protein_synonyms: dict):
    mentioned_proteins = []
    for protein_id, protein_names in protein_synonyms.items():
        for protein_name in protein_names:
            # use regex to find protein names in abstract
            pattern = re.compile(r'\b{}\b'.format(re.escape(protein_name)))
            #print(f"protein name: {protein_name}")
            #print(f"pattern: {pattern}")
            if re.search(pattern, abstract):
                mentioned_proteins.append((protein_id, protein_name))
                #print(f"mentioned_proteins: {mentioned_proteins}")
                #mentioned_proteins.append(protein_name)
                abstract = re.sub(pattern, protein_id, abstract)
                #print(f"abstract with replaced id's: {abstract}")
    return abstract_id, abstract, journal_name, mentioned_proteins

proteinSynonyms = {}
abstractProteins = {}

with open(args.proteinFile, 'r') as proteinFile, open(args.abstractsFile, 'r') as abstractsFile:
    proteinFile.readline() #skip header
    while True:
        line = proteinFile.readline()
        if line == "":
            break

        # remove newlines and quotes
        line = line.strip('\n').replace('"','')
        # remove Enzyme Commission number
        record = re.sub(r"\(EC[\s][\d.]+[-]*\)",'',line)

        elements = record.split(',', 1) #splitting at the first comma to separate the id
        # elements is just the record in a list of 2 elements: uniprot id and the rest of the line as the 2nd element.
    
        # isolate uniprot id number
        uniprot_id = elements[0]
        #print(f"uniprot id: {uniprot_id}")

        # isolate common name
        common_name = elements[1].split(' (', 1)[0].strip()
        #print(f"common_name: {common_name}")

        # break down other names
        # isolate non-common names
        non_common_names = elements[1].split(' (', 1)[1].strip() if len(elements[1].split(' (', 1)) > 1 else ''
        #print(f"non_common_names: {non_common_names}")
        
        # remove trailing paren
        other_names = non_common_names.strip(')')
        #print(f"other_names: {other_names}")

        # split into different names
        other_names_list = re.split(r"\)[\s]+\(", other_names) if len(other_names) > 1 else ''
        #print(f"other_names_list: {other_names_list}")

        all_names = [common_name]
        all_names += other_names_list

        # put it all together into the synonyms dictionary
        proteinSynonyms[uniprot_id] = all_names
        #print(proteinSynonyms)

    abstractsFile.readline() #skip header
    while True:
        absline = abstractsFile.readline()
        if absline == "":
            break

        absline = absline.strip()
        abs_parts = absline.split(',', 1) # separate by first comma
        abs_id = int(abs_parts[0])
        abs_text = abs_parts[1].rsplit(',',1) # separate by last comma
        abstract = abs_text[0] #title, abstract
        journal = abs_text[1]

        mentioned_proteins = extract_proteins_from_abstract(abs_id, abstract, journal, proteinSynonyms)
        #print(mentioned_proteins)
        if len(mentioned_proteins[-1]) > 0:
            abstractProteins[mentioned_proteins[0]] = [mentioned_proteins[1], mentioned_proteins[2], mentioned_proteins[3:]]

    #print(abstractProteins)
with open("osti_ecoli_562_abstracts_proteins.tsv", "w") as summary:
#with open("osti_ecoli_562_abstracts_proteins_test.tsv", "w") as summary:
    summary.write(f"OSTI_ID\tTitle_Abstract\tPublication_Name\tMentioned_Proteins\n")
    for id, values in abstractProteins.items():
        #print(f"values: {values}")
        journal_name = values[1]
        prot_tup_list = values[2][0:]
        #print(f"prot_tup_list: {prot_tup_list}")
        #print(f"prot_tup_list[0]: {prot_tup_list[0]}")
        #print(f"prot_tup_list[0][0]: {prot_tup_list[0][0]}")
        prot_list=[]
        for i in range(len(prot_tup_list[0])):
            prot_list.append(prot_tup_list[0][i])
        #prot_str = ",".join(prot_list)
        #print(f"prot_list: {prot_list}")
        prot_str = ''
        for tup in prot_list:
            prot_str += str(tup) + ","
        prot_str = prot_str[:-1]
        #print(f"prot_str: {prot_str}")
        row = f"{id}\t{values[0]}\t{journal_name}\t{prot_str}\n"
        #print(f"row: {row}")
        summary.write(row)


# write out protein synonyms dictionary
with open("562_ecoli_protein_synonyms_dictionary.csv", "w") as dictionary:
    dictionary.write(f"Uniprot_ID\tNames\n")
    for id, names in proteinSynonyms.items():
        name_str = "\t".join(names)
        row = f"{id}\t{name_str}\n"
        dictionary.write(row)

'''
        # case-sensitive searching
        for id, names in proteinSynonyms.items():
            for name in names:
                if name in absline.split():
                    if abs_id in abstractProteins:
                        print(abs_id, name)
                        abstractProteins[abs_id][1].append(name)
                    else:
                        #print(abstractProteins[abs_id])
                        abstractProteins[abs_id] = [abs, [name]]
'''

'''
# write out results to a .csv
# UPDATE FILENAME FOR EACH RUN:
with open("osti_ecoli_abstracts_proteins.csv", "w") as summary:
    summary.write(f"OSTI_ID,Abstract,Names\n")
    for id, abstract in abstractProteins.items():
        summary.write(f"{id}, {abstract}\n")
'''

