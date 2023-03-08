from typing import Dict, List, Union
import re
import os
import csv


def parse_jobstring(job_string:str):
    """Parse job string for a single job.
    """
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
    state, = re.findall(r'State=([\w\+]+)', node_string)
    num_cpus_alloc, = re.findall(r'CPUAlloc=(\d+)', node_string)
    num_cpus_total, = re.findall(r'CPUTot=(\d+)', node_string)
    num_gpus_alloc, = re.findall(r'AllocTRES=.*gres/gpu=(\d)', node_string) or [0]
    num_gpus_total, = re.findall(r'Gres=[a-zA-Z]+:(\d)', node_string)
    mem_alloc, = re.findall(r'AllocMem=(\d+)', node_string)
    mem_total, = re.findall(r'RealMemory=(\d+)', node_string)
    return nodename, state, int(num_cpus_alloc), int(num_cpus_total), int(num_gpus_alloc), int(num_gpus_total), MiB2GiB(float(mem_alloc)), MiB2GiB(float(mem_total))


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
    nodenames = resolve_hostname_expr(nodenames)
    # nodenames = os.popen(f'scontrol show hostname {nodenames}').read().split()
    cpu_indices, = re.findall(r'CPU_IDs=([-,\d]+)', job_tres_string) or ['']
    gpu_indices, = re.findall(r'IDX:([-,\d]+)\)', job_tres_string) or ['']
    cpu_indices = resolve_index_expr(cpu_indices)
    gpu_indices = resolve_index_expr(gpu_indices)
    mem, = map(MiB2GiB, map(int, re.findall(r'Mem=(\d+)', job_tres_string)))
    job_tres_dict = {
        nodename: {'cpus': cpu_indices, 'gpus': gpu_indices, 'mem': mem}
        for nodename in nodenames
    }
    return job_tres_dict


def resolve_hostname_expr(expr:str) -> List[str]:
    """# Vars (example)
    ex0) A single-node job
    @expr: `"batch1"`
    @return: `["batch1"]`

    ex1)
    @expr: `"batch[1,3-5]"`
    @return: `["batch1", "batch3", "batch4", "batch5"]`

    ex2) Dashed hostname
    @expr: `"debug-g[1-4]"`
    @return: `["debug-g1", "debug-g2", "debug-g3", "debug-g4"]`

    ex3) Multiple host ranges
    @expr: `"debug-g[1,3-4],batch[1-2]"`
    @return: `["debug-g1", "debug-g3", "debug-g4", "batch1", "batch2"]`
    """
    # TODO: csv랑 re랑 비교
    splitted_host_ranges, = list(csv.reader([expr], delimiter=',', quotechar='[', quoting=csv.QUOTE_MINIMAL))
    all_hostnames = []
    for splitted_host_range in splitted_host_ranges:
        m = re.match(r'(?P<hostname_root>[\w-]+)(\[(?P<range>[\d,-]+)\])?', splitted_host_range)
        if m['range'] is not None:
            indices = resolve_index_expr(m['range'])
            hostnames = [f"{m['hostname_root']}{i}" for i in indices]
        else:
            hostnames = [m['hostname_root']]
        all_hostnames += hostnames
    return all_hostnames


def resolve_index_expr(expr:str) -> List[int]:
    '''# Vars (example)
    @expr: `"0-1,3"`
    @return: `[0, 1, 3]`
    '''
    if expr:
        # this function is called many times and slow speed of os.popen(...).read() matters
        # indices:List[str] = os.popen(f'scontrol show hostname [{expr_string}]').read().split()
        comma_splitted = expr.split(',')
        indices_lists = list(map(resolve_element_expr, comma_splitted))
        indices = sum(indices_lists, [])
        return sorted(set(map(int, indices)))
    else:
        return []


def resolve_element_expr(element_expr:str):
    """# Vars (example)
    ex1)
    @element_expr: `"0-3"`
    @return: `[0, 1, 2, 3]`

    ex2)
    @element_expr: `"4"`
    @return: `[4]`
    """
    dash_splitted = list(map(int, element_expr.split('-')))
    if len(dash_splitted) == 1:
        return dash_splitted
    elif len(dash_splitted) == 2:
        x, y = dash_splitted
        return list(range(x, y+1))
    else:
        raise


def MiB2GiB(MiB:int) -> float:
    return MiB / 1024
