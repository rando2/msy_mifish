import pandas as pd

# Draft code for combining files

# List of names of input files. For a list, separate each filename with a comma. The file names need to be in quotes
# Example: input_files = ["myfile1.xlsx", "myfile2.xlsx", "myfile3.xlsx"]
input_files = ["MiFish Output 797 - 801.xlsx"]

# Provide the name you want for the output .fasta file that you need for galaxy
fasta_file = "mifish797.fasta"

# Provide the name you want for the output .count file that you need for galaxy
count_file = "mifish797.count"

# This section contains our functions (shouldn't need to edit)

def create_fasta(mifish_data, fasta_file):
    namedSeq = dict()
    with open(fasta_file, "w") as outfile:
        for index, row in mifish_data.iterrows():
            seqID = row["Sample name"] + "_" + str(index)
            seq = row["Sequence"]
            outfile.write(">" + seqID + "\n" + seq + "\n\n")
            namedSeq[seq] = seqID
    return(namedSeq)

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
count_table.to_csv(count_file)

