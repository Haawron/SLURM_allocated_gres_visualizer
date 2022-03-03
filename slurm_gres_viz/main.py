from itertools import cycle
import os
import re
if __name__ == '__main__':  # for test
    from args import args
else:
    from .args import args


class bcolors:
    CEND = '\033[0m'
    
#     CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
#     CWHITE  = '\33[37m'
    
    CGREY    = '\33[90m'
    CRED2    = '\33[91m'
    CGREEN2  = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2   = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2  = '\33[96m'
#     CWHITE2  = '\33[97m'

color_pool = [val for key, val in bcolors.__dict__.items() if key.startswith('C') and key!='CEND']


def main():
    job_strings, node_strings = get_strings()
    num_gpus_for_each_node = dict(get_node_attrs(node_string) for node_string in node_strings)
    jobs = [get_job_attrs(job_string) for job_string in job_strings if check_job_running_with_gres(job_string)]
    if not jobs:
        halt()
    prettify_gres(jobs, num_gpus_for_each_node)
    print_legends(jobs)


def get_strings():
    if args.test:
        with open('./test_jobs.txt', 'r') as f1, open('./test_nodes.txt', 'r') as f2:
            job_strings = f1.read().strip().split('\n\n')
            node_strings = f2.read().strip().split('\n\n')
    else:
        job_strings = os.popen('scontrol show job -d').read().strip().split('\n\n')
        node_strings = os.popen('scontrol show nodes').read().strip().split('\n\n')

    if job_strings[0] == 'No jobs in the system':
        halt()

    return job_strings, node_strings


def halt():
    print('No jobs in the system')
    exit()


def prettify_gres(jobs, num_gpus_for_each_node):
    stars = get_stars(jobs, num_gpus_for_each_node)
    nodename_width = max(len(nodename) for nodename in stars)
    for nodename, star_components in stars.items():
        print(f'{nodename:<{nodename_width}}: {star_components}')


def print_legends(jobs):
    column_names = ['COLORS', 'USER_ID', 'JOB_ID', 'ARRAY_IDX', 'JOB_NAME', 'NODE_NAME', 'ALLOCATED_GPUS']
    keys = ['userid', 'jobid', 'arraytaskid', 'jobname']  # columns to compute the column width of each
    widths = [8] + [get_column_width(jobs, key, column_name) for key, column_name in zip(keys, column_names[1:-2])]\
        + [max(len(column_names[-2]), *[len(job['resources'].keys()) for job in jobs])]\
        + [max(len(column_names[-1]), *[len(job['resources'].values()) for job in jobs])]

    delimiter = '  '
    width = sum(widths) + (len(column_names)-1) * len(delimiter)
    print(f'\n{" LEGENDS ":=^{width}}')

    jobs_and_colors = get_jobs_and_colors(jobs)
    indent = sum(widths[:-2]) + (len(column_names)-2) * len(delimiter)
    header = delimiter.join([f'{column_name:{width}s}' for column_name, width in zip(column_names, widths) if width])
    lines = []
    for job, color in jobs_and_colors:
        line_elems = [f'{color}********{bcolors.CEND}']
        for key, width in zip(keys, widths[1:-2]):
            if job[key] is not None:
                if key == 'jobid' and job['arrayjobid'] is not None:
                    line_elems += [f"{job['arrayjobid']:<{width}}"]
                else:
                    line_elems += [f"{job[key]:<{width}}"]
            elif width != 0:  # this job does not have the value but some others do
                line_elems += [' ' * width]
        line_elems += [render_resource_string(job['resources'], indent, widths[-2])]
        line = delimiter.join(line_elems)
        lines += [line]
    body = '\n'.join(lines)
    print(header)
    print(body)


def get_stars(jobs, num_gpus_for_each_node):
    jobs_and_colors = get_jobs_and_colors(jobs)
    stars = {nodename: get_gres_components(num_gpus) for nodename, num_gpus in num_gpus_for_each_node.items()}
    for job, color in jobs_and_colors:
        for nodename, gpu_indices in job['resources'].items():
            for gpu_idx in gpu_indices:
                stars[nodename][gpu_idx] = f'{color}{stars[nodename][gpu_idx]}{bcolors.CEND}'
    stars = {nodename: ''.join(star_components) for nodename, star_components in stars.items()}
    return stars


def render_resource_string(resources, indent, nodename_width):
    delimiter = '\n' + ' ' * indent
    return delimiter.join([
        f'{nodename:{nodename_width}s}  {",".join(map(str, gpu_indices))}'
        for nodename, gpu_indices in resources.items()
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


def get_job_attrs(job_string):
    if check_job_running_with_gres(job_string):
        userid, = re.findall(r'UserId=(\S+)', job_string)
        jobid, = re.findall(r'^JobId=(\d+)', job_string)  # Why ^? => not to capture ArrayJobId
        arrayjobid, = re.findall(r'ArrayJobId=(\d+)', job_string) or (None,)
        arraytaskid, = re.findall(r'ArrayTaskId=(\d+)', job_string) or (None,)
        jobname, = re.findall(r'JobName=(.*)', job_string)
        resources = re.findall(r'\s(Nodes=.*)', job_string)  # \s: white-space-like char
        resources = dict(sum([list(get_res_attrs(res_string).items()) for res_string in resources], []))
        return {'userid': userid, 'jobid': jobid, 'arrayjobid': arrayjobid, 'arraytaskid': arraytaskid, 'jobname': jobname, 'resources': resources}


def get_node_attrs(node_string):
    nodename, = re.findall(r'NodeName=(\S+)', node_string)  # \S: non-white-space-like char
    num_gpus, = re.findall(r'Gres=[a-zA-Z]+:(\d+)', node_string)
    return nodename, int(num_gpus)


def check_job_running_with_gres(job_string):
    jobstate, = re.findall(r'JobState=([A-Z]+)', job_string)
    return jobstate == 'RUNNING' and re.findall(r'GRES=\S+\(IDX:[-,\d]+\)', job_string)


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
    return zip(jobs, cycle(color_pool))


if __name__ == '__main__':
    main()
