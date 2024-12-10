getFileList = function() {
  # using species name, pull list of filenames to parse from all.zip
  setwd("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI")
  if (dir.exists(paths = "./IntAct/psi25/species/") == FALSE) {
    print("Cannot find appropriate species files. Download all.zip from IntAct and unzip psi25/species/.")
  }
  #filenames = list.files("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/IntAct/psi25/species/", 
  #                       pattern ="*.xml", full.names = TRUE)
  filenames = list.files("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/IntAct/yeast/", 
                         pattern = "*.xml", full.names = TRUE)
  print("getFileList was called")
  return(filenames)
}

pull_interactions = function(taxonID) {
  filenames = getFileList()
  
  species_interactions = data.frame()
  data_headers = c("PMID", "ParticipantA", "ParticipantB", "SpeciesA", "TaxonID_A", 
                   "SpeciesB", "TaxonID_B")
  
  # parallelize pulling interactions:
  # don't use all the cores on machine since that will break things
  numcores <- parallel::detectCores()/2 
  cl <- parallel::makeCluster(numcores) 
  clusterEvalQ(cl = cl, library(magrittr)) 
  clusterEvalQ(cl = cl, library(dplyr)) # clusterExport(cl = cl, "combos_num") library(foreach) library(doParallel) 
  registerDoParallel(cl)
  
  # results is the dataframe housing all the ppi data
  #results = foreach(i = 1:length(filenames), .combine = "rbind", .packages = 'RpsiXML') %dopar% {
  for(i in 1:length(filenames)) {
    current_interaction = RpsiXML::parsePsimi25Interaction(filenames[i], INTACT.PSIMI25, verbose=TRUE)
    record = data.frame(matrix(nrow = length(RpsiXML::interactions(current_interaction)), ncol = length(data_headers)))
    
    for(j in 1:length(RpsiXML::interactions(current_interaction))) {
      pmid = current_interaction@interactions[[j]]@expPubMed[[1]]
      #participant_list = current_interaction@interactions[[j]]@participant
      participantA = current_interaction@interactions[[j]]@bait
      print(paste0("participantA:",participantA))
      participantB = current_interaction@interactions[[j]]@prey
      print(paste0("participantB:", participantB))
      
      # skip if not a binary interaction:
      #if(length(participant_list) != 2) { 
      #  next
      #} # exclude na's
      #else if(any(is.na(participant_list))) {
      #  next
      #} else {
      #  participantA = current_interaction@interactions[[j]]@participant[[1]]
      #  participantB = current_interaction@interactions[[j]]@participant[[2]]
      #}
      
      if(is.null(participantA)) {
        speciesA = NA
        speciesA_taxid = NA
        print(paste0("speciesA:",speciesA))
        print(paste0("speciesA_taxid:",speciesA_taxid))
      } else {
        speciesA = lapply(current_interaction@interactors[participantA], function(x) x@organismName)[[1]]
        speciesA_taxid = lapply(current_interaction@interactors[participantA], function(x) x@taxId)[[1]]
      }
      
      if(is.null(participantB)) {
        speciesB = NA
        speciesB_taxid = NA
      } else {
        speciesB = lapply(current_interaction@interactors[participantB], function(x) x@organismName)[[1]]
        speciesB_taxid = lapply(current_interaction@interactors[participantB], function(x) x@taxId)[[1]]
      }
      
      if((speciesA_taxid != taxonID) & (speciesB_taxid != taxonID)) {
        next
      } else {
        record_list = c(pmid, participantA, participantB, speciesA, speciesA_taxid, speciesB, speciesB_taxid)
        
        record[j,] = record_list
      }
      #browser()
    }
    interactions = rbind(interactions, record)
  }
  stopCluster(cl)
  
  colnames(results) = data_headers
  interactions = na.omit(results)
  
  return(interactions)
}

yeast_interactions_fxtest = pull_interactions(559292)