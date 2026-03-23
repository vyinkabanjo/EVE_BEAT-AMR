import requests
import os

TB_PROTEINS = {
    'InhA': 'P9WGR1',       # Isoniazid/Ethionamide target
    'KatG': 'P9WIE5',       # Isoniazid activator
    'RpoB': 'P9WGK9',       # Rifampicin target
    'DprE1': 'I6Y1T8',      # Benzothiazinone target
    'MmpL3': 'P9WJF1',      # SQ109 target
    'AtpE': 'P9WPS1',       # Bedaquiline target (ATP synthase subunit)
    'EmbB': 'P9WJP9'        # Ethambutol target
}

# TB_PROTEINS = {
#     'InhA': 'P9WGR1'
# }

def download_uniprot_fasta(uniprot_id, output_dir='data/sequences'):
    """Download FASTA from UniProt"""
    os.makedirs(output_dir, exist_ok=True)
    
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    response = requests.get(url)
    
    if response.status_code == 200:
        output_file = f"{output_dir}/{uniprot_id}.fasta"
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"✓ Downloaded {uniprot_id}")
        return output_file
    else:
        print(f"✗ Failed to download {uniprot_id}")
        return None

# Download all sequences
for protein_name, uniprot_id in TB_PROTEINS.items():
    print(f"Downloading {protein_name} ({uniprot_id})...")
    fasta_file = download_uniprot_fasta(uniprot_id)
    
    # Rename to protein name for clarity
    if fasta_file:
        new_name = f"data/sequences/{protein_name}_MTUB.fasta"
        os.rename(fasta_file, new_name)
        print(f"  Saved as {new_name}\n")