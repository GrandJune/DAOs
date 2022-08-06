#!/bin/sh
#SBATCH --partition=long
#SBATCH --job-name=T
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=junyi@comp.nus.edu.sg
python Exp_t.py