from typing import Dict, List, Union
import re
import os


def parse_jobstring(job_string:str):
    userid, = re.findall(r'UserId=(\S+)', job_string)
    jobid, = re.findall(r'^JobId=(\d+)', job_string)  # Why ^? => not to capture ArrayJobId
    arrayjobid, = re.findall(r'ArrayJobId=(\d+)', job_string) or (None,)
    arraytaskid, = re.findall(r'ArrayTaskId=(\d+)', job_string) or (None,)
    jobname, = re.findall(r'JobName=(.*)', job_string)
    job_tres_strings = re.findall(r'\s(Nodes=.*)', job_string)  # \s: white-space-like char
    job_tres_dict = dict(sum([list(job_tres_string_to_dict(job_tres_string).items()) for job_tres_string in job_tres_strings], []))  # sum up tres dicts
    return userid, jobid, arrayjobid, arraytaskid, jobname, job_tres_dict


def parse_nodestring(node_string:str):
    nodename, = re.findall(r'NodeName=(\S+)', node_string)  # \S: non-white-space-like char
    num_cpus_alloc, = re.findall(r'CPUAlloc=(\d+)', node_string)
    num_cpus_total, = re.findall(r'CPUTot=(\d+)', node_string)
    num_gpus_total, = re.findall(r'Gres=[a-zA-Z]+:(\d+)', node_string)
    mem_alloc, = re.findall(r'AllocMem=(\d+)', node_string)
    mem_total, = re.findall(r'RealMemory=(\d+)', node_string)
    return nodename, int(num_cpus_alloc), int(num_cpus_total), int(num_gpus_total), MiB2GiB(float(mem_alloc)), MiB2GiB(float(mem_total))


def job_tres_string_to_dict(job_tres_string:str) -> Dict[str,List[Union[int,List[int],float]]]:
    """Convert TRES string of a job to python object

    Parameters
    ----------
    job_tres_string : str
        * ex1) `"Nodes=node1 CPU_IDs=0-31 Mem=0 GRES=gpu(IDX:4-7)"`
        * ex2) `"Nodes=vll[2-3] CPU_IDs=8-11 Mem=5120 GRES=gpu:1(IDX:2)`

    Returns
    -------
    Dict[str,List[int]]
    converted allocated TRES infos in appropriate python object
    * ex1) `{'node1': {'cpus': [0, 1, ..., 31], 'gpus': [4, 5, 6, 7]}, 'mem': 0}`
    * ex2) `{'vll2': {'cpus': [8, 9, 10, 11], 'gpus': [2], 'mem': 5120}, 'vll3': {'cpus': [8, 9, 10, 11], 'gpus': [2], 'mem': 5120}}`
    """
    nodenames, = re.findall(r'Nodes=(\S+)', job_tres_string)
    nodenames = os.popen(f'scontrol show hostname {nodenames}').read().split()
    cpu_indices, = re.findall(r'CPU_IDs=([-,\d]+)', job_tres_string) or ['']
    gpu_indices, = re.findall(r'IDX:([-,\d]+)\)', job_tres_string) or ['']
    cpu_indices = resolve_expr(cpu_indices)
    gpu_indices = resolve_expr(gpu_indices)
    mem, = map(MiB2GiB, map(int, re.findall(r'Mem=(\d+)', job_tres_string)))
    job_tres_dict = {
        nodename: {'cpus': cpu_indices, 'gpus': gpu_indices, 'mem': mem}
        for nodename in nodenames
    }
    return job_tres_dict


def resolve_expr(expr_string) -> List[int]:
    '''# Vars (example)
    @expr_string: `"0-1,3"`
    @return: `[0, 1, 3]`
    '''
    if expr_string:
        indices:List[str] = os.popen(f'scontrol show hostname [{expr_string}]').read().split()
        return list(map(int, indices))
    else:
        return []


def MiB2GiB(MiB:int) -> float:
    return MiB / 1024
