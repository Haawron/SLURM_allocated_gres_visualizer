import argparse


def rate_in_range(value):
    value = float(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("Interval must be positive")
    elif value < 1:
        raise argparse.ArgumentTypeError("Interval smaller than 1s is not allowed")
    return value


parser = argparse.ArgumentParser(description='SLURM Allocated GRES Visualizer')

# gpu loggings
parser.add_argument('-m', '--only-mine', action='store_true',
                    help='asd')
parser.add_argument('-f', '--full', action='store_true',
                    help='asd')
parser.add_argument('-i', '--index', action='store_true',
                    help='Use Gres\' indices instead of stars(*)')
parser.add_argument('-gm', '--gpu-memory', action='store_true',
                    help='asd')
parser.add_argument('-gu', '--gpu-util', action='store_true',
                    help='asd')

parser.add_argument('-p', '--filter', type=str, default='', help='give a filter string. e.g. "job_name=foo" "n=foo" "job_id={1,2-4}" "id={1,2-4}" "user_id=bar" "uid=bar" "node=foo-1" "w=foo-1"', nargs='*')

# iterate
parser.add_argument('-l', '--loop', type=rate_in_range, default=-1,
                    help='asd')

# test
parser.add_argument('-t', '--test-from-log', action='store_true',
                    help='Test mode')

args = parser.parse_args()
