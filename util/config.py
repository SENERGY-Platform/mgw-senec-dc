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

__all__ = ("conf",)

import simple_env_var


@simple_env_var.configuration
class Conf:
    @simple_env_var.section
    class MsgBroker:
        host = "message-broker"
        port = 1883

    @simple_env_var.section
    class Logger:
        level = "debug"
        enable_mqtt = False

    @simple_env_var.section
    class Client:
        clean_session = False
        keep_alive = 30
        id = "senec-dc"

    @simple_env_var.section
    class Discovery:
        scan_delay = 3600
        timeout = 2
        subnet = '10.42.0.0/24'
        num_workers = 0
        ip_list = ""
        device_id_prefix = "senec-"

    @simple_env_var.section
    class StartDelay:
        enabled = False
        min = 5
        max = 20

    @simple_env_var.section
    class Senergy:
        dt_box = "urn:infai:ses:device-type:afe50ee4-8588-4505-a019-33b1d947a3bf"
        events_energy_seconds = 10
        service_energy = "energy"

conf = Conf()

if not conf.Senergy.dt_box:
    exit('Please provide SENERGY device types')
