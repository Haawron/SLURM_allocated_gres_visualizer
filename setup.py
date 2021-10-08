from setuptools import setup

setup(
    name="slurm_gres_viz",
    version="1.0",
    author="Hyogun Lee(Haawron)",
    author_email="gunsbrother@khu.ac.kr",
    python_requires='>=3.6',
    description="The app for visualizing allocated GPUs by SLURM",
    license="MIT",
    url="https://github.com/Haawron/SLURM_allocated_gres_visualizer",
    packages=['slurm_gres_viz'],
    package_dir={'slurm_gres_viz', 'src'},
    entry_points={
        'console_scripts' : ['slurm-gres-viz=src.slurm_gres_viz.main:main']
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
