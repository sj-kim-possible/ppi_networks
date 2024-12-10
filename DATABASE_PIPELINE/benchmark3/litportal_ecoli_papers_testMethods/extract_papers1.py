#!/usr/bin/env python
#
#.-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-
#/ / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \
#`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'
# Extract Text from PMIDs
# sj kim
#
# script overview: Takes a list of PMID's and extracts the full text of each article. 
# The text of each article can be found as [PMID].txt in the directory of this script.
# Some PMID's that cannot be extracted by this script is output as a list: pmid_errors.txt, in the directory of this script.

#### [ port ] ####
import metapub
import io
import requests
import pypdf
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="This script takes a list of PMID's and extracts the full text.")
    parser.add_argument("-p", "--pmidsFile", help="A list of PMID's.", required=True, type=str)
    return parser.parse_args()
args = get_args()

# terminal command:
# ./extract_papers.py -p litportal_ecoli_pmids.csv

# NOTE: 3 queries per second without an NCBI_API_KEY

""" 
# This is the version for litportal_ecoli_pmids.csv & litportal_ecoli_pmids_test.csv
with open(args.pmidsFile, 'r') as pmidsInFile:
    raw_infile = pmidsInFile.readline().strip()
    pmids = str.split(raw_infile, ",")
    
    for pmid in pmids:
        doi = metapub.pubmedcentral.get_doi_for_otherid(str(pmid))
        pmc = metapub.pubmedcentral.get_pmcid_for_otherid(str(pmid))
        print(f"pmid: {pmid}")
        print(f"doi: {doi}")
        print(f"pmcid: {pmc}")
"""

# This version is for pmid_errors.txt:
with open(args.pmidsFile, 'r') as pmidsInFile, open("errors_summary.txt", "a+") as pmidsOutfile:
    pmidsOutfile.write(f"pmid\tdoi\tpmcid\n")
    while True:
        pmid = pmidsInFile.readline().strip()
        if pmid == "":
            break
        doi = metapub.pubmedcentral.get_doi_for_otherid(str(pmid))
        pmc = metapub.pubmedcentral.get_pmcid_for_otherid(str(pmid))
        pmidsOutfile.write(f"{pmid}\t{doi}\t{pmc}\n")
        
