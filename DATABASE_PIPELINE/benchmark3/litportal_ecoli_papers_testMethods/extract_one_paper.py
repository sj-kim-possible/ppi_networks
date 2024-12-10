#!/usr/bin/env python
#
#.-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-
#/ / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \ \ / / \
#`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'
# Extract Text from PMIDs
# sj kim
#
# script overview: Testing the core functionality of finding a PDF online for one paper
# and extracting text from the one paper

#### [ port ] ####
import metapub
import io
import requests
import pypdf
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="This script takes a list of PMID's and extracts the full text.")
    #parser.add_argument("-p", "--pmidsFile", help="A list of PMID's.", required=True, type=str)
    return parser.parse_args()
args = get_args()

pmid = 36909476
doi = "10.1101/2023.02.27.530276"
#pmc = "PMC10002632"

fetch = metapub.PubMedFetcher()
# fetch article by PMID:
#article = fetch.article_by_pmid(str(pmid))
article = fetch.article_by_doi(str(doi))
#article = fetch.article_by_pmcid(str(pmc))
# pull article
src = metapub.FindIt(doi=str(doi))
if src.url is None: print(src.reason) #TXERROR: could not get PDF from EuropePMC.org and USE_NIH set to False fuuuuuck
# construct URL of article, in PDF form
req = requests.get(src.url)
file = io.BytesIO(req.content)
# extract text from PDF:
reader = pypdf.PdfReader(file)
# open a .txt file to write out content
with open(f"{pmid}.txt", "w") as outfile:
    # loop through all the pages of the PDF and extract text
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        outfile.write(page.extract_text())
