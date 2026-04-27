# plot_training_loss.py
import re
import matplotlib.pyplot as plt

def parse_training_log(log_file):
    steps, elbo, bce, kld_latent, kld_decoder = [], [], [], [], []
    with open(log_file) as f:
        for line in f:
            match = re.search(r'Update (\d+). Negative ELBO : ([\d.]+), BCE: ([\d.]+), KLD_latent: ([\d.]+), KLD_decoder_params_norm: ([\d.]+)', line)
            if match:
                steps.append(int(match.group(1)))
                elbo.append(float(match.group(2)))
                bce.append(float(match.group(3)))
                kld_latent.append(float(match.group(4)))
                kld_decoder.append(float(match.group(5)))
    return steps, elbo, bce, kld_latent, kld_decoder

# log_files = {
#     "KatG": "logs/eve_train_katg_15848200.log",
#     "AtpE": "logs/eve_train_atpe_15864809.log",
#     "DprE1": "logs/eve_train_dpre1_15853817.log",
#     "EmbB": "logs/eve_train_embb_15853925.log",
#     "MmpL3": "logs/eve_train_mmpl3_15864523.log",
#     "RpoB": "logs/eve_train_rpob_15864604.log",
# }

log_files = {
    "InhA": "logs/eve_train_inha_16241833.log",
    "DprE1": "logs/eve_train_dpre1_16241849.log",
    "MmpL3": "logs/eve_train_mmpl3_16241860.log"
}

for protein,log_file in log_files.items():
    steps, elbo, bce, kld_latent, kld_decoder = parse_training_log(log_file)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f"{protein} EVE Training Loss", fontsize=14)

    axes[0,0].plot(steps, elbo)
    axes[0,0].set_title("Negative ELBO")
    axes[0,0].set_xlabel("Steps")

    axes[0,1].plot(steps, bce, color='orange')
    axes[0,1].set_title("BCE")
    axes[0,1].set_xlabel("Steps")

    axes[1,0].plot(steps, kld_latent, color='green')
    axes[1,0].set_title("KLD Latent")
    axes[1,0].set_xlabel("Steps")

    axes[1,1].plot(steps, kld_decoder, color='red')
    axes[1,1].set_title("KLD Decoder")
    axes[1,1].set_xlabel("Steps")

    plt.tight_layout()
    plt.savefig(f"logs/{protein.lower()}_training_loss.png", dpi=200, bbox_inches='tight')
    print(f"Saved to logs/{protein.lower()}_training_loss.png")