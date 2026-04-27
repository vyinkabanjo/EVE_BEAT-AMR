# fix_headers.py
import os

# protein_name: (eve_name, start, end)
proteins = {
    "InhA":  ("INHA_MYCTU",  1, 269),
    "KatG":  ("KATG_MYCTU",  1, 740),
    "DprE1": ("DPRE1_MYCTU", 1, 461),
    "EmbB":  ("EMBB_MYCTU",  1, 1098),
    "MmpL3": ("MMPL3_MYCTU", 1, 944),
    "AtpE":  ("ATPE_MYCTU",  1, 81),
    "RpoB":  ("RPOB_MYCTU",  1, 1178),
}

msa_dir = "../data/MSA"

for protein, (eve_name, start, end) in proteins.items():
    input_file = f"{msa_dir}/{protein}/{protein}_alignment.a2m"
    output_file = f"{msa_dir}/{protein}/{protein}_alignment_fixed.a2m"

    if not os.path.exists(input_file):
        print(f"Skipping {protein} - file not found")
        continue

    with open(input_file) as f:
        lines = f.readlines()

    lines[0] = f">{eve_name}/{start}-{end}\n"

    with open(output_file, "w") as f:
        f.writelines(lines)

    print(f"Done - {protein}")