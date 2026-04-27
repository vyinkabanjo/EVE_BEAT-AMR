# run_msa_processing.py
import sys
import os
sys.path.append('.')
from utils.data_utils import MSA_processing

proteins = ["InhA"]
# proteins = ["KatG"]
# proteins = ["DprE1", "EmbB", "MmpL3", "AtpE", "RpoB"]

os.makedirs("data/weights", exist_ok=True)

for protein in proteins:
    # msa_file = f"data/MSA/{protein}/{protein}_alignment_fixed.a2m"
    msa_file = f"data/MSA/{protein}/{protein}_alignment_subsampled.a2m"
    weights_file = f"data/weights/{protein}_weights"

    if not os.path.exists(msa_file):
        print(f"Skipping {protein} - file not found")
        continue

    print(f"\nProcessing {protein}...")
    msa = MSA_processing(
        MSA_location=msa_file,
        theta=0.2,
        use_weights=True,
        weights_location=weights_file,
        preprocess_MSA=True,
        threshold_sequence_frac_gaps=0.5,
        threshold_focus_cols_frac_gaps=0.3
    )
    print(f"Done - {protein}")