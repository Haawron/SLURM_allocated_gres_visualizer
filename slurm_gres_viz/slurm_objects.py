from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
from prometheus_client.parser import text_string_to_metric_families
from parsers import parse_jobstring, parse_nodestring


class Job:
    def __init__(self, job_string):
        self.job_string = job_string
        self.userid, self.jobid, self.arrayjobid, self.arraytaskid, self.jobname, self.job_tres_dict = parse_jobstring(self.job_string)


class GPU:
    def __init__(self, dcgm_stat:Dict[str,float]):
        # self.gpuname = gpuname  # TODO: gpu name from slurm.conf??
        self.gpuutil = dcgm_stat['DCGM_FI_DEV_GPU_UTIL']
        self.vram_used = dcgm_stat['DCGM_FI_DEV_FB_USED']
        self.vram_total = dcgm_stat['DCGM_FI_DEV_FB_FREE'] + self.vram_used


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
        nodename, num_cpus, num_gpus, mem_used, mem_total = parse_nodestring(self.node_string)
        self.nodename = nodename  # already have, exporter
        self.public_ip = node_ip_dict[self.nodename]  # given
        self.node_metrics = self.get_node_metrics()
        self.gpu_metrics, self.gpus = self.get_gpu_metrics()

        self.num_cpus = num_cpus  # node_string
        self.num_gpus = num_gpus  # node_string
        self.cpu_loads = [
            self.node_metrics['node_load1'].samples[0].value,
            self.node_metrics['node_load5'].samples[0].value,
            self.node_metrics['node_load15'].samples[0].value,
        ]  # node_string, exporter[v]
        self.mem_total = mem_total  # node_string
        self.mem_used = mem_used  # node_string[v], exporter


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
