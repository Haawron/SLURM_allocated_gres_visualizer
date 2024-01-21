from typing import List, Dict, Tuple
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sty import fg, ef, bg

if __name__.startswith('slurm_gres_viz'):
    from .slurm_objects import Node, Job, GPU
    from .args import args
else:
    from slurm_objects import Node, Job, GPU
    from args import args
from pprint import pprint


cmap = plt.get_cmap('jet')
RED = (255, 50, 0)
YELLOW = (200, 200, 0)


class Displayer:
    def __init__(self, nodes:List[Node], jobs:List[Job], **display_options):
        self.dashboard = DashBoard(nodes, jobs, **display_options)
        self.legend = Legend(jobs, **display_options)

    def show(self):
        self.dashboard.show()
        self.legend.show()


class DashBoard:  # Upper body
    def __init__(self,
        nodes:List[Node], jobs:List[Job],

        show_index:bool=False, show_gpu_memory:bool=False, show_gpu_util:bool=False,
        show_only_mine:bool=False, filter_dict:Dict[str, List[str]]={}
    ):
        self.nodes = nodes
        self.jobs = jobs

        self.show_index = show_index
        self.show_gpu_memory = show_gpu_memory
        self.show_gpu_util = show_gpu_util
        self.show_only_mine = show_only_mine if filter_dict == {} else False
        self.filter_dict = filter_dict

        self.max_num_node_gpus = max(map(lambda node: node.num_gpus_total, self.nodes))
        self.delimiter_within_gpu = '|'
        if sum([self.show_index, self.show_gpu_memory, self.show_gpu_util]) <= 1:
            self.delimiter_between_gpu = ''
        else:
            self.delimiter_between_gpu = ' '
        self.char_fill_hidden = '#'
        self.all_mine_masks = self.get_mine_mask()
        self.all_filter_masks = self.get_filter_mask()
        self.all_occupancy_masks = self.get_occupancy_mask()
        self.all_gpu_items = self.build_items()
        self.all_gpu_items = self.stylize_items(self.all_gpu_items)
        self.widths = self.calculate_widths()

    def show(self):
        lines = [
            f'{node.name:{self.widths["nodename"]}}: '
            f'[GPU] [{node.num_gpus_alloc}/{node.num_gpus_total}] {self.delimiter_between_gpu.join(gpu_items)}      '
            f'[CPU]  {node.num_cpus_alloc:>{self.widths["cpu"]}}/{node.num_cpus_total:{self.widths["cpu"]}}  '
            f'[MEM]  {node.mem_alloc:>{self.widths["mem"]-3}.0f}/{node.mem_total:{self.widths["mem"]}.2f} GiB'
            for node, gpu_items in zip(self.nodes, self.all_gpu_items.values())
        ]
        body = '\n'.join(lines)
        print(body)

    def build_items(self):
        all_gpu_items:Dict[str,List[str]] = {}
        for node in self.nodes:
            mine_masks = self.all_mine_masks[node.name]
            filter_masks = self.all_filter_masks[node.name]
            occupancy_masks = self.all_occupancy_masks[node.name]
            gpu_items:List[str] = []
            for gpu_idx in range(self.max_num_node_gpus):
                is_mine = mine_masks[gpu_idx]
                is_filtered = filter_masks[gpu_idx]
                is_occupied = occupancy_masks[gpu_idx]
                will_be_hidden = (self.show_only_mine and not is_mine) or is_filtered
                if gpu_idx >= node.num_gpus_total:  # pseudo item to align, as colorizer's width varies aligning with width does not work
                    gpu_items.append(' '*len(gpu_item))
                else:
                    gpu_item = []
                    if any([self.show_index, self.show_gpu_memory, self.show_gpu_util]):
                        if self.show_index:
                            gpu_item.append(f'{gpu_idx}')
                        if self.show_gpu_memory:
                            gpu_item.append(f'{node.gpus[gpu_idx].vram_alloc:>4.1f}/{node.gpus[gpu_idx].vram_total:4.1f}GiB')
                        if self.show_gpu_util:
                            util = int(round(node.gpus[gpu_idx].util, 0))
                            gpu_item.append(f'{util:>2d}%' if util < 100 else '100')
                        content = self.delimiter_within_gpu.join(gpu_item)
                        if is_occupied:
                            if will_be_hidden:
                                content = self.char_fill_hidden * len(content)
                        else:  # idle GPUs
                            content = '-' * len(content)
                        gpu_item = '[' + content + ']'
                    else:
                        if is_occupied:
                            if will_be_hidden:
                                gpu_item = self.char_fill_hidden
                            else:
                                gpu_item = '*'
                        else:  # idle GPUs
                            gpu_item = '-'
                    gpu_items.append(gpu_item)
            all_gpu_items[node.name] = gpu_items
        return all_gpu_items

    def stylize_items(self, all_gpu_items):
        for job in self.jobs:
            color = get_color_from_idx(int(job.id))
            is_mine = os.environ['USER'] in job.userid
            for nodename, tres_dict in job.tres_dict.items():
                for gpu_idx in tres_dict['gpus']:
                    is_filtered = self.all_filter_masks[nodename][gpu_idx]
                    will_be_hidden = (self.show_only_mine and not is_mine) or is_filtered
                    if not will_be_hidden:
                        content = colorize(all_gpu_items[nodename][gpu_idx], color)
                        if is_mine:
                            content = make_bold(content)
                        all_gpu_items[nodename][gpu_idx] = content

        # not occupied -> colored into gray
        gray = tuple(100 for _ in range(3))
        for nodename, occupancy_masks in self.all_occupancy_masks.items():
            for gpu_idx, is_occupied in enumerate(occupancy_masks):
                if not is_occupied:  # idle GPUs
                    all_gpu_items[nodename][gpu_idx] = colorize(all_gpu_items[nodename][gpu_idx], gray)

        # TODO: 비정상(not in IDLE, MIXED, ALLOCATED) 노드 취소선
        for node in self.nodes:
            if any([invalid_state in node.states for invalid_state in ['DOWN', 'INVALID']]):
                for gpu_idx in range(node.num_gpus_total):
                    all_gpu_items[node.name][gpu_idx] = colorize(all_gpu_items[node.name][gpu_idx], RED, True)
            elif 'DRAIN' in node.states:
                for gpu_idx in range(node.num_gpus_total):
                    all_gpu_items[node.name][gpu_idx] = colorize(all_gpu_items[node.name][gpu_idx], YELLOW, True)
            else:  # valid node
                pass
        return all_gpu_items

    def calculate_widths(self):
        widths = {
            'nodename': max(map(lambda node: len(node.name), self.nodes)),
            'cpu': max(map(lambda node: np.log10(node.num_cpus_total).astype(int)+1, self.nodes)),
            'mem': 6
            # why don't we have gpu items' width?
            # => as colorizer's width varies aligning with width does not work
        }
        return widths

    def get_mine_mask(self):
        all_mine_masks:Dict[str,List[bool]] = {node.name: [False]*self.max_num_node_gpus for node in self.nodes}
        for job in self.jobs:
            is_mine = os.environ['USER'] in job.userid
            if is_mine:
                for nodename, tres_dict in job.tres_dict.items():
                    for gpu_idx in tres_dict['gpus']:
                        all_mine_masks[nodename][gpu_idx] = True
        return all_mine_masks
    
    def get_filter_mask(self):
        if self.filter_dict == {}:
            return {node.name: [False]*self.max_num_node_gpus for node in self.nodes}
        name_to_job_object = {'user_id':'userid', 'job_id':'id', 'arrayjobid':'arrayjobid', 'arraytaskid':'arraytaskid', 'job_name':'name', 'node_name':'tres_dict'}
        all_filter_masks:Dict[str,List[bool]] = {node.name: [True]*self.max_num_node_gpus for node in self.nodes}
        for job in self.jobs:
            for key, values in self.filter_dict.items():
                _property = getattr(job, name_to_job_object[key])
                for nodename, tres_dict in job.tres_dict.items():
                    for gpu_idx in tres_dict['gpus']:
                        all_filter_masks[nodename][gpu_idx] = \
                            all_filter_masks[nodename][gpu_idx] and \
                            sum([_property == value if sum([c >= '0' and c <= '9' for c in _property])==len(_property) \
                                else  value in _property for value in values ])
        for nodename, filter_masks in all_filter_masks.items():
            for gpu_idx, is_filtered in enumerate(filter_masks):
                all_filter_masks[nodename][gpu_idx] = not all_filter_masks[nodename][gpu_idx]
        return all_filter_masks

    def get_occupancy_mask(self):
        all_occupancy_masks:Dict[str,List[bool]] = {node.name: [False]*self.max_num_node_gpus for node in self.nodes}
        for job in self.jobs:
            for nodename, tres_dict in job.tres_dict.items():
                for gpu_idx in tres_dict['gpus']:
                    all_occupancy_masks[nodename][gpu_idx] = True
        return all_occupancy_masks


class Legend:  # Lower body
    def __init__(self,
            jobs:List[Job],

            show_index:bool=False, show_gpu_memory:bool=False, show_gpu_util:bool=False,
            show_only_mine:bool=False, filter_dict:Dict[str, List[str]]={}
        ):
        self.jobs = jobs
        self.space_placeholder = '@'  # not to be splitted by str.split
        self.delimiter_column = '   '

        self.show_index = show_index
        self.show_gpu_memory = show_gpu_memory
        self.show_gpu_util = show_gpu_util
        self.show_only_mine = show_only_mine if filter_dict == {} else False
        self.filter_dict = filter_dict

        self.default_colnames = ['colors', 'user_id', 'job_id', 'job_arr_id', 'job_arr_task_id', 'job_name', 'node_name', 'gpus', 'cpus', 'mem']
        self.default_display_colnames = [colname.replace('job_arr_task_id', 'arr_idx').upper() for colname in self.default_colnames if colname != 'job_arr_id']
        self.default_aligns = pd.Series(['<', '<', '>', '<', '<', '<', '^', '^', '>', '>'], self.default_colnames)

        self.df, self.display_colnames, self.aligns = self.build_df()
        self.widths = self.calculate_widths(self.df, self.display_colnames)

    def show(self):
        if not self.df.empty:
            df_s = self.df.to_string(max_colwidth=0, index=False)
            lines = [line.split() for line in df_s.split('\n')]
            lines[0] = self.display_colnames
        else:
            lines = [self.display_colnames]
        s = []
        for line in lines:
            ss = []
            for elem, colname in zip(line, self.df.columns):
                ss.append(f'{elem:{self.aligns[colname]}{self.widths[colname]}}'.replace(self.space_placeholder, ' '))
            ss = self.delimiter_column.join(ss)
            s.append(ss)
        whole_width = self.widths.sum() + (self.widths.shape[0]-1)*len(self.delimiter_column)
        print()
        print(f'{" LEGEND ":=^{whole_width}}')
        print('\n'.join(s))

    def build_df(self):
        records = self.build_records_from_jobs(self.jobs)
        df = pd.DataFrame.from_records(records, columns=self.default_colnames[1:])
        if self.show_only_mine:
            df = df[df['user_id'].str.contains(os.environ['USER'])]
        if self.filter_dict != {}:
            for key, values in self.filter_dict.items():
                _df = pd.DataFrame()
                if key == 'user_id' or key == 'job_name' :
                    for value in values:
                        _df = pd.concat([_df, df[df[key].str.contains(value)]])
                else:
                    for value in values:
                        _df = pd.concat([_df, df[df[key] == value]])
                df = pd.merge(df, _df, how='inner',)
        color_legend = df['job_id'].map(lambda jid: colorize('********', get_color_from_idx(int(jid))))  # before the column job_id overwritten
        df['job_id'] = df['job_arr_id'].fillna(df['job_id'])  # firstly with job_arr_id, and overwrite with job_id only for none rows
        del df['job_arr_id']
        df['gpus'] = df['gpus'].replace('', pd.NA).fillna('-')
        df['mem'] = df['mem'].astype(str) + f'{self.space_placeholder}GiB'
        # inserting the color legend
        df.insert(0, 'colors', color_legend)
        # masking multi-node jobs
        duplicates = df.duplicated(subset=['job_id', 'job_arr_task_id'], keep='first')
        df.loc[duplicates, ['colors', 'user_id', 'job_id', 'job_arr_task_id', 'job_name']] = self.space_placeholder

        no_arr_job = df['job_arr_task_id'].replace(self.space_placeholder, pd.NA).isna().all()
        display_colnames = self.default_display_colnames.copy()
        aligns = self.default_aligns.copy()
        if no_arr_job:
            del df['job_arr_task_id']
            del aligns['job_arr_task_id']
            display_colnames.remove('ARR_IDX')
        else:
            df['job_arr_task_id'] = df['job_arr_task_id'].fillna(self.space_placeholder)

        return df, display_colnames, aligns

    def build_records_from_jobs(self, jobs):
        records = []
        for job in jobs:
            for nodename, tres_dict in job.tres_dict.items():
                record = [
                    job.userid, job.id, job.arrayjobid, job.arraytaskid, job.name, nodename,
                    ','.join(map(str, tres_dict['gpus'])), len(tres_dict['cpus']), int(tres_dict['mem'])
                ]
                records.append(record)
        return records

    def calculate_widths(self, df, display_colnames):
        tmp_df_for_calculating_width = pd.concat([df.astype(str), pd.DataFrame([display_colnames], columns=df.columns)], ignore_index=True)
        widths = tmp_df_for_calculating_width.applymap(lambda elem: len(str(elem))).max()
        widths['colors'] = 8
        return widths


def get_color_from_idx(idx:int):
    color = cmap(((11*idx) % 256) / 256)[:-1]  # RGB
    color = list(map(lambda x: int(x*255), color))
    return color


def colorize(source:str, color:List[int], background:bool=False):
    if not background:
        output = fg(*color) + source + fg.rs
    else:
        output = bg(*color) + source + bg.rs
    return output


def make_bold(source:str):
    output = ef.b + source + ef.rs
    return output
