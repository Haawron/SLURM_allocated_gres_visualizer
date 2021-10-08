# SLURM_allocated_gres_visualizer
**The app for visualizing allocated GPUs by SLURM**

When you are using Slurm and you want to check which gpus are allocated, you must have done something like
- `ssh` to each computing node and run `nvidia-smi`. Then, repeat it.
- Run `scontrol show job -d | grep GRES` and roll your eyeballs.


both of which are very tedious. This project can solve this.

# Requirements
## For Debianization
This repo can be debianized with `python3-stdeb`
```bash
apt-get install python3-stdeb
```
`python3-stdeb` has some unspecified dependencies. You need to install them manually.
```bash
apt-get build-essential devscripts dh-python fakeroot python-all
```

## Slurm
Be sure that `slurmctld`(master) and `slurmd`(nodes) are active so that there are no problems for running `scontrol show nodes` or `scontrol show job`.

# Installation
```bash
# Debianize
git clone https://github.com/Haawron/SLURM_allocated_gres_visualizer.git
cd SLURM_allocated_gres_visualizer
python3 setup.py --command-packages=stdeb.command bdist_deb  # be sure to be without conda

# Install
dpkg -i deb_dist/python3-slurm-gres-viz_1.0-1_all.deb
```

# Usage
```bash
slurm-gres-viz
slurm-gres-viz -i
```

![image](https://user-images.githubusercontent.com/25451196/136583132-108034a7-5088-4e46-91d7-c2c37dfd5704.png)
