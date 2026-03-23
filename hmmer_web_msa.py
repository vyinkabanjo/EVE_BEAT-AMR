import requests
import time
import os

# TB_PROTEINS = {
#     'InhA': 'P9WGR1',
#     'KatG': 'P9WIE5', 
#     'RpoB': 'P9WGK9',
#     'DprE1': 'I6Y1T8',
#     'MmpL3': 'P9WJF1',
#     'AtpE': 'P9WPS1',
#     'EmbB': 'P9WJP9'
# }

TB_PROTEINS = {
    'InhA': 'P9WGR1',
    'KatG': 'P9WIE5',
}

def get_sequence_from_uniprot(uniprot_id):
    """Fetch sequence from UniProt"""
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        sequence = ''.join(lines[1:])  # Skip header
        return sequence
    return None

def submit_hmmer_search(sequence, database='uniref100'):
    """Submit search to HMMER web server"""
    
    url = 'https://www.ebi.ac.uk/Tools/hmmer/search/jackhmmer'
    
    data = {
        'seq': f'>query\n{sequence}',
        'seqdb': database,
        'iterations': 5,  # 5 iterations like EVE paper
        'incE': 0.001,    # E-value threshold
        'E': 10,
        'alignView': 'full',
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        # Parse job ID from response
        job_url = response.url
        job_id = job_url.split('/')[-1]
        return job_id
    else:
        print(f"Failed to submit: {response.status_code}")
        return None

def check_job_status(job_id):
    """Check if HMMER job is complete"""
    url = f'https://www.ebi.ac.uk/Tools/hmmer/results/{job_id}/score'
    response = requests.get(url)
    return response.status_code == 200

def download_alignment(job_id, output_file):
    """Download alignment in A2M format"""
    
    # Wait for job to complete
    print("Waiting for HMMER search to complete...")
    while not check_job_status(job_id):
        time.sleep(30)
        print(".", end='', flush=True)
    print("\n✓ Search complete!")
    
    # Download alignment
    url = f'https://www.ebi.ac.uk/Tools/hmmer/download/{job_id}/alignment/a2m'
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"✓ Alignment saved to {output_file}")
        return True
    else:
        print(f"✗ Failed to download alignment")
        return False

# Main pipeline
def generate_msa_for_protein(protein_name, uniprot_id):
    """Complete MSA generation pipeline"""
    
    print(f"\n{'='*60}")
    print(f"Generating MSA for {protein_name}")
    print(f"{'='*60}\n")
    
    # 1. Get sequence
    print(f"1. Fetching sequence for {uniprot_id}...")
    sequence = get_sequence_from_uniprot(uniprot_id)
    if not sequence:
        print(f"✗ Failed to get sequence")
        return False
    print(f"✓ Sequence retrieved ({len(sequence)} aa)")
    
    # 2. Submit to HMMER
    print(f"\n2. Submitting to HMMER web server...")
    job_id = submit_hmmer_search(sequence)
    if not job_id:
        print(f"✗ Failed to submit search")
        return False
    print(f"✓ Job submitted: {job_id}")
    
    # 3. Download alignment
    print(f"\n3. Waiting for results and downloading...")
    os.makedirs('data/MSA', exist_ok=True)
    output_file = f'data/MSA/{protein_name}_MTUB_b0.3.a2m'
    success = download_alignment(job_id, output_file)
    
    if success:
        # Check alignment quality
        with open(output_file) as f:
            n_seqs = sum(1 for line in f if line.startswith('>'))
        print(f"\n✓ MSA contains {n_seqs} sequences")
        print(f"✓ N/L ratio: {n_seqs/len(sequence):.1f}")
        
        if n_seqs < 10 * len(sequence):
            print("⚠️  WARNING: MSA may be too shallow for good VAE training")
    
    return success

# Run for all proteins
if __name__ == '__main__':
    results = {}
    
    for protein_name, uniprot_id in TB_PROTEINS.items():
        success = generate_msa_for_protein(protein_name, uniprot_id)
        results[protein_name] = success
        
        if success:
            print(f"\n{'='*60}")
            print(f"✓ {protein_name} MSA COMPLETE")
            print(f"{'='*60}\n")
        else:
            print(f"\n✗ {protein_name} FAILED\n")
        
        # Be nice to the server
        time.sleep(60)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}\n")
    
    for protein, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {protein}")