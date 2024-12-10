library(doParallel)
library(foreach)
library(RpsiXML) #devtools::install_github("bioc/RpsiXML")
library(tidyverse)

"""
This script extracts protein-protein interactions of a specified species of 
interest. This script must be supplied with the appropriate and specific 
taxonomy ID, which can be found at: https://www.uniprot.org/taxonomy/?query=*
UniProt's Taxonomy browser. 

This script assumes that IntAct in its entirety has been downloaded 
(likely a file named all.zip) and this file must be located:
/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/IntAct
Additionally, the folder psi25/species/ within all.zip must be unzipped. 
This folder can be unzipped using the script: extract_species.sh in the same
folder mentioned above. 

There are two modes to the function below: parallelized and nested for-loop.
For-loop mode exists to debug and collect metadata, parallelized is for speed.
Check variables in code before running to know which mode - labelled with comments.

note to self:
As of 9/21/23, this folder contains 2,424 .xml species files, 2,420 of which are
uniquely named. 
"""

### packages ###
library(RpsiXML)
#devtools::install_github("bioc/RpsiXML")
library(tidyverse)
library(doParallel)
library(foreach)


### functions ###
make_unique_ID <- function(PMID, term1, term2) {
  paste0(c(PMID, sort(c(term1, term2))), collapse = " ")
}

deDupe = function(interaction_df) {
  interaction_df_id = interaction_df %>%
    mutate(ID = pmap(list(PMID = PMID, term1 = EntityA, term2 = EntityB), make_unique_ID) %>% unlist())
  
  deduped = interaction_df_id %>% distinct(ID, .keep_all = TRUE)
  return(deduped)
}


