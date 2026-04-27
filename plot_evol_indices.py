# plot_evol_indices.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
proteins = ["ATPE_MYCTU", "KATG_MYCTU", "INHA_MYCTU", "DPRE1_MYCTU", 
            "EMBB_MYCTU", "MMPL3_MYCTU", "RPOB_MYCTU"]

data_dir = "results/evol_indices"
plot_dir = "results/plots"
os.makedirs(plot_dir, exist_ok=True)

for protein in proteins:
    # Find the file
    files = [f for f in os.listdir(data_dir) if f.startswith(protein)]
    if not files:
        print(f"No file found for {protein}, skipping")
        continue
    
    df = pd.read_csv(os.path.join(data_dir, files[0]), 
                 header=0,
                 names=['protein_name', 'mutations', 'evol_indices'])
    df = df[df['mutations'] != 'wt']  # remove wildtype

    # Parse mutation info
    df['position'] = df['mutations'].str[1:-1].astype(int)
    df['mut_aa'] = df['mutations'].str[-1]
    df['wt_aa'] = df['mutations'].str[0]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"{protein} Evolutionary Indices", fontsize=14)

    # Plot 1: Histogram
    axes[0].hist(df['evol_indices'], bins=50, color='steelblue', 
                 edgecolor='white', alpha=0.8, density=True)
    axes[0].axvline(x=0, color='red', linestyle='--', linewidth=1.5, 
                    label='WT baseline')
    axes[0].set_xlabel("Evolutionary Index")
    axes[0].set_ylabel("% of Variants")
    axes[0].set_title("Distribution of Evolutionary Indices")
    axes[0].legend()

    # Plot 2: Heatmap (positions x amino acids)
    pivot = df.pivot_table(index='mut_aa', columns='position', 
                           values='evol_indices', aggfunc='mean')
    # Subsample positions if too many
    if pivot.shape[1] > 100:
        step = pivot.shape[1] // 100
        pivot = pivot.iloc[:, ::step]
    
    sns.heatmap(pivot, ax=axes[1], cmap='RdBu_r', center=0,
                cbar_kws={'label': 'Evolutionary Index'},
                xticklabels=10, yticklabels=True)
    axes[1].set_title("Mutational Landscape Heatmap")
    axes[1].set_xlabel("Position")
    axes[1].set_ylabel("Mutant Amino Acid")

    # Plot 3: Mean evol index per position
    pos_means = df.groupby('position')['evol_indices'].mean()
    axes[2].plot(pos_means.index, pos_means.values, 
                 color='steelblue', linewidth=0.8, alpha=0.7)
    axes[2].fill_between(pos_means.index, pos_means.values, 0,
                         where=(pos_means.values < 0), 
                         color='green', alpha=0.3, label='Tolerated')
    axes[2].fill_between(pos_means.index, pos_means.values, 0,
                         where=(pos_means.values > 0),
                         color='red', alpha=0.3, label='Deleterious')
    axes[2].axhline(y=0, color='black', linestyle='--', linewidth=1)
    axes[2].set_xlabel("Position")
    axes[2].set_ylabel("Mean Evolutionary Index")
    axes[2].set_title("Mean Tolerance per Position")
    axes[2].legend()

    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f"{protein}_evol_indices.png"), 
                dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved plots for {protein}")