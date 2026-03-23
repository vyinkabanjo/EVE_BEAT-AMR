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
    'InhA': 'P9WGR1'
}

def read_local_sequence(protein_name):
    """Read sequence from already-downloaded FASTA file"""
    fasta_file = f'data/sequences/{protein_name}_MTUB.fasta'
    
    if not os.path.exists(fasta_file):
        print(f"✗ FASTA file not found: {fasta_file}")
        print(f"  Run download_tb_sequences.py first!")
        return None
    
    with open(fasta_file, 'r') as f:
        lines = f.readlines()
        # Skip header line, join sequence lines
        sequence = ''.join(line.strip() for line in lines[1:])
    
    return sequence

def submit_mmseqs2_job(sequence, protein_name):
    """Submit to MMseqs2 web server"""
    
    url = "https://search.mmseqs.com/api/ticket"
    
    data = {
        'q': f'>query\n{sequence}',
        'mode': 'env',  # Environmental sequences (like UniRef)
        'database[]': 'UniRef100',  # ← CHANGED TO UNIREF100
    }
    
    print(f"Submitting {protein_name} to MMseqs2...")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        job_id = response.json()['id']
        print(f"✓ Job submitted: {job_id}")
        return job_id
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def check_mmseqs2_status(job_id):
    """Check if job is complete"""
    url = f"https://search.mmseqs.com/api/ticket/{job_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        status = response.json()['status']
        return status == 'COMPLETE'
    return False

def download_mmseqs2_alignment(job_id, output_file):
    """Download alignment"""
    
    # Wait for completion
    print("Waiting for job to complete", end='', flush=True)
    max_wait = 3600  # 1 hour max
    elapsed = 0
    
    while not check_mmseqs2_status(job_id) and elapsed < max_wait:
        print('.', end='', flush=True)
        time.sleep(10)
        elapsed += 10
    
    if elapsed >= max_wait:
        print("\n✗ Timeout - job took too long")
        return False
    
    print(" Done!")
    
    # Download A3M format (similar to A2M)
    url = f"https://search.mmseqs.com/api/result/download/{job_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(output_file, 'w') as f:
            f.write(response.text)
        
        # Count sequences
        n_seqs = response.text.count('>')
        
        # Get alignment length (first sequence)
        lines = response.text.split('\n')
        first_seq_lines = []
        in_first_seq = False
        for line in lines:
            if line.startswith('>'):
                if in_first_seq:
                    break
                in_first_seq = True
            elif in_first_seq:
                first_seq_lines.append(line.strip())
        
        aln_length = len(''.join(first_seq_lines).replace('-', ''))
        
        print(f"✓ Downloaded alignment:")
        print(f"  Sequences: {n_seqs}")
        print(f"  Length: {aln_length} positions")
        print(f"  N/L ratio: {n_seqs/aln_length:.1f}")
        
        # Quality check
        if n_seqs < 50:
            print(f"  ⚠️  WARNING: Very shallow alignment")
        elif n_seqs > 100000:
            print(f"  ⚠️  WARNING: Very deep alignment (may need subsampling)")
        else:
            print(f"  ✓ Alignment depth looks good")
        
        return True
    else:
        print(f"✗ Download failed: {response.status_code}")
        return False

# Main execution
if __name__ == '__main__':
    
    print("\n" + "="*60)
    print("MSA Generation via MMseqs2 (UniRef100)")
    print("="*60 + "\n")
    
    # Check that sequences exist
    if not os.path.exists('data/sequences'):
        print("✗ data/sequences/ directory not found!")
        print("  Run download_tb_sequences.py first!")
        exit(1)
    
    os.makedirs('data/MSA', exist_ok=True)
    
    results = {}
    job_info = {}  # Save job IDs in case we need to resume
    
    for protein_name, uniprot_id in TB_PROTEINS.items():
        print(f"\n{'='*60}")
        print(f"Generating MSA for {protein_name} ({uniprot_id})")
        print(f"{'='*60}\n")
        
        # Read sequence from local file (NO RE-DOWNLOADING!)
        sequence = read_local_sequence(protein_name)
        if not sequence:
            results[protein_name] = False
            continue
        
        print(f"✓ Loaded sequence: {len(sequence)} aa")
        
        # Submit job
        job_id = submit_mmseqs2_job(sequence, protein_name)
        if not job_id:
            results[protein_name] = False
            continue
        
        job_info[protein_name] = job_id
        
        # Download alignment
        output_file = f"data/MSA/{protein_name}_MTUB_b0.3.a3m"
        success = download_mmseqs2_alignment(job_id, output_file)
        results[protein_name] = success
        
        if success:
            print(f"\n✓✓✓ {protein_name} MSA COMPLETE")
            print(f"    Saved to: {output_file}\n")
        else:
            print(f"\n✗✗✗ {protein_name} FAILED\n")
        
        # Be nice to the server
        if protein_name != list(TB_PROTEINS.keys())[-1]:  # Not last protein
            print("Waiting 30 seconds before next submission...")
            time.sleep(30)
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}\n")
    
    for protein, success in results.items():
        status = "✓" if success else "✗"
        file_path = f"data/MSA/{protein}_MTUB_b0.3.a3m" if success else "N/A"
        print(f"{status} {protein:10s} → {file_path}")
    
    success_count = sum(results.values())
    print(f"\n{success_count}/{len(results)} proteins completed successfully")
    
    # Save job IDs for reference
    if job_info:
        with open('mmseqs2_job_ids.txt', 'w') as f:
            for protein, job_id in job_info.items():
                f.write(f"{protein}\t{job_id}\n")
        print(f"\n✓ Job IDs saved to mmseqs2_job_ids.txt")
    
    if success_count == len(results):
        print("\n🎉 ALL MSAs GENERATED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Transfer data/MSA/ folder to work laptop")
        print("2. Run train_VAE.py")
        print("3. Run compute_evol_indices.py")
        print("4. Run train_GMM_and_compute_EVE_scores.py")
    elif success_count > 0:
        print(f"\n⚠️  {len(results) - success_count} proteins failed")
        print("You can retry just those proteins manually")
    else:
        print("\n✗ No MSAs generated - check API status or try manual HMMER submission")