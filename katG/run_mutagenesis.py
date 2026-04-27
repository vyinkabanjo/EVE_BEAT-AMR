import os
import copy
import yaml
import subprocess

def generate_and_run_mutants(base_yaml, mutations):
    with open(base_yaml, 'r') as f:
        config = yaml.safe_load(f)

    wt_seq = config['sequences'][0]['protein']['sequence']

    for wt_aa, pos, mut_aa in mutations:
        idx = pos - 1
        if wt_seq[idx] != wt_aa:
            continue

        mut_seq = wt_seq[:idx] + mut_aa + wt_seq[idx+1:]
        mut_config = copy.deepcopy(config)
        mut_config['sequences'][0]['protein']['sequence'] = mut_seq

        yaml_name = f"katG_INH_monomer_{wt_aa}{pos}{mut_aa}.yaml"
        with open(yaml_name, 'w') as f:
            yaml.dump(mut_config, f, sort_keys=False)

        print(f"Executing Boltz-2 prediction for {wt_aa}{pos}{mut_aa}...")
        subprocess.run(
            ['boltz', 'predict', yaml_name, '--use_msa_server', '--cache', '/data1/greenbab/users/lic14/boltz2cache'],
            check=True
        )

if __name__ == '__main__':
    target_mutations = [
        ('D', 137, 'A'), ('D', 137, 'R'), ('D', 137, 'W'),
        ('S', 315, 'A'), ('S', 315, 'D'), ('S', 315, 'W')
    ]
    
    if os.path.exists('katG_INH_monomer.yaml'):
        generate_and_run_mutants('katG_INH_monomer.yaml', target_mutations)
    else:
        print("Error: katG_INH_monomer.yaml not found in the current directory.")
