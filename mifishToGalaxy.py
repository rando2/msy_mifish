# Before running, must install python packages openpyxl and pandas packages through PyCharm
import pandas as pd
import os
import csv

# SET YOUR VARIABLES HERE
# Set the name of your mifish output file (this assume it's in the same directory (folder) as this script)
mifish_file = "MiFish Output 797 - 801.xlsx"
# Set the name of the information about the taxonomy
taxonomy_information = "MiFish797_taxonomy.xlsx"
# Set the name of the output .tax file for galaxy
tax_file = "MiFish797.tax"

# THESE ARE FUNCTIONS YOU HOPEFULLY WON'T NEED TO CHANGE
def create_taxonomy(mifish_data, taxonomy_information):
    """The first thing you need to do is look up the species to provide information to Galaxy about where they fall
    in a phylogenetic tree. Let's make Python generate us a file that we can edit that contains all of the species
    identified"""

    taxonomy = mifish_data[["Species","Family","Order"]]
    taxonomy = taxonomy.drop_duplicates(subset=None, keep='first')
    taxonomy["Kingdom"] = ["Animalia"] * len(taxonomy.index)
    taxonomy["Phylum"] = [""] * len(taxonomy.index) # We may be able to set this to chordata, just depends on what Mifish is looking for
    taxonomy["Class"] = [""] * len(taxonomy.index)
    taxonomy["Mifish species"] = taxonomy["Species"]
    taxonomy["Genus"] = [x[0] for x in taxonomy["Species"].str.split(" ")]
    taxonomy["Species"] = [x[1] for x in taxonomy["Species"].str.split(" ")]

    taxonomy[["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species", "Mifish species"]].to_excel(
        taxonomy_information, index=False)
    print("Fish taxonomy is in", taxonomy_information, ". Please fill in taxonomic information, then rerun")
    exit("Exiting after creating taxonomy file")

# HERE IS THE MAIN SCRIPT WITH STEPS
# First, read in an Excel file from mifish to Python
mifish_data = pd.read_excel(mifish_file)
mifish_data = mifish_data[mifish_data["Sample name"] != "Sample name"]

# Load (or generate) taxonomic info file, depending on whether it exists
if os.path.exists(taxonomy_information):
    # Check if the taxonomic information in the file is filled in
    mifish_tax = pd.read_excel(taxonomy_information, na_filter = True)
    if mifish_tax["Phylum"].isna().sum() > 0:
        exit("Error: You still need to fill in the phylogenetic information in " + taxonomy_information)
    else:
        with open(tax_file, "w") as outfile:
            out_writer = csv.writer(outfile, delimiter="\t")
            # If the info is filled in, we can build our .tax file
            for index, row in mifish_data.iterrows():
                sample_name = row["Sample name"]
                confidence = row["Confidence"]
                mifish_species = row["Species"]
                tax_row = mifish_tax[mifish_tax['Mifish species'] == mifish_species].values[0]
                kingdom, phylum, pclass, order, family, genus, species, mifish_species = tax_row
                tax_string = kingdom + "(100);" + phylum + "(100);" + pclass + \
                             "(100);" + order + "(100);"
                if confidence == "HIGH":
                    tax_string += family + "(100);" + genus + "(95);" + \
                                 species + "(92);"
                elif confidence == "MODERATE":
                    tax_string += family + "(97);" + genus + "(87);" + \
                                 species + "(80);"
                elif confidence == "LOW":
                    tax_string += family + "(92);" + genus + "(82);" + \
                                 species + "(70);"
                else:
                    exit("Error! Confidence value not recognized: " + confidence)

                # Write the output to a file in .tax format
                out_writer.writerow([sample_name, tax_string])
else:
    # If the file doesn't exist, generate it.
    create_taxonomy(mifish_data, taxonomy_information)
