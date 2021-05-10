import pandas as pd
import csv
import os

# Draft code for combining files

# List of names of input files. For a list, separate each filename with a comma. The file names need to be in quotes
# Example: input_files = ["myfile1.xlsx", "myfile2.xlsx", "myfile3.xlsx"]
input_files = ["MiFish Output 797 - 801.xlsx"]

# Provide the name you want for the output .fasta file that you need for galaxy
fasta_file = "mifish797.fasta"

# Set the name of the information about the taxonomy
taxonomy_information = "MiFish797_taxonomy.xlsx"

# Set the name of the output .tax file for galaxy
tax_file = "MiFish797.tax"

# Provide the name you want for the output .count file that you need for galaxy
count_file = "mifish797.count_table"

# This section contains our functions (shouldn't need to edit)

def create_fasta(mifish_data, fasta_file):
    namedSeq = dict()
    with open(fasta_file, "w") as outfile:
        for index, row in mifish_data.iterrows():
            seqID = "Seq" + row["Sample name"] + "_" + str(index)
            seq = row["Sequence"]
            outfile.write(">" + seqID + "\n" + seq + "\n")
            namedSeq[seq] = seqID
    return(namedSeq)

def create_tax(namedData, tax_file, taxonomy_information):
    if os.path.exists(taxonomy_information):
        # Check if the taxonomic information in the file is filled in
        mifish_tax = pd.read_excel(taxonomy_information, na_filter=True)
        if mifish_tax["Phylum"].isna().sum() > 0:
            exit("Error: You still need to fill in the phylogenetic information in " + taxonomy_information)

        sequence_tax = dict()
        # If the info is filled in, we can build our .tax file
        for index, row in namedData.iterrows():
            seqID = row["SeqID"]
            confidence = row["Confidence"]
            mifish_species = row["Species"]
            tax_row = mifish_tax[mifish_tax['Mifish species'] == mifish_species].values[0]
            kingdom, phylum, pclass, order, family, genus, species, mifish_species = tax_row
            tax_string = kingdom + "(100);" + phylum + "(100);" + pclass + "(100);" + order + "(100);"
            if confidence == "HIGH":
                tax_string += family + "(100);" + genus + "(95);" + species + "(92);"
            elif confidence == "MODERATE":
                tax_string += family + "(97);" + genus + "(87);" + species + "(80);"
            elif confidence == "LOW":
                tax_string += family + "(92);" + genus + "(82);" + species + "(70);"
            else:
                exit("Error! Confidence value not recognized: " + confidence)

            # Write the output to a file in .tax format
            sequence_tax[seqID] = tax_string
        taxDF = pd.DataFrame.from_dict(sequence_tax, orient="index")
        taxDF.to_csv(tax_file, sep="\t")


# This section contains the code that runs when you run the script

# First, create a list of all the Mifish output files we want to add to the analysis
df_list = [pd.read_excel(file) for file in input_files]

# Concatenate the files together
allData = pd.concat(df_list)
allData = allData[allData["Sample name"] != "Sample name"]

# Make a fasta file of the unique sequences found and store the info in a dictionary
uniqueSeqDF = allData.drop_duplicates(subset=['Sequence'])
namedSeq = pd.DataFrame.from_dict(create_fasta(uniqueSeqDF, fasta_file), orient="index", columns=["SeqID"])

# Add the sequence names to the rest of the data
namedData = allData.join(pd.DataFrame(namedSeq), on = "Sequence")

# Create the .tax file
create_tax(namedData, tax_file, taxonomy_information)

# Count how many times each sequence occurs per sample
groupedData = namedData.groupby(['Sample name', "SeqID"]).size()
countData = groupedData.to_frame(name = 'size').reset_index()
countData_dict = countData.to_dict()

# The above contains all the data we need, but it's organized wrong. Here we can reorganize it
reordered_dict = dict()
for index in range(0,len(countData.index)):
    sample = countData_dict["Sample name"][index]
    sequence = countData_dict["SeqID"][index]
    value = countData_dict["size"][index]

    seq_dict = reordered_dict.get(sequence, {})
    seq_dict[sample] = value
    reordered_dict[sequence] = seq_dict

# Now we can convert the reorganized data to a dataframe and fill in any missing values with 0
count_table = pd.DataFrame.from_dict(reordered_dict, orient = "index").fillna(0)

# A count table also contains a row indicating the total number of times a sequence was observed.
# Let's compute that and then add it to correct place (first column)
count_table["total"] = count_table.sum(axis=1)
cols = count_table.columns.tolist()
cols = cols[-1:] + cols[:-1]
count_table = count_table[cols]

# Finally, let's convert all of our totals to integers instead of floats (decimals), which is how they're formatted in
# the Galaxy output
for col in cols:
    count_table[col] = count_table[col].astype(int)

# Last but not least, let's write the file!
count_table.index.name = "Representative_Sequence"
count_table.to_csv(count_file)
