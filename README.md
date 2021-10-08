# SLURM_allocated_gres_visualizer
The app for visualizing allocated GPUs by SLURM

# Requirements
This repo can be debianized with `python-stdeb`
```bash
apt-get install python3-stdeb
```
`python-stdeb` has some unspecified dependencies. You need to install them manually.
```bash
apt-get build-essential devscripts dh-python fakeroot python-all
```

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
