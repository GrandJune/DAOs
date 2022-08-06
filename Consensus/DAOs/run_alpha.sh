#!/bin/sh
#SBATCH --partition=long
#SBATCH --job-name=Alpha
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=junyi@comp.nus.edu.sg
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py39
python Exp_alpha.py