### script ###
pull_interactions = function(taxonID) {
  setwd("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI")
  if (dir.exists(paths = "./IntAct/psi25/species/") == FALSE) {
    print("Cannot find appropriate species files. Download all.zip from IntAct and unzip psi25/species/.")
  }
  
  # all of IntAct:
  filenames = list.files("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/IntAct/psi25/species/", 
                         pattern ="*.xml", full.names = TRUE)
  
  # THIS IS YEAST TEST. 
  #filenames = list.files("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/IntAct/yeast_test", 
  #                       pattern = "*.xml", full.names = TRUE)
  
  species_interactions = data.frame()
  data_headers = c("PMID", "EntityA", "EntityB", "SpeciesA", "TaxonID_A", 
                   "SpeciesB", "TaxonID_B")
  
  unfiltered_interactions = 0 #keeping count of interactions being thrown out
  total_interactions = 0
  
  # parallelize pulling interactions:
  # don't use all the cores on machine since that will break things
  numcores <- parallel::detectCores()/2 
  cl <- parallel::makeCluster(numcores) 
  clusterEvalQ(cl = cl, library(magrittr)) 
  clusterEvalQ(cl = cl, library(dplyr)) # clusterExport(cl = cl, "combos_num") library(foreach) library(doParallel) 
  registerDoParallel(cl)
  
  # results is the dataframe housing all the ppi data
  # RESULTS = PARALLELIZED MODE
  results = foreach(i = 1:length(filenames), .combine = "rbind", .packages = 'RpsiXML') %dopar% {
    # FOR.. = FOR-LOOP MODE
    #for(i in 1:length(filenames)) {
    # current_interaction is the S4 object made by 1 file
    current_interaction = RpsiXML::parsePsimi25Interaction(filenames[i], INTACT.PSIMI25, verbose=TRUE) 
    record = data.frame(matrix(nrow = length(RpsiXML::interactions(current_interaction)), ncol = length(data_headers)))
    
    # within each file, there are n interactions:
    for(j in 1:length(RpsiXML::interactions(current_interaction))) {
      pmid = as.numeric(current_interaction@interactions[[j]]@expPubMed[[1]])
      bait = na.omit(current_interaction@interactions[[j]]@baitUniProt)
      prey_all = na.omit(current_interaction@interactions[[j]]@preyUniProt)
      #participants_all = current_interaction@interactions[[j]]@participant
      
      # check bait first:
      # if length of bait != 1, next
      if(length(bait) != 1){
        unfiltered_interactions = unfiltered_interactions + 1
        total_interactions = total_interactions + 1
        next
        # if bait is NA, next
      } else if (anyNA(bait)) {
        unfiltered_interactions = unfiltered_interactions + 1
        total_interactions = total_interactions + 1
        next
        
        # check prey next:
        # if there's less than one prey entry, next
      } else if (length(prey_all) < 1) {
        unfiltered_interactions = unfiltered_interactions + 1
        total_interactions = total_interactions + 1
        next
        
        # checking if there's exactly 1 prey:
      } else if (length(prey_all) == 1) {
        # if our single prey is NA, next
        if (anyNA(prey_all)) { 
          unfiltered_interactions = unfiltered_interactions + 1
          total_interactions = total_interactions + 1
          next
          
          # if prey == bait, next
        } else if (bait == prey_all) {
          unfiltered_interactions = unfiltered_interactions + 1
          total_interactions = total_interactions + 1
          next
        } else {
          # at this point, we know:
          # bait is valid protein
          # prey is also one valid protein that isn't the same as bait
          
          speciesA = lapply(current_interaction@interactors[bait], function(x) x@organismName)[[1]]
          speciesA_taxon = lapply(current_interaction@interactors[bait], function(x) x@taxId)[[1]]
          speciesB = lapply(current_interaction@interactors[prey_all], function(x) x@organismName)[[1]]
          speciesB_taxon = lapply(current_interaction@interactors[prey_all], function(x) x@taxId)[[1]]
          
          if((speciesA_taxon == taxonID) & (speciesB_taxon == taxonID)) {
            record_list = c(pmid, bait, prey_all, speciesA, speciesA_taxon, speciesB, speciesB_taxon)
            record[j, ] = record_list
            total_interactions = total_interactions + 1
          } else {
            unfiltered_interactions = unfiltered_interactions + 1
            total_interactions = total_interactions + 1
          }
        }
        
        # more than 1 prey:
      } else if(length(prey_all) > 1) {
        
        for(k in 1:length(prey_all)) {
          prey = prey_all[k]
          speciesA = lapply(current_interaction@interactors[bait], function(x) x@organismName)[[1]]
          speciesA_taxon = lapply(current_interaction@interactors[bait], function(x) x@taxId)[[1]]
          speciesB = lapply(current_interaction@interactors[prey], function(x) x@organismName)[[1]]
          speciesB_taxon = lapply(current_interaction@interactors[prey], function(x) x@taxId)[[1]]
          
          if((speciesA_taxon == taxonID) & (speciesB_taxon == taxonID)) {
            record_list = c(pmid, bait, prey, speciesA, speciesA_taxon, speciesB, speciesB_taxon)
            record[j, ] = record_list
            total_interactions = total_interactions + 1
          } else {
            unfiltered_interactions = unfiltered_interactions + 1
            total_interactions = total_interactions + 1
          }
          
        }
        
      }
    } # end of inner for-loop
    species_interactions = rbind(species_interactions, record)
  } # end of outer for-loop
  stopCluster(cl)
  
  # these two lines for parallel run
  colnames(results) = data_headers
  species_interactions = na.omit(results)
  
  # these two lines for for-looping
  #colnames(species_interactions) = data_headers
  #species_interactions = na.omit(species_interactions)
  
  deduped_interactions = deDupe(species_interactions)
  num_dupe = nrow(species_interactions) - nrow(deduped_interactions)
  
  # some summary stats: (only for for-looping)
  #outfile_name = paste0(taxonID, "_summary_stats.txt")
  #write_lines(
  #  c(paste0("organism: ", taxonID),
  #    paste0("invalid interactions tally: ", unfiltered_interactions),
  #    paste0("total number of interactions: ", total_interactions),
  #    paste0("duplicates tally: ", num_dupe),
  #    paste0("percentage of interactions thrown out: ", (unfiltered_interactions + num_dupe)/total_interactions)), 
  #  file = outfile_name
  #)
  
  data_outfile_name = paste0(taxonID, "_interactions_test.csv")
  write.table(deduped_interactions, 
              file = data_outfile_name,
              quote = FALSE,
              sep = '\t',
              row.names = FALSE)
  
  return(deduped_interactions)
} # end of function


# PARALLEL MODE: CHANGE ME WHEN CODE IS UPDATED


start.time = Sys.time()
pull_interactions(83333) #E.coli
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken




