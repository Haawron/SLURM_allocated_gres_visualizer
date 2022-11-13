# SLURM_allocated_gres_visualizer
**The app for visualizing allocated GPUs by SLURM**

![image](https://user-images.githubusercontent.com/25451196/201534640-150d5914-a453-47d2-bf98-d972a5d80337.png)

When you are using Slurm and you want to check which gpus are allocated, you must have done something like
- `ssh` to each computing node and run `nvidia-smi`. Then, repeat it.
- Run `scontrol show job -d | grep GRES` and roll your eyeballs.


both of which are very tedious. This project can solve this.

# Requirements
- matplotlib
- sty

## Slurm
Be sure that `slurmctld`(master) and `slurmd`(nodes) are active so that there are no problems for running `scontrol show nodes` or `scontrol show job`.

# Installation
```bash
git clone https://github.com/Haawron/SLURM_allocated_gres_visualizer.git
cd SLURM_allocated_gres_visualizer
/usr/bin/python3 setup.py install  # be sure to be without conda
```

# Usage
```bash
slurm-gres-viz
slurm-gres-viz -i  # stars are replaced to indices
```

