# Draft code for combining files

# Set the name of the output .fasta file for galaxy
fasta_file = "mifish.fasta"

def create_fasta(mifish_data, fasta_file):
    print(mifish_data["Sequence"].unique)
    with open(fasta_file, "w") as outfile:
        for index, row in mifish_data.iterrows():
            seqID = row["Sample name"] + str(index)
            seq = row["Sequence"]
            outfile.write(">" + seqID + "\n" + seq + "\n\n")


# Create the fasta file (should be quick!)
create_fasta(mifish_data, fasta_file)
