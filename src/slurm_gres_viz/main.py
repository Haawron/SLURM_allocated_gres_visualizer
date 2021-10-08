from itertools import cycle
import os
from .args import args


def keyval_split(string):  # 'key=value' -> ('key', 'value')
    item = string.split('=', 1)
    if len(item)==1:  # string = 'key='
        item.append('')
    return item


def parse_scontrol(scontrol_string):
    output = []
    for item in scontrol_string:
        attrs = {}
        item = item.split()  # item = ['JobId=454',...]
        for attr_str in item:  # attr_str = 'JobId=454'
            key, value = keyval_split(attr_str)
            if '=' in value:  # value = 'cpu=32,node=1,billing=32'
                keyvals = [keyval_split(attr_str_) for attr_str_ in value.split(',')]
                value = {key: val for key, val in keyvals}
            attrs[key] = value
        output.append(attrs)
    return output  # list of dicts


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


def prettify_gres(jobs, nodes, color_pool):
    stars = get_stars(jobs, nodes, color_pool)
    max_gres = max([len(val) for _, val in stars.items()])
    max_nodename = max([len(node['NodeName']) for node in nodes])
    for nodename, gres in stars.items():
        print(f'{nodename:<{max_nodename}}: {gres:<{max_gres}}')


def get_stars(jobs, nodes, color_pool):  # 'gpu(IDX:0-1,3-5,7)' -> ******* with colors
    jobs_and_colors = get_jobs_and_colors(jobs, color_pool)
    stars = {node['NodeName']: get_components(node) for node in nodes}
    for job, color in jobs_and_colors:
        nodename = job['NodeList']
        gpu_indices = parse_gres(job['GRES'])
        for gpu_idx in gpu_indices:
            stars[nodename][gpu_idx] = f'{color}{stars[nodename][gpu_idx]}{bcolors.CEND}'
    stars = {name: ''.join(gres) for name, gres in stars.items()}
    return stars


def get_components(node):
    num_gres = int(node['Gres'].split(':')[-1]) 
    if args.index:
        return [f'[{str(i)}]' for i in range(num_gres)]
    else:
        return ['*'] * num_gres


def get_jobs_and_colors(jobs, color_pool):
    return zip(jobs, cycle(color_pool))


def parse_gres(gres_string):  # 'gpu(IDX:0-1,3)' -> [0, 1, 3]
    if gres_string.startswith('gpu'):
        indices = gres_string[:-1].split(':')[-1]  # '0-1,3'
        indices = indices.split(',')  # ['0-1', '3']
        output = []
        for idx in indices:
            if '-' in idx:  # '0-1'
                start, end = map(int, idx.split('-'))
                output += list(range(start, end+1))
            else:  # '3'
                output += [int(idx)]
        return output


def print_legends(jobs, color_pool):
    for job in jobs:
        job['GRES_print'] = ','.join(map(str, parse_gres(job['GRES'])))
    field_names = ['COLORS', 'USER_ID', 'JOB_ID', 'Job_NAME', 'NODE_NAME', 'ALLOCATED_GPUS']
    correspondences = [None, 'UserId', 'JobId', 'JobName', 'NodeList', 'GRES_print']
    
    fields = [{'name': field_name, 'corresponds_to': correspondence} for field_name, correspondence in zip(field_names, correspondences)]
    fields[0]['width'] = 8
    for field in fields[1:]:
        field['width'] = get_col_width(jobs, field['corresponds_to'], field['name'])

    delimiter = '  '
    width = sum(field['width'] for field in fields) + (len(fields)-1)*len(delimiter)
    print(f'\n{" LEGENDS ":=^{width}}')

    jobs_and_colors = get_jobs_and_colors(jobs, color_pool) 
    header = delimiter.join([f'{field["name"]:{field["width"]}s}' for field in fields])
    body = '\n'.join([
        delimiter.join(
            [f'{color}********{bcolors.CEND}']
            + [f"{job[field['corresponds_to']]:<{field['width']}}" for field in fields[1:]])
        for job, color in jobs_and_colors
    ])
    print(header)
    print(body)


def get_col_width(jobs, field, field_name):
    return max([len(job[field]) for job in jobs] + [len(field_name)])


def main():
    jobs_string = os.popen('scontrol show job -d').read().strip().replace('\n\n', 'BREAK').split('BREAK')
    nodes_string = os.popen('scontrol show nodes').read().strip().replace('\n\n', 'BREAK').split('BREAK')

    jobs = parse_scontrol(jobs_string)  # list of dicts
    nodes = parse_scontrol(nodes_string)  # list of dicts
    jobs = [job for job in jobs if job['JobState']=='RUNNING']  # filter RUNNING jobs
    color_pool = [val for key, val in bcolors.__dict__.items() if key.startswith('C') and key!='CEND']

    prettify_gres(jobs, nodes, color_pool)
    print_legends(jobs, color_pool)


if __name__ == '__main__':
    main()
