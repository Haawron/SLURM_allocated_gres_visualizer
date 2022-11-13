from typing import List
import os
import re
import matplotlib.pyplot as plt
from sty import fg
if __name__ == '__main__':  # for test
    from args import args
else:
    from .args import args


cmap = plt.get_cmap('jet')


def main():
    job_strings, node_strings = get_strings()
    node_attrs = dict(get_node_attrs(node_string) for node_string in node_strings)
    jobs = [get_running_job_with_gres_attrs(job_string) for job_string in job_strings if check_job_running_with_gres(job_string)]
    if not jobs:
        halt()
    prettify_gres(jobs, node_attrs)
    print_legends(jobs)


def get_strings():
    if args.test:
        with open('./test_jobs.txt', 'r') as f1, open('./test_nodes.txt', 'r') as f2:
            job_strings = f1.read().strip().split('\n\n')
            node_strings = f2.read().strip().split('\n\n')
    else:
        job_strings = os.popen('scontrol show job -d -a').read().strip().split('\n\n')
        node_strings = os.popen('scontrol show nodes').read().strip().split('\n\n')

    if job_strings[0] == 'No jobs in the system':
        halt()

    return job_strings, node_strings


def halt():
    print('No jobs in the system')
    exit()


def prettify_gres(jobs, node_attrs):
    stars = get_stars(jobs, node_attrs)
    nodename_width = max(len(nodename) for nodename in stars)
    for nodename, star_components in stars.items():
        print(f'{nodename:<{nodename_width}}: [GPUs] {star_components}  {get_res_strings(nodename, node_attrs)}')

def print_legends(jobs):
    column_names = ['COLORS', 'USER_ID', 'JOB_ID', 'ARRAY_IDX', 'JOB_NAME', 'NODE_NAME', 'GPUS', 'CPUS', 'MEM']
    keys = ['userid', 'jobid', 'arraytaskid', 'jobname']  # columns to compute the column width of each
    widths = [8] + [get_column_width(jobs, key, column_name) for key, column_name in zip(keys, column_names[1:-4])]\
        + [max(len(column_names[-4]), *[len(list(job['gpus'].keys())[0]) for job in jobs])]\
        + [max(len(column_names[-3]), *[len(','.join(str(e) for e in list(job['gpus'].values())[0])) for job in jobs])]\
        + [max(len(column_names[-2]), *[len(','.join(str(e) for e in list(job['cpus'].values())[0])) for job in jobs])]\
        + [max(len(column_names[-1]), *[len(','.join(str(e) for e in list(job['mem'].values())[0])) for job in jobs])]\

    delimiter = '  '
    width = sum(widths) + (len(column_names)-1) * len(delimiter)
    print(f'\n{" LEGENDS ":=^{width}}')

    jobs_and_colors = get_jobs_and_colors(jobs)
    indent = sum(widths[:-4]) + (len(column_names)-5) * len(delimiter)
    header = delimiter.join([f'{column_name:{width}s}' for column_name, width in zip(column_names, widths) if width])
    lines = []
    for job, color in jobs_and_colors:
        # line_elems = [f'{color}********{bcolors.CEND}']
        line_elems = [colorize('********', color)]
        for key, width in zip(keys, widths[1:-4]):
            if job[key] is not None:
                if key == 'jobid' and job['arrayjobid'] is not None:
                    line_elems += [f"{job['arrayjobid']:<{width}}"]
                else:
                    line_elems += [f"{job[key]:<{width}}"]
            elif width != 0:  # this job does not have the value but some others do
                line_elems += [' ' * width]
        line_elems += [render_resource_string(job, indent, [widths[i] for i in range(-4, -1)] + [max(len(list(job['mem'].values())[0]) for job in jobs)])]
        line = delimiter.join(line_elems)
        lines += [line]
    body = '\n'.join(lines)
    print(header)
    print(body)


