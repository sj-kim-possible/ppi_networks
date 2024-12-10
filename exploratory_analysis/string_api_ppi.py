#!/usr/bin/env python

##################################################################
## For the given list of proteins print out only the interactions
## between these protein which have medium or higher confidence
## experimental score
##
## Requires requests module:
## type "python -m pip install requests" in command line (win)
## or terminal (mac/linux) to install the module
##################################################################

import requests ## python -m pip install requests


string_api_url = "https://version-11-5.string-db.org/api"
output_format = "tsv"
method = "network"

##
## Construct URL
##

# call format:
#https://string-db.org/api/[output-format]/network?identifiers=[your_identifiers]&[optional_parameters]


request_url = "/".join([string_api_url, output_format, method])
#https://string-db.org/api/tsv/network
print(f"request_url = {request_url}")

##
## Set parameters
##

protein_of_interest = ["GMC2"]

params = {

    "identifiers" : "%0d".join(protein_of_interest), # your protein
    "species" : 559292 # species NCBI identifier (yeast)
    #"caller_identity" : "www.awesome_app.org" # your app name

}
print(f"params = {params}")

##
## Call STRING
##

response = requests.post(request_url, data=params)
print(f"response = {response}")

for line in response.text.strip().split("\n"):

    l = line.strip().split("\t")
    print(f"{l}")
    p1, p2 = l[2], l[3]

    ## filter the interaction according to experimental score
    experimental_score = float(l[10])
    if experimental_score > 0.4:
        ## print 
        print("\t".join([p1, p2, "experimentally confirmed (prob. %.3f)" % experimental_score]))