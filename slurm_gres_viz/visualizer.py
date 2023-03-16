import re
from typing import List, Tuple, Dict
from multiprocessing.pool import ThreadPool

if __name__.startswith('slurm_gres_viz'):  # for test
    from .slurm_objects import Job, GPU, Node
    from .displayer import Displayer
else:
    from slurm_objects import Job, GPU, Node
    from displayer import Displayer


class SlurmTresVisualizer:
    def __init__(self,
        node_strings:List[str], job_strings:List[str],
        test_mode:bool=False,

        show_index:bool=False, show_gpu_memory:bool=False, show_gpu_util:bool=False,
        show_only_mine:bool=False
    ):
        self.node_strings = node_strings
        self.job_strings = job_strings

        self.test_mode = test_mode

        self.show_index = show_index
        self.show_gpu_memory = show_gpu_memory
        self.show_gpu_util = show_gpu_util
        self.show_only_mine = show_only_mine

        self.nodes, self.jobs = self.get_infos()

    # =================================================================================================

    def get_infos(self):
        nodes = self.get_node_infos()
        jobs = self.get_job_infos()
        return nodes, jobs

    def get_node_infos(self):
        request_exporter = self.show_gpu_memory or self.show_gpu_util
        node_ip_dict = get_ips_from_etchosts() if request_exporter else None
        def get_node(node_string):
            return Node(
                node_string=node_string, node_ip_dict=node_ip_dict,
                request_exporter=request_exporter
            )
        if request_exporter:
            with ThreadPool(len(self.node_strings)) as t:
                nodes = t.map(get_node, self.node_strings)
        else:
            nodes = [get_node(node_string) for node_string in self.node_strings]
        return nodes

    def get_job_infos(self):
        job_infos:List[Job] = []
        for job_string in self.job_strings:
            if job_string == 'No jobs in the system':
                job_infos = []
                break
            else:
                jobstate, = re.findall(r'JobState=([A-Z]+)', job_string)
                if jobstate == 'RUNNING':
                    job_info = Job(job_string)
                    job_infos.append(job_info)
        return job_infos

    # =================================================================================================

    def show(self):
        if self.test_mode:
            for job in self.jobs:
                print(job.userid, job.id, job.name)
                print(job.tres_dict)
            print()

        displayer = Displayer(
            self.nodes, self.jobs,
            show_index=self.show_index,
            show_gpu_memory=self.show_gpu_memory,
            show_gpu_util=self.show_gpu_util,
            show_only_mine=self.show_only_mine
        )
        displayer.show()


def get_ips_from_etchosts() -> Dict[str,str]:
    with open('/etc/hosts') as f:
        data = f.read()
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    ip_node_pairs:List[Tuple[str,str]] = re.findall(ip_pattern + r'\s*([\w-]*)', data)  # [(ip, nodename), ...]
    ip_node_pairs = list(map(lambda tuple: tuple[::-1], ip_node_pairs))  # [(nodename, ip), ...]
    return dict(ip_node_pairs)
