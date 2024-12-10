#!/usr/bin/env python

# This script takes a protein file (2-column .csv with column 0: uniprot entry number, column 1: protein names in order of most common to 
# least (this ordering is the default when downloaded from UniProt))
# and an abstract file which is a list of abstracts downloaded from LitPortal - preprocessed in R (intact_uniprot_comparison.Rmd)
# and finds the number of times any of the protein names are mentioned in the abstract, and how many times per abstract. 
# writes out a file with the UniProt ID, number of times it was encountered in the abstracts file, and the synonyms for the ID.

### [ port ] ###

import argparse
import math
import re

def get_args():
    parser = argparse.ArgumentParser(description="This script constructs a synonym table for E.coli proteins and searches through a list of abstracts to find mentions/matches.")
    parser.add_argument("-p", "--proteinFile", help="Two-column .csv file with UP entry number and protein names, downloaded from UniProt.", required=True, type=str)
    parser.add_argument("-a", "--abstractsFile", help="List of abstracts downloaded from LitPortal.", required=True, type=str)
    return parser.parse_args()
args = get_args()

def addOneToCount(dictionary: dict, key: str) -> None:
    ''' takes a dictionary and a specific key and increments one to existing key/value. If not, adds key and sets to 1.'''
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1

proteinSynonyms = {}
abstractCounts = {}

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
        # case-sensitive searching
        for id, names in proteinSynonyms.items():
            for name in names:
                if name in absline:
                    addOneToCount(abstractCounts, id)


# write out results to a .csv
# UPDATE FILENAME FOR EACH RUN:
with open("osti_ecoli_562_protein_coverage.csv", "w") as summary:
    summary.write(f"ID,Counts,Names\n")
    for id, count in abstractCounts.items():
        summary.write(f"{id}, {count}, {proteinSynonyms[id]}\n")

