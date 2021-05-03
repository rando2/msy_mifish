# Before running, must install python packages openpyxl and pandas packages through PyCharm
import pandas as pd
import os

# SET YOUR VARIABLES HERE
# Set the name of your mifish output file (this assume it's in the same directory (folder) as this script)
mifish_file = "mifish.xlsx"
# Set the name of the associated taxonomy file
taxonomy_file = "fish_taxonomy.xlsx"

# THESE ARE FUNCTIONS YOU WON'T NEED TO CHANGE
def create_taxonomy(mifish_data, taxonomy_file):
    """The first thing you need to do is look up the species to provide information to Galaxy about where they fall
    in a phylogenetic tree. Let's make Python generate us a file that we can edit that contains all of the species
    identified"""

    taxonomy = mifish_data[["Species","Family","Order"]]
    taxonomy = taxonomy.drop_duplicates(subset=None, keep='first')
    taxonomy["Kingdom"] = ["Animalia"] * len(taxonomy.index)
    taxonomy["Phylum"] = [""] * len(taxonomy.index) # We may be able to set this to chordata, just depends on what Mifish is looking for
    taxonomy["Class"] = [""] * len(taxonomy.index)
    taxonomy["Genus"] = [x[0] for x in taxonomy["Species"].str.split(" ")]
    taxonomy["Species"]  = [x[0] for x in taxonomy["Species"].str.split(" ")]

    taxonomy[["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]].to_excel(taxonomy_file)
    print("Fish taxonomy is in", taxonomy_file, ". Please fill in taxonomic information")
    exit(0)

# HERE IS THE MAIN SCRIPT WITH STEPS
# First, read in an Excel file from mifish to Python
mifish_data = pd.read_excel(mifish_file)

# Check if the taxonomic information is available & filled in. If the file doesn't exist, generate it.
if os.path.exists(taxonomy_file):
    mifish_tax = pd.read_excel(taxonomy_file, na_filter = True)
    if mifish_tax["Phylum"].isna().sum() > 0:
        exit("Error: You still need to fill in the phylogenetic information in " + taxonomy_file)
    else:
        print(list(mifish_tax["Phylum"]))
else:
    create_taxonomy(mifish_data, taxonomy_file)

# Taxonomy file: This file is formatted to show the sample name and then the taxonomic classification, like this:
# 794_HC2_R_001.fastq	Bacteria(100);Cyanobacteria_Chloroplast(98);Chloroplast(96);Chloroplast_order_incertae_sedis(96);Chloroplast(96);Bacillariophyta(88);
