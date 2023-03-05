from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
from prometheus_client.parser import text_string_to_metric_families
if __name__.startswith('slurm_gres_viz'):
    from .parsers import parse_jobstring, parse_nodestring, MiB2GiB
else:  # for test
    from parsers import parse_jobstring, parse_nodestring, MiB2GiB


class Job:
    def __init__(self, job_string):
        self.job_string = job_string
        self.userid, self.id, self.arrayjobid, self.arraytaskid, self.name, self.tres_dict = parse_jobstring(self.job_string)


class GPU:
    def __init__(self, dcgm_stat:Dict[str,float]):
        # self.gpuname = gpuname  # TODO: gpu name from slurm.conf??
        self.util = float(dcgm_stat['DCGM_FI_DEV_GPU_UTIL'])
        self.vram_alloc = MiB2GiB(float(dcgm_stat['DCGM_FI_DEV_FB_USED']))
        self.vram_total = MiB2GiB(float(dcgm_stat['DCGM_FI_DEV_FB_FREE'])) + self.vram_alloc


class Node:
    def __init__(self, node_string:str, node_ip_dict:Dict[str,str]):
        """# Vars (example)
        @nodename: `"vll3"`
        @num_cpus: `96`
        @num_gpus: `8`
        @mem_total: `336833`
        @public_ip: `"xxx.xxx.xxx.xxx"`
        @gpu_infos: `[{"gpuname": "", "gpuutil": 83, "vram_used": 18832, "vram_total": 24080}, ...]`
        @cpu_load: `2.10`
        @mem_used: `61440`
        """
        self.node_string = node_string
        nodename, num_cpus_alloc, num_cpus_total, num_gpus_total, mem_alloc, mem_total = parse_nodestring(self.node_string)
        self.name = nodename  # already have, exporter
        self.public_ip = node_ip_dict[self.name]  # given
        self.node_metrics = self.get_node_metrics()
        self.gpu_metrics, self.gpus = self.get_gpu_metrics()

        self.num_cpus_total = num_cpus_total  # node_string
        self.num_cpus_alloc = num_cpus_alloc  # node_string
        self.num_gpus_total = num_gpus_total  # node_string
        self.cpu_loads = [
            self.node_metrics['node_load1'].samples[0].value,
            self.node_metrics['node_load5'].samples[0].value,
            self.node_metrics['node_load15'].samples[0].value,
        ]  # node_string, exporter[v]
        self.mem_alloc = mem_alloc  # node_string[v], exporter
        self.mem_total = mem_total  # node_string

    def get_node_metrics(self) -> dict:
        response = requests.get(f'http://{self.public_ip}:9100/metrics')  # node exporter
        if response.ok:
            metrics = self.html2metrics(response.text)
            return {metric.name: metric for metric in metrics}
        else:
            raise  # The metric server does not respond

    def get_gpu_metrics(self) -> Tuple[dict, List[GPU]]:
        response = requests.get(f'http://{self.public_ip}:9400/metrics')  # dcgm exporter
        if response.ok:
            gpu_metrics = self.html2metrics(response.text)
            gpus = self.metrics2gpu_objs(gpu_metrics)
            return gpu_metrics, gpus
        else:
            raise  # The metric server does not respond

    def metrics2gpu_objs(self, metrics) -> List[GPU]:
        gpu_indices = []
        for metric in metrics:
            if metric.samples and 'gpu' in metric.samples[0].labels:
                gpu_indices.append(metric.samples[0].labels['gpu'])
        num_gpus = len(set(gpu_indices))
        dcgm_stats:List[Dict[str,float]] = [{} for _ in range(num_gpus)]
        for metric in metrics:
            if metric.samples and 'gpu' in metric.samples[0].labels:
                sample = metric.samples[0]
                gpu_idx = int(sample.labels['gpu'])
                dcgm_stats[gpu_idx][sample.name] = sample.value
        return [GPU(dcgm_stat) for dcgm_stat in dcgm_stats]

    def html2metrics(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        metrics = list(text_string_to_metric_families(soup.get_text()))
        return metrics
