library(tidyverse)
library(data.table)
library(UniprotR)

#ecoli_562 = fread("/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/uniprotkb_taxonomy_id_562_2024_01_25.tsv")
#reviewed_562 = ecoli_562 %>% filter(Reviewed == "reviewed")
#unique_562 = data.frame(
#  Entry = reviewed_562$Entry,
#  Protein_Names = reviewed_562$`Protein names`
#)

#interactions_562 = data.frame(
#  Protein_A = reviewed_562$Entry,
#  Protein_B = reviewed_562$`Interacts with`
#)

#interactions_562 = interactions_562[!(is.na(interactions_562$Protein_B) | interactions_562$Protein_B==""),]

binary_interactions_562_test = data.frame(matrix(ncol=2))
colnames(binary_interactions_562_test) = c("Protein_A", "Protein_B")
bin_int_count = 0
mult_int_count = 0
for(i in seq(dim(interactions_562)[1])) {
  interacts_with = strsplit(interactions_562$Protein_B[i], "; ") %>% unlist()
  if (sum(grepl("\\s+", interacts_with)) > 0) {interacts_with = str_extract(interacts_with, "(?<=\\[).*(?=\\])")}
  if (length(interacts_with) == 1){
    bin_int_count = bin_int_count + 1
    proteinA = interactions_562$Protein_A[i]
    proteinB = interacts_with
    binary_interaction = c(proteinA, proteinB)
    binary_interactions_562_test = rbind(binary_interactions_562_test, binary_interaction)
  } else { # more than 1 Protein_B
    mult_int_count = mult_int_count + 1
    for(j in seq(length(interacts_with))){
      proteinA = interactions_562$Protein_A[i]
      proteinB = interacts_with[j]
      binary_interaction = c(proteinA, proteinB)
      binary_interactions_562_test = rbind(binary_interactions_562_test, binary_interaction)
    }
  }
}
binary_interactions_562_test = na.omit(binary_interactions_562_test)

#collapse duplicates:
binary_interactions_562_test = binary_interactions_562_test %>% filter(Protein_A != Protein_B)


getBinIntPubs = function(proteinA, proteinB) {
  A = ecoli_562 %>% filter(Entry == proteinA)
  pubs_A = A$`PubMed ID` %>% strsplit("; ") %>% unlist()
  B = ecoli_562 %>% filter(Entry == proteinB)
  pubs_B = B$`PubMed ID` %>% strsplit("; ") %>% unlist()
  
  interaction_pubs = intersect(pubs_A, pubs_B)
  return(length(interaction_pubs))
}

getOrganism = function(protein) {
  protein_info = ecoli_562 %>% filter(Entry == protein)
  organism_name = protein_info$Organism 
  return(organism_name)
}

#binary_interactions_562_test = binary_interactions_562_test %>% mutate(
binary_interactions_562_test %>% mutate(
  #browser(),
  Species_A = GetProteinAnnontate(Protein_A, "organism_name"),
  Species_B = GetProteinAnnontate(Protein_B, "organism_name"),
  Number_Publications = map2_dbl(Protein_A, Protein_B, getBinIntPubs)
)

