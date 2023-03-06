from setuptools import setup
from pip._internal.req import parse_requirements


requirements = parse_requirements('requirements.txt', session=False)
required_packages = [str(package.req) for package in requirements]

setup(
    name="slurm_gres_viz",
    version="2.0.0",
    author="Hyogun Lee(Haawron)",
    author_email="gunsbrother@khu.ac.kr",
    python_requires='>=3.6',
    install_requires=required_packages,
    description="The app for visualizing allocated GPUs by SLURM",
    license="MIT",
    url="https://github.com/Haawron/SLURM_allocated_gres_visualizer",
    packages=['slurm_gres_viz'],
    package_dir={'slurm_gres_viz': 'slurm_gres_viz'},
    entry_points={
        'console_scripts' : ['slurm-gres-viz=slurm_gres_viz.main:main']
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
