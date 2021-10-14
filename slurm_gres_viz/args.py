import argparse


parser = argparse.ArgumentParser(description='SLURM Allocated GRES Visualizer')
parser.add_argument('-i', '--index', action='store_true', 
                    help='Use Gres\' indices instead of stars(*)')
parser.add_argument('-t', action='store_true', 
                    help='Test mode')
args = parser.parse_args()
args.test = args.t  # --test is used by pybuild
