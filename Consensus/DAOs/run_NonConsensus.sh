#!/bin/sh
#SBATCH --partition=long
#SBATCH --job-name=NonConsensus
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=junyi@comp.nus.edu.sg
python Exp_NonConsensus.py