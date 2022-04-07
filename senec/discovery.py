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

import asyncio
import ipaddress
import threading
import time
from typing import Dict, List

import aiohttp as aiohttp
import pysenec
from mgw_dc.dm import device_state

from util import get_logger, conf, diff, SenecDevice

__all__ = ("Discovery",)

from util.device_manager import DeviceManager
from util.mac import parse_mac
from util.scanner import Scanner

logger = get_logger(__name__.split(".", 1)[-1])


class Discovery(threading.Thread):
    def __init__(self, device_manager: DeviceManager):
        super().__init__(name="discovery", daemon=True)
        self._device_manager = device_manager

    @staticmethod
    async def get_senec_devices() -> Dict[str, SenecDevice]:
        logger.info("Starting scan")
        devices: Dict[str, SenecDevice] = {}

        hosts: List[str] = []
        try:
            subnet = ipaddress.ip_network(conf.Discovery.subnet)
            for host in subnet:
                hosts.append(str(host))
        except Exception as e:
            logger.info(f'Skipping range scan, could not setup: {e}')

        detected = Scanner.scan(hosts=hosts, num_workers=conf.Discovery.num_workers,
                                 timeout=conf.Discovery.timeout)

        hosts = str(conf.Discovery.ip_list).split(',')
        for host in detected:
            hosts.append(host)

        unique_hosts: Dict[str, any] = {}
        for host in hosts:
            unique_hosts[host] = {}

        devs: Dict[str, pysenec.Senec] = {}
        for ip in unique_hosts.keys():
            if len(ip) == 0: continue
            try:
                dev = pysenec.Senec(ip, aiohttp.ClientSession())
                await dev.read_senec_v21_all()
                devs[ip] = dev
            except Exception as e:
                logger.warning(f"Could not discover device with ip {ip} : {e}")
        for addr, dev in devs.items():
            mac = parse_mac(dev._raw["WIZARD"]["MAC_ADDRESS_BYTES"])
            logger.info("Discovered '" + mac + "' at " + dev.host)
            id = conf.Discovery.device_id_prefix + mac
            attributes = [
                {"key": "network/ip", "value": dev.host},
            ]
            devices[id] = SenecDevice(id=id, name="Senec Home " + mac, type=conf.Senergy.dt_box, state=device_state.online,
                                     senec_device=dev, attributes=attributes)

        logger.info("Discovered " + str(len(devices)) + " devices")
        return devices

    async def _refresh_devices(self):
        try:
            senec = await self.get_senec_devices()
            stored_devices = self._device_manager.get_devices()

            new_devices, missing_devices, existing_devices = diff(stored_devices, senec)
            if new_devices:
                for device_id in new_devices:
                    self._device_manager.handle_new_device(senec[device_id])
            if missing_devices:
                for device_id in missing_devices:
                    self._device_manager.handle_missing_device(stored_devices[device_id])
            if existing_devices:
                for device_id in existing_devices:
                    self._device_manager.handle_existing_device(stored_devices[device_id])
            self._device_manager.set_devices(devices=senec)
        except Exception as ex:
            logger.error("refreshing devices failed - {}".format(ex))

    def run(self) -> None:
        logger.info("starting {} ...".format(self.name))
        asyncio.run(self.discovery_loop())

    async def discovery_loop(self):
        await self._refresh_devices()
        last_discovery = time.time()
        while True:
            if time.time() - last_discovery > conf.Discovery.scan_delay:
                last_discovery = time.time()
                await self._refresh_devices()
            time.sleep(conf.Discovery.scan_delay / 100)  # at most 1 % too late
