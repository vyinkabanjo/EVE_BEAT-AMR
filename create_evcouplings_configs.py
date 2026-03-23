# create_evcouplings_configs.py
import os
import json

TB_PROTEINS = {
    'InhA': 'P9WGR1',
    'KatG': 'P9WIE5'
}

def create_config(protein_name, uniprot_id):
    """Create EVcouplings config for alignment generation"""
    
    os.makedirs('evcouplings_configs', exist_ok=True)
    
    config = {
        "global": {
            "prefix": f"{protein_name}_MTUB",
            "sequence_id": uniprot_id,
            "sequence_file": f"data/sequences/{protein_name}_MTUB.fasta",
            "region": None,  # Use full sequence
        },
        
        "databases": {
            # Use EBI's remote jackhmmer service (no local database needed!)
            "sequence_database": "uniref100",
            "jackhmmer_use_web": True,  # KEY: Use web service
        },
        
        "align": {
            "protocol": "standard",
            "iterations": 5,  # Match EVE paper
            
            # Filtering (from EVE paper)
            "sequence_threshold": 0.5,  # ≥50% alignment to target
            "minimum_sequence_coverage": 0.5,
            "minimum_column_coverage": 0.7,  # ≥70% residue occupancy
            
            # Sequence reweighting (EVE uses theta=0.2 for bacteria)
            "theta": 0.2,
            
            # Bit score threshold (EVE uses 0.3 bits/residue)
            "use_bitscores": True,
            "domain_threshold": 0.3,  # bits per aligned residue
            
            # No additional filters
            "seqid_filter": None,
            
            # Compute statistics
            "compute_num_effective_seqs": True,
        },
        
        "batch": {
            "environment": "local",
        },
        
        "management": {
            "output_dir": f"evcouplings_output/{protein_name}_MTUB",
        }
    }
    
    output_file = f"evcouplings_configs/{protein_name}_config.txt"
    
    # EVcouplings uses a custom format (not pure JSON)
    with open(output_file, 'w') as f:
        for section, params in config.items():
            f.write(f"[{section}]\n")
            for key, value in params.items():
                if value is None:
                    continue
                elif isinstance(value, bool):
                    f.write(f"{key} = {str(value).lower()}\n")
                elif isinstance(value, (int, float)):
                    f.write(f"{key} = {value}\n")
                else:
                    f.write(f"{key} = {value}\n")
            f.write("\n")
    
    print(f"✓ Created config: {output_file}")
    return output_file

# Create all configs
for protein_name, uniprot_id in TB_PROTEINS.items():
    create_config(protein_name, uniprot_id)

print("\n✓ All config files created!")