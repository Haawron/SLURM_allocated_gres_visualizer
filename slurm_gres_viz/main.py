import os
import time

from pathlib import Path

if __name__ == '__main__':  # for test
    from args import args
    from visualizer import SlurmTresVisualizer
else:  # slurm_gres_viz.main
    from .args import args
    from .visualizer import SlurmTresVisualizer


# TODO: GPU 정보 받아오는 건 GPU 옵션 받았을 때만 해야 함
# TODO: 했는데도 느려서 프로파일링 해야 함


def get_display_options():
    display_options = {
        'show_index': args.full or args.index,
        'show_gpu_memory': args.full or args.gpu_memory,
        'show_gpu_util': args.full or args.gpu_util,
        'show_only_mine': args.only_mine,
        'filter_string': args.filter,
    }
    return display_options


def looper(func):  # decorator
    def wrapper(**display_options):
        if args.loop < 0:
            func(**display_options)
        else:
            while True:
                func(**display_options)
                print('\n\n')
                time.sleep(args.loop)
    return wrapper


@looper
def run(**display_options):
    strings = {
        'node_strings': os.popen('scontrol show nodes').read().strip().split('\n\n'),
        'job_strings': os.popen('scontrol show job -d -a').read().strip().split('\n\n'),
    }
    viz = SlurmTresVisualizer(**strings, **display_options)
    viz.show()


def main():
    display_options = get_display_options()
    run(**display_options)


def forced_main():
    display_options = get_display_options()
    if 'admin' not in os.environ['USER']:
        display_options['show_only_mine'] = True
    run(**display_options)


if __name__ == '__main__':  # testing
    if args.test_from_log:
        strings = {}
        for p_case_dir in Path('test/logs').glob('**/*'):
            for obj in ['node', 'job']:
                p_obj = (p_case_dir / obj).with_suffix('.log')
                if p_obj.is_file():
                    with p_obj.open() as f:
                        strings[f'{obj}_strings'] = f.read().strip().split('\n\n')
                else:
                    break
            else:  # no break
                print(p_case_dir.name)
                SlurmTresVisualizer(**strings)
                print()
    else:
        from cProfile import Profile
        from pstats import Stats
        profiler = Profile()
        profiler.runcall(main)
        stats = Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats('tottime')
        stats.print_stats(20)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
