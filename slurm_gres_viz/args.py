import argparse


parser = argparse.ArgumentParser(description='SLURM Allocated GRES Visualizer')
parser.add_argument('-i', '--index', action='store_true', 
                    help='Use Gres\'s indices instead of stars(*)')
args = parser.parse_args()
