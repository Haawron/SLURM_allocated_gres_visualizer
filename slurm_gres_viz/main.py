from array import array
from itertools import cycle
import os
import re
import math
if __name__ == '__main__':  # for test
    from args import args
else:
    from .args import args

class bcolors:
    CEND = '\033[0m'

    MAROON="\033[38;5;1m"
    GREEN="\033[38;5;2m"
    OLIVE="\033[38;5;3m"
    NAVY="\033[38;5;4m"
    PURPLE="\033[38;5;5m"
    TEAL="\033[38;5;6m"
    SILVER="\033[38;5;7m"
    GREY="\033[38;5;8m"
    RED="\033[38;5;9m"
    LIME="\033[38;5;10m"
    YELLOW="\033[38;5;11m"
    BLUE="\033[38;5;12m"
    FUCHSIA="\033[38;5;13m"
    AQUA="\033[38;5;14m"
    NAVYBLUE="\033[38;5;17m"
    DARKBLUE="\033[38;5;18m"
    BLUE3="\033[38;5;19m"
    BLUE3="\033[38;5;20m"
    BLUE1="\033[38;5;21m"
    DARKGREEN="\033[38;5;22m"
    DEEPSKYBLUE4="\033[38;5;23m"
    DEEPSKYBLUE4="\033[38;5;24m"
    DEEPSKYBLUE4="\033[38;5;25m"
    DODGERBLUE3="\033[38;5;26m"
    DODGERBLUE2="\033[38;5;27m"
    GREEN4="\033[38;5;28m"
    SPRINGGREEN4="\033[38;5;29m"
    TURQUOISE4="\033[38;5;30m"
    DEEPSKYBLUE3="\033[38;5;31m"
    DEEPSKYBLUE3="\033[38;5;32m"
    DODGERBLUE1="\033[38;5;33m"
    GREEN3="\033[38;5;34m"
    SPRINGGREEN3="\033[38;5;35m"
    DARKCYAN="\033[38;5;36m"
    LIGHTSEAGREEN="\033[38;5;37m"
    DEEPSKYBLUE2="\033[38;5;38m"
    DEEPSKYBLUE1="\033[38;5;39m"
    GREEN3="\033[38;5;40m"
    SPRINGGREEN3="\033[38;5;41m"
    SPRINGGREEN2="\033[38;5;42m"
    CYAN3="\033[38;5;43m"
    DARKTURQUOISE="\033[38;5;44m"
    TURQUOISE2="\033[38;5;45m"
    GREEN1="\033[38;5;46m"
    SPRINGGREEN2="\033[38;5;47m"
    SPRINGGREEN1="\033[38;5;48m"
    MEDIUMSPRINGGREEN="\033[38;5;49m"
    CYAN2="\033[38;5;50m"
    CYAN1="\033[38;5;51m"
    DARKRED="\033[38;5;52m"
    DEEPPINK4="\033[38;5;53m"
    PURPLE4="\033[38;5;54m"
    PURPLE4="\033[38;5;55m"
    PURPLE3="\033[38;5;56m"
    BLUEVIOLET="\033[38;5;57m"
    ORANGE4="\033[38;5;58m"
    GREY37="\033[38;5;59m"
    MEDIUMPURPLE4="\033[38;5;60m"
    SLATEBLUE3="\033[38;5;61m"
    SLATEBLUE3="\033[38;5;62m"
    ROYALBLUE1="\033[38;5;63m"
    CHARTREUSE4="\033[38;5;64m"
    DARKSEAGREEN4="\033[38;5;65m"
    PALETURQUOISE4="\033[38;5;66m"
    STEELBLUE="\033[38;5;67m"
    STEELBLUE3="\033[38;5;68m"
    CORNFLOWERBLUE="\033[38;5;69m"
    CHARTREUSE3="\033[38;5;70m"
    DARKSEAGREEN4="\033[38;5;71m"
    CADETBLUE="\033[38;5;72m"
    CADETBLUE="\033[38;5;73m"
    SKYBLUE3="\033[38;5;74m"
    STEELBLUE1="\033[38;5;75m"
    CHARTREUSE3="\033[38;5;76m"
    PALEGREEN3="\033[38;5;77m"
    SEAGREEN3="\033[38;5;78m"
    AQUAMARINE3="\033[38;5;79m"
    MEDIUMTURQUOISE="\033[38;5;80m"
    STEELBLUE1="\033[38;5;81m"
    CHARTREUSE2="\033[38;5;82m"
    SEAGREEN2="\033[38;5;83m"
    SEAGREEN1="\033[38;5;84m"
    SEAGREEN1="\033[38;5;85m"
    AQUAMARINE1="\033[38;5;86m"
    DARKSLATEGRAY2="\033[38;5;87m"
    DARKRED="\033[38;5;88m"
    DEEPPINK4="\033[38;5;89m"
    DARKMAGENTA="\033[38;5;90m"
    DARKMAGENTA="\033[38;5;91m"
    DARKVIOLET="\033[38;5;92m"
    PURPLE="\033[38;5;93m"
    ORANGE4="\033[38;5;94m"
    LIGHTPINK4="\033[38;5;95m"
    PLUM4="\033[38;5;96m"
    MEDIUMPURPLE3="\033[38;5;97m"
    MEDIUMPURPLE3="\033[38;5;98m"
    SLATEBLUE1="\033[38;5;99m"
    YELLOW4="\033[38;5;100m"
    WHEAT4="\033[38;5;101m"
    GREY53="\033[38;5;102m"
    LIGHTSLATEGREY="\033[38;5;103m"
    MEDIUMPURPLE="\033[38;5;104m"
    LIGHTSLATEBLUE="\033[38;5;105m"
    YELLOW4="\033[38;5;106m"
    DARKOLIVEGREEN3="\033[38;5;107m"
    DARKSEAGREEN="\033[38;5;108m"
    LIGHTSKYBLUE3="\033[38;5;109m"
    LIGHTSKYBLUE3="\033[38;5;110m"
    SKYBLUE2="\033[38;5;111m"
    CHARTREUSE2="\033[38;5;112m"
    DARKOLIVEGREEN3="\033[38;5;113m"
    PALEGREEN3="\033[38;5;114m"
    DARKSEAGREEN3="\033[38;5;115m"
    DARKSLATEGRAY3="\033[38;5;116m"
    SKYBLUE1="\033[38;5;117m"
    CHARTREUSE1="\033[38;5;118m"
    LIGHTGREEN="\033[38;5;119m"
    LIGHTGREEN="\033[38;5;120m"
    PALEGREEN1="\033[38;5;121m"
    AQUAMARINE1="\033[38;5;122m"
    DARKSLATEGRAY1="\033[38;5;123m"
    RED3="\033[38;5;124m"
    DEEPPINK4="\033[38;5;125m"
    MEDIUMVIOLETRED="\033[38;5;126m"
    MAGENTA3="\033[38;5;127m"
    DARKVIOLET="\033[38;5;128m"
    PURPLE="\033[38;5;129m"
    DARKORANGE3="\033[38;5;130m"
    INDIANRED="\033[38;5;131m"
    HOTPINK3="\033[38;5;132m"
    MEDIUMORCHID3="\033[38;5;133m"
    MEDIUMORCHID="\033[38;5;134m"
    MEDIUMPURPLE2="\033[38;5;135m"
    DARKGOLDENROD="\033[38;5;136m"
    LIGHTSALMON3="\033[38;5;137m"
    ROSYBROWN="\033[38;5;138m"
    GREY63="\033[38;5;139m"
    MEDIUMPURPLE2="\033[38;5;140m"
    MEDIUMPURPLE1="\033[38;5;141m"
    GOLD3="\033[38;5;142m"
    DARKKHAKI="\033[38;5;143m"
    NAVAJOWHITE3="\033[38;5;144m"
    GREY69="\033[38;5;145m"
    LIGHTSTEELBLUE3="\033[38;5;146m"
    LIGHTSTEELBLUE="\033[38;5;147m"
    YELLOW3="\033[38;5;148m"
    DARKOLIVEGREEN3="\033[38;5;149m"
    DARKSEAGREEN3="\033[38;5;150m"
    DARKSEAGREEN2="\033[38;5;151m"
    LIGHTCYAN3="\033[38;5;152m"
    LIGHTSKYBLUE1="\033[38;5;153m"
    GREENYELLOW="\033[38;5;154m"
    DARKOLIVEGREEN2="\033[38;5;155m"
    PALEGREEN1="\033[38;5;156m"
    DARKSEAGREEN2="\033[38;5;157m"
    DARKSEAGREEN1="\033[38;5;158m"
    PALETURQUOISE1="\033[38;5;159m"
    RED3="\033[38;5;160m"
    DEEPPINK3="\033[38;5;161m"
    DEEPPINK3="\033[38;5;162m"
    MAGENTA3="\033[38;5;163m"
    MAGENTA3="\033[38;5;164m"
    MAGENTA2="\033[38;5;165m"
    DARKORANGE3="\033[38;5;166m"
    INDIANRED="\033[38;5;167m"
    HOTPINK3="\033[38;5;168m"
    HOTPINK2="\033[38;5;169m"
    ORCHID="\033[38;5;170m"
    MEDIUMORCHID1="\033[38;5;171m"
    ORANGE3="\033[38;5;172m"
    LIGHTSALMON3="\033[38;5;173m"
    LIGHTPINK3="\033[38;5;174m"
    PINK3="\033[38;5;175m"
    PLUM3="\033[38;5;176m"
    VIOLET="\033[38;5;177m"
    GOLD3="\033[38;5;178m"
    LIGHTGOLDENROD3="\033[38;5;179m"
    TAN="\033[38;5;180m"
    MISTYROSE3="\033[38;5;181m"
    THISTLE3="\033[38;5;182m"
    PLUM2="\033[38;5;183m"
    YELLOW3="\033[38;5;184m"
    KHAKI3="\033[38;5;185m"
    LIGHTGOLDENROD2="\033[38;5;186m"
    LIGHTYELLOW3="\033[38;5;187m"
    GREY84="\033[38;5;188m"
    LIGHTSTEELBLUE1="\033[38;5;189m"
    YELLOW2="\033[38;5;190m"
    DARKOLIVEGREEN1="\033[38;5;191m"
    DARKOLIVEGREEN1="\033[38;5;192m"
    DARKSEAGREEN1="\033[38;5;193m"
    HONEYDEW2="\033[38;5;194m"
    LIGHTCYAN1="\033[38;5;195m"
    RED1="\033[38;5;196m"
    DEEPPINK2="\033[38;5;197m"
    DEEPPINK1="\033[38;5;198m"
    DEEPPINK1="\033[38;5;199m"
    MAGENTA2="\033[38;5;200m"
    MAGENTA1="\033[38;5;201m"
    ORANGERED1="\033[38;5;202m"
    INDIANRED1="\033[38;5;203m"
    INDIANRED1="\033[38;5;204m"
    HOTPINK="\033[38;5;205m"
    HOTPINK="\033[38;5;206m"
    MEDIUMORCHID1="\033[38;5;207m"
    DARKORANGE="\033[38;5;208m"
    SALMON1="\033[38;5;209m"
    LIGHTCORAL="\033[38;5;210m"
    PALEVIOLETRED1="\033[38;5;211m"
    ORCHID2="\033[38;5;212m"
    ORCHID1="\033[38;5;213m"
    ORANGE1="\033[38;5;214m"
    SANDYBROWN="\033[38;5;215m"
    LIGHTSALMON1="\033[38;5;216m"
    LIGHTPINK1="\033[38;5;217m"
    PINK1="\033[38;5;218m"
    PLUM1="\033[38;5;219m"
    GOLD1="\033[38;5;220m"
    LIGHTGOLDENROD2="\033[38;5;221m"
    LIGHTGOLDENROD2="\033[38;5;222m"
    NAVAJOWHITE1="\033[38;5;223m"
    MISTYROSE1="\033[38;5;224m"
    THISTLE1="\033[38;5;225m"
    YELLOW1="\033[38;5;226m"
    LIGHTGOLDENROD1="\033[38;5;227m"
    KHAKI1="\033[38;5;228m"
    WHEAT1="\033[38;5;229m"
    CORNSILK1="\033[38;5;230m"


color_pool = [val for key, val in bcolors.__dict__.items() if key!='CEND']
import random; random.shuffle(color_pool)


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
    column_names = ['COLORS', 'USER_ID', 'JOB_ID', 'ARRAY_IDX', 'JOB_NAME', 'NODE_NAME', 'ALLOCATED_GPUS', 'ALLOCATED_CPUS', 'ALLOCATED_MEM']
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
        line_elems = [f'{color}********{bcolors.CEND}']
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
                stars[nodename][gpu_idx] = f'{color}{stars[nodename][gpu_idx]}{bcolors.CEND}'
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
    return f'{node_attrs[nodename]["alloc_gpus"]}/{node_attrs[nodename]["num_gpus"]}\t[CPUs]  {node_attrs[nodename]["alloc_cpus"]:>{width_alloc_cpus}}/{node_attrs[nodename]["num_cpus"]:>{width_cpus}}\t[Mem]  {float(node_attrs[nodename]["alloc_mem"]):{width_alloc_mem}g}/{node_attrs[nodename]["mem_size"]:{width_mem}g} GiB'

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
    return zip(jobs, cycle(color_pool))


if __name__ == '__main__':
    main()
