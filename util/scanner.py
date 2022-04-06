"""
   Copyright 2022 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from queue import Queue, Empty
from threading import Thread, Lock
from typing import List

import requests

from util import get_logger

logger = get_logger(__name__.split(".", 1)[-1])


class Scanner:

    @staticmethod
    def scan(hosts: List[str], num_workers: int, timeout: float) -> List[str]:
        queue = Queue()
        list_lock = Lock()
        alive_host_list: List[str] = []
        for host in hosts:
            queue.put_nowait(host)
        if num_workers == 0:
            num_workers = len(hosts)
        for _ in range(min(num_workers, len(hosts))):  # no more workers than checks
            worker = ScanWorker(queue, alive_host_list, list_lock, timeout)
            worker.start()
        queue.join()
        return alive_host_list


class ScanWorker(Thread):

    def __init__(self, queue: Queue, alive_host_list: List[str], list_lock: Lock, timeout: float):
        super().__init__()
        self.queue = queue
        self.alive_host_list = alive_host_list
        self.list_lock = list_lock
        self.timeout = timeout

    def run(self):
        while self.queue.not_empty:
            try:
                host = self.queue.get_nowait()
            except Empty:
                return

            try:
                resp = requests.get(host, timeout=self.timeout)
                if not resp.ok or not resp.text.startswith("<!DOCTYPE html><title>SENEC"):
                    break
                with self.list_lock:
                    self.alive_host_list.append(host)
            except Exception as ex:
                logger.debug(host + " - " + str(ex))
                continue
            finally:
                self.queue.task_done()
