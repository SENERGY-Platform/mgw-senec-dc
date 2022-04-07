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
import datetime
import typing

import rfc3339

from util import SenecDevice


def handle_energy(device: SenecDevice, *args, **kwargs) -> typing.Dict:
    senec = device.get_senec()

    senec.update()
    time = datetime.datetime.now()
    resp = {
        "state": senec.system_state,
        "house_power": senec.house_power, # Brutto Consumption W
        "solar_power": senec.solar_generated_power, # Brutto Generation W
        "total_solar_energy": senec.solar_total_generated, # Brutto Generation kWh
        "total_house_energy": senec.house_total_consumption, # Brutto Consumption kWh
        "grid": {
            "state_power": senec.grid_state_power, # Delta W
            "imported_power": senec.grid_imported_power, # Netto Consumption W
            "exported_power": senec.grid_exported_power, # Netto Generation W
            "total_import": senec.grid_total_import, # Netto Consumption kWh
            "total_export": senec.grid_total_export, # Netto Generation kWh
        },
        "battery": {
            "charge_percent": senec.battery_charge_percent, # Device, Lifetime %
            "charge_power": senec.battery_charge_power, # Generation W, Charge Power
            "discharge_power": senec.battery_discharge_power, # Consumption W, Charge Power
            "state_power": senec.battery_state_power, # Delta W, Charge Power
            "total_charged": senec.battery_total_charged, # Device kWh, Charge Energy Function
            "total_discharged": senec.battery_total_discharged, # Device kWh, Discharge Energy Function
        },
        "time": rfc3339.format(time, utc=True)
    }
    return resp
