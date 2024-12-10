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
# Some articles that cannot be extracted by this script is output as a list: pmid_errors.txt, in the directory of this script.

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

with open(args.pmidsFile, 'r') as pmidsInFile, open(f"pull_article_manually.txt", "a+") as errorsOutfile:
    errorsOutfile.write(f"pmid\tdoi\tpmcid\n")
    raw_infile = pmidsInFile.readline().strip()
    pmids = str.split(raw_infile, ",")
    
    for pmid in pmids:
        doi = metapub.pubmedcentral.get_doi_for_otherid(str(pmid))
        pmc = metapub.pubmedcentral.get_pmcid_for_otherid(str(pmid))
        # if an article can't be pulled, the doi and pmc are BOTH "None"
        if ((doi == "None") and (pmc == "None")):
            errorsOutfile.write(f"{pmid}\t{doi}\t{pmc}\n")
        else:
            print(f"pmid: {pmid}")
            # For each PMID of interest, fetch article:
            fetch = metapub.PubMedFetcher()
            # fetch article by PMID:
            article = fetch.article_by_pmid(str(pmid))
            # pull article
            src = metapub.FindIt(str(pmid))
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
            