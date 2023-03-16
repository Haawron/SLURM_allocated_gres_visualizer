from setuptools import setup
from pip._internal.req import parse_requirements
import os


requirements = parse_requirements('requirements.txt', session=False)
required_packages = [str(package.__dict__.get('req', package.__dict__['requirement'])) for package in requirements]

setup(
    name="slurm_gres_viz",
    version="2.1.1",
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
        'console_scripts' : [
            f'slurm-gres-viz=slurm_gres_viz.main:{"forced_main" if bool(os.environ.get("FORCE_ONLY_MINE", False)) else "main"}'
        ]  # todo: main function을 여러 개 만들고 main class가 옵션을 args가 아니라 init에서 받아와야 함
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
