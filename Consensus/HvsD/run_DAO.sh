#!/bin/sh
#SBATCH --partition=long
#SBATCH --job-name=S
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=junyi@comp.nus.edu.sg

python Exp_DAO.py