def get_stars(jobs, node_attrs):
    jobs_and_colors = get_jobs_and_colors(jobs)
    stars = {nodename: get_gres_components(attr['num_gpus']) for nodename, attr in node_attrs.items()}
    for job, color in jobs_and_colors:
        for nodename, gpu_indices in job['gpus'].items():
            for gpu_idx in gpu_indices:
                # stars[nodename][gpu_idx] = f'{color}{stars[nodename][gpu_idx]}{bcolors.CEND}'
                stars[nodename][gpu_idx] = colorize(f'{stars[nodename][gpu_idx]}', color)
    stars = {nodename: ''.join(star_components) for nodename, star_components in stars.items()}

    # for not the same number of GPUs in each node
    blank = "   " if args.index else " " # "   " for index, " " for star
    max_gpus = max([attr['num_gpus'] for attr in node_attrs.values()])
    for nodename, num_gpus in zip(node_attrs.keys(), [attr['num_gpus'] for attr in node_attrs.values()]):
        stars[nodename] = f'{stars[nodename]}{blank*(max_gpus-num_gpus)}'

    return stars


def render_resource_string(job, indent, widths):
    delimiter = '\n' + ' ' * indent
    cpus = list(job['cpus'].values())[0]
    mem = list(job['mem'].values())[0]

    # for multi-node jobs
    if len(job['gpus'].items()) > 1:
        cpus = str(int(cpus) // len(job['gpus'].items()))
        mem = str(float(mem) / len(job['gpus'].items()))

    return delimiter.join([
        f'{nodename:{widths[-4]}s}  {",".join(map(str, gpu_indices)):{widths[-3]}s}  {cpus:{widths[-2]}s}  {float(mem):<{widths[-1]}g} {"GiB"}'
        for nodename, gpu_indices in job['gpus'].items()
    ])


def get_column_width(jobs, key, column_name):
    width_for_values = max(len(job[key] or []) for job in jobs)  # job[arraytaskid] can be None
    if width_for_values==0:
        return 0
    else:
        return max(width_for_values, len(column_name))


def get_gres_components(num_gpus) -> list:
    if args.index:
        return [f'[{str(i)}]' for i in range(num_gpus)]
    else:
        return ['*'] * num_gpus

def get_res_strings(nodename, node_attrs):
    width_cpus = max([len(str(node_attrs[nodename]['alloc_cpus'])) for nodename in node_attrs])
    width_alloc_cpus = max([len(str(node_attrs[nodename]['alloc_cpus'])) for nodename in node_attrs])
    width_mem = max([len(str(node_attrs[nodename]['mem_size'])) for nodename in node_attrs])
    width_alloc_mem = max([len(str(node_attrs[nodename]['alloc_mem'])) for nodename in node_attrs])
    string_cpu = f'[CPUs]  {node_attrs[nodename]["alloc_cpus"]:>{width_alloc_cpus}}/{node_attrs[nodename]["num_cpus"]:>{width_cpus}}'
    string_mem = f'[Mem]  {float(node_attrs[nodename]["alloc_mem"]):{width_alloc_mem}g}/{node_attrs[nodename]["mem_size"]:{width_mem}g} GiB'
    return '  ' + string_cpu + '   ' + string_mem

def get_running_job_with_gres_attrs(job_string):
    if check_job_running_with_gres(job_string):
        userid, = re.findall(r'UserId=(\S+)', job_string)
        jobid, = re.findall(r'^JobId=(\d+)', job_string)  # Why ^? => not to capture ArrayJobId
        arrayjobid, = re.findall(r'ArrayJobId=(\d+)', job_string) or (None,)
        arraytaskid, = re.findall(r'ArrayTaskId=(\d+)', job_string) or (None,)
        jobname, = re.findall(r'JobName=(.*)', job_string)
        gpus = re.findall(r'\s(Nodes=.*)', job_string)  # \s: white-space-like char
        gpus = dict(sum([list(get_res_attrs(res_string).items()) for res_string in gpus], []))
        cpus, mem = get_alloc_res_job_attrs(job_string)
        return {'userid': userid, 'jobid': jobid, 'arrayjobid': arrayjobid,
                'arraytaskid': arraytaskid, 'jobname': jobname,
                'gpus': gpus, 'cpus': cpus, 'mem': mem}

def get_parent_job_array_attrs(job_string):
    if check_job_parent_jobarray(job_string):
        pass

def get_node_attrs(node_string):
    nodename, = re.findall(r'NodeName=(\S+)', node_string)  # \S: non-white-space-like char
    num_gpus, = re.findall(r'Gres=[a-zA-Z]+:(\d+)', node_string)
    num_cpus, = re.findall(r'CPUTot=(\d+)', node_string)
    mem_size, = re.findall(r'RealMemory=(\d+)', node_string)

    alloc_gpus, alloc_cpus, alloc_mem = get_alloc_res_node_attrs(node_string)

    return nodename, {'num_gpus': int(num_gpus), 'num_cpus': int(num_cpus),
                    'mem_size': round(float(mem_size) / 1024, 2), 'alloc_gpus': int(alloc_gpus),
                    'alloc_cpus': int(alloc_cpus), 'alloc_mem': float(alloc_mem)}

def get_alloc_res_node_attrs(node_string):
    alloc_tres = re.findall(r'AllocTRES=cpu=(\d+),mem=(\d+)([a-zA-Z]+),gres/gpu=(\d+)', node_string)
    if len(alloc_tres) == 0:
        return 0, 0, 0
    else:
        alloc_tres = list(alloc_tres[0])
        return alloc_tres[-1], alloc_tres[0], get_mem_size_in_GiB(alloc_tres)[1]

def get_alloc_res_job_attrs(job_string):
    nodename, = re.findall(r'\sNodes=(\S+)', job_string)  # \s: white-space-like char
    alloc_tres = re.findall(r'TRES=cpu=(\d+),mem=(\d+)([a-zA-Z]+)', job_string)
    if len(alloc_tres) == 0:
        return {nodename:0}, {nodename:0}
    else:
        alloc_tres = list(alloc_tres[0])
        return {nodename:alloc_tres[0]}, {nodename:get_mem_size_in_GiB(alloc_tres)[1]}

def get_mem_size_in_GiB(alloc_tres):
    if alloc_tres[2] == 'M':
        alloc_tres[1] = str(round(float(alloc_tres[1]) / 1024, 2))
    else:
        pass

    return alloc_tres

def check_job_running_with_gres(job_string):
    jobstate, = re.findall(r'JobState=([A-Z]+)', job_string)
    return jobstate == 'RUNNING' and re.findall(r'GRES=\S+\(IDX:[-,\d]+\)', job_string)


def check_job_parent_jobarray(job_string):
    jobid, = re.findall(r'^JobId=(\d+)', job_string)
    arrayjobid, = re.findall(r'ArrayJobId=(\d+)', job_string)
    jobstate, = re.findall(r'JobState=([A-Z]+)', job_string)
    if arrayjobid is None \
        or jobstate not in ['RUNNING', 'PENDING'] \
        or jobid != arrayjobid:
        return False
    else:
        return True


def get_res_attrs(res_string):  # Nodes=node1 CPU_IDs=0-31 Mem=0 GRES=gpu(IDX:4-7) -> {'node1': [4, 5, 6, 7]}
    nodes, = re.findall(r'Nodes=(\S+)', res_string)
    if '[' in nodes:
        indices, = re.findall(r'\[([-,\d]+)\]', nodes)
        indices = parse_exp(indices)
        rootname = nodes.split('[')[0]
        nodes = [rootname+str(idx) for idx in indices]
    else:
        nodes = [nodes]
    gres, = re.findall(r'IDX:([-,\d]+)\)', res_string)
    gres = parse_exp(gres)
    return {nodename: gres for nodename in nodes}


def parse_exp(exp_string):  # '0-1,3' -> [0, 1, 3]
    exps = exp_string.split(',')  # '0-1,3' -> ['0-1', '3']
    def expand_exp(exp):  # '0-1' -> [0, 1] or '3' -> [3]
        if '-' in exp:
            a, b = map(int, exp.split('-'))
            return list(range(a, b+1))
        else:
            return [int(exp)]
    return sum([expand_exp(exp) for exp in exps], [])  # concat trick


def get_jobs_and_colors(jobs) -> zip:
    def get_color_from_jid(jid:int):
        color = cmap(((11*jid) % 256) / 256)[:-1]
        color = list(map(lambda x:int(x*255), color))
        return color

    return zip(jobs, [get_color_from_jid(int(job['jobid'])) for job in jobs])


def colorize(source:str, color:List[int]):
    return fg(*color) + source + fg.rs


if __name__ == '__main__':
    main()
