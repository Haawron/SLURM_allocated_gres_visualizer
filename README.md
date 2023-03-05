# SLURM_allocated_gres_visualizer
**The app for visualizing allocated GPUs by SLURM**

![image](https://user-images.githubusercontent.com/25451196/222977415-c8b992e6-d46d-4856-9a26-558505e64956.png)

When you are using Slurm and you want to check which gpus are allocated, you must have done something like
- `ssh` to each computing node and run `nvidia-smi`. Then, repeat it.
- Run `scontrol show job -d | grep GRES` and roll your eyeballs.


both of which are very tedious. This project can solve this.

# Requirements

## Packages
- matplotlib
- sty
- prometheus-client
- requests
- pandas

## Slurm
- Be sure that `slurmctld`(master) and `slurmd`(nodes) are active so that there are no problems for running `scontrol show nodes` or `scontrol show job`.
- Be sure that `AutoDetect=nvml` for all computing nodes to avoid GPU index mismatch.
- For all computing nodes, `node-exporter` are available at port `9100` and `dcgm-exporter` at `9400`.

# Installation
```bash
git clone https://github.com/Haawron/SLURM_allocated_gres_visualizer.git
cd SLURM_allocated_gres_visualizer
/usr/bin/python3 setup.py install  # be sure to be without conda
```

# Usage
```bash
slurm-gres-viz

# GPU options
slurm-gres-viz -i  # stars are replaced to indices
slurm-gres-viz -gm -gu  # VRAM and GPU util
slurm-gres-viz -f  # Full information of GPUs
slurm-gres-viz -m  # mine: shows only my GPUs

# others
slurm-gres-viz -l 1  # looping every 1 second (same as nvidia-smi)
```

