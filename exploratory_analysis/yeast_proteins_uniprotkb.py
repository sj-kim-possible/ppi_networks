#!/usr/bin/env python

# timer
import time
startTime = time.time()

# https://www.uniprot.org/help/api_queries
# port
import re
import requests
from requests.adapters import HTTPAdapter, Retry


re_next_link = re.compile(r'<(.+)>; rel="next"')
retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))

def get_next_link(headers):
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)

def get_batch(batch_url):
    while batch_url:
        response = session.get(batch_url)
        response.raise_for_status()
        total = response.headers["x-total-results"]
        yield response, total
        batch_url = get_next_link(response.headers)

# e.coli: 1.08 million proteins
# taxonomy id for escherichia coli : 562
#url = 'https://rest.uniprot.org/uniprotkb/search?fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Clength%2Ccc_pathway%2Ccc_interaction&format=tsv&query=%28%28taxonomy_id%3A562%29%29&size=500'
# yeast: 6.7k proteins
# taxonomy id for saccharomyces cerevisiae S288C : 559292
#url = 'https://rest.uniprot.org/uniprotkb/search?fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Clength%2Ccc_pathway%2Ccc_interaction&format=tsv&query=%28%28taxonomy_id%3A559292%29%29%20AND%20%28reviewed%3Atrue%29&size=500'
# yeast plus pubmed ID:
url = 'https://rest.uniprot.org/uniprotkb/search?fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Clength%2Ccc_pathway%2Ccc_interaction%2Clit_pubmed_id&format=tsv&query=%28%28taxonomy_id%3A559292%29%29&size=500'

interactions = {}
with open(f"yeast_protein_interactions_pubmedIDs.txt", "w") as pubmedIDOutfile:
    for batch, total in get_batch(url):
    #print(f"batch = {batch}, total = {total}")
        for line in batch.text.splitlines()[1:]:
            record = line.split('\t')
            #print(f"{record}")
            primaryAccession = record[0]
            #print(f"{primaryAccession}")
            interactsWith = record[-2]
            #print(f"{interactsWith}")
            pubmedIDOutfile.write(f"Protein ID: {primaryAccession}, pubmedIDs: {record[-1]}\n")
            #print(f"pubmedIDs = ",{record[-1]})
            interactions[primaryAccession] = len(interactsWith.split(';')) if interactsWith else 0
        print(f'{len(interactions)} / {total}')

sorted_interactions = sorted(interactions.items(), key=lambda item: item[1], reverse=True)
with open(f"yeast_sorted_interactions.txt", "w") as sortedInteractionsOutfile:
    for i in range(len(sorted_interactions)):
        sortedInteractionsOutfile.write(f"{sorted_interactions[i]}\n")

# end timer
executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))