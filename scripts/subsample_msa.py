# subsample_msa.py
import random

input_file = "data/MSA/InhA/InhA_alignment_fixed.a2m"
output_file = "data/MSA/InhA/InhA_alignment_subsampled.a2m"
max_seqs = 100000

sequences = []
current_header = ""
current_seq = ""

with open(input_file) as f:
    for line in f:
        if line.startswith(">"):
            if current_header:
                sequences.append((current_header, current_seq))
            # Keep full header for first sequence, strip metadata for rest
            current_header = line
            current_seq = ""
        else:
            current_seq += line
    if current_header:
        sequences.append((current_header, current_seq))

print(f"Total sequences: {len(sequences)}")

focus = sequences[0]
rest = sequences[1:]
random.seed(42)
random.shuffle(rest)
selected = [focus] + rest[:max_seqs-1]

with open(output_file, "w") as f:
    # Write focus sequence with full header
    f.write(selected[0][0])
    f.write(selected[0][1])
    # Write rest with cleaned headers (just >ID/start-end)
    for header, seq in selected[1:]:
        clean_header = header.split()[0] + "\n"
        f.write(clean_header)
        f.write(seq)

print(f"Done - wrote {len(selected)} sequences")