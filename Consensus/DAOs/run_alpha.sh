#!/bin/sh
#SBATCH --partition=long
#SBATCH --job-name=Alpha
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=junyi@comp.nus.edu.sg
python Exp_alpha.py