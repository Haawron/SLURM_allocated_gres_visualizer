import argparse


parser = argparse.ArgumentParser(description='SLURM Allocated GRES Visualizer')
parser.add_argument('-i', '--index', action='store_true', 
                    help='Use Gres\' indices instead of stars(*)')
parser.add_argument('-x', action='store_true', 
                    help='Test mode')
args = parser.parse_args()
args.test = args.x  # --test is used by pybuild
