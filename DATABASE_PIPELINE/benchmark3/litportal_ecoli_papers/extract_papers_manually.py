#!/usr/bin/env python
#
#.-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-
#/ / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \
#`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'
# Extract Text from PMIDs (Manual)
# sj kim
#
# script overview: Takes a (local) directory of article PDF's with the name: [PMID].pdf and extracts the full text of each article. 
# The text of each article can be found as [PMID].txt in the directory of this script.
# Script is intended for PMID's that didn't get extracted from extract_papers.py - manually downloaded PDF's 

#### [ port ] ####
import io
import pypdf
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser(description="This script takes a local directory of article PDF's and extracts the full text.")
    parser.add_argument("-p", "--pdfDir", help="A directory with PDF's to convert to .txt files.", required=True, type=str)
    return parser.parse_args()
args = get_args()

filenames = os.listdir(args.pdfDir)

for file in filenames:
    filepath = f"{args.pdfDir}{file}"
    reader = pypdf.PdfReader(filepath)
    pmid = file.split(".")[0]
    # keep track of where we are when running script
    print(f"pmid: {pmid}")
    # open a .txt file to write out content
    with open(f"{pmid}.txt", "w") as outfile:
        # loop through all the pages of the PDF and extract text
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            outfile.write(page.extract_text())