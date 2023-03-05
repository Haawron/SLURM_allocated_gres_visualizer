from typing import List, Dict, Union, Tuple
import os
import re
import time

from pathlib import Path
from multiprocessing.pool import ThreadPool

import matplotlib.pyplot as plt

if __name__ == '__main__':  # for test
    from args import args
    from slurm_objects import Job, GPU, Node
    from displayer import Displayer
else:  # slurm_gres_viz.main
    from .args import args
    from .slurm_objects import Job, GPU, Node
    from .displayer import Displayer


cmap = plt.get_cmap('jet')

# TODO: GPU 정보 받아오는 건 GPU 옵션 받았을 때만 해야 함
# TODO: GPU index 마다의 util 보여줘야 함
# TODO: 반복해서 출력해야 함


class SlurmTresVisualizer:
    def __init__(self, node_strings:List[str], job_strings:List[str]):
        self.node_strings = node_strings
        self.job_strings = job_strings

        self.nodes, self.jobs = self.get_infos()
        if args.test:
            for job in self.jobs:
                print(job.userid, job.id, job.name)
                print(job.tres_dict)
            print()
        self.show()

    # =================================================================================================

    def get_infos(self):
        nodes = self.get_node_infos_from_node_strings()
        jobs = self.get_job_infos_from_job_strings()
        return nodes, jobs

    def get_node_infos_from_node_strings(self):
        node_ip_dict = get_ips_from_etchosts()
        def get_node(node_string):
            return Node(node_string=node_string, node_ip_dict=node_ip_dict)
        with ThreadPool(len(self.node_strings)) as t:
            nodes = t.map(get_node, self.node_strings)
        return nodes

    def get_job_infos_from_job_strings(self):
        job_infos:List[Job] = []
        for job_string in self.job_strings:
            jobstate, = re.findall(r'JobState=([A-Z]+)', job_string)
            if jobstate == 'RUNNING':
                job_infos.append(Job(job_string))
        return job_infos

    # =================================================================================================

    def show(self):
        displayer = Displayer(self.nodes, self.jobs)
        displayer.show()


# =================================================================================================
# =================================================================================================

# static methods


def get_ips_from_etchosts() -> Dict[str,str]:
    with open('/etc/hosts') as f:
        data = f.read()
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    ip_node_pairs:List[Tuple[str,str]] = re.findall(ip_pattern + r'\s*(\w*)', data)  # [(ip, nodename), ...]
    ip_node_pairs = list(map(lambda tuple: tuple[::-1], ip_node_pairs))  # [(nodename, ip), ...]
    return dict(ip_node_pairs)


def main():
    def wrapper():
        strings = {
            'node_strings': os.popen('scontrol show nodes').read().strip().split('\n\n'),
            'job_strings': os.popen('scontrol show job -d -a').read().strip().split('\n\n'),
        }
        SlurmTresVisualizer(**strings)

    if args.loop < 0:
        wrapper()
    else:
        while True:
            wrapper()
            print('\n\n')
            time.sleep(args.loop)


if __name__ == '__main__':
    if args.test:
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
        main()
