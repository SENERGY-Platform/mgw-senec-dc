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
from typing import List


def parse_mac(bytes: List[int]) -> str:
    if len(bytes) != 6:
        raise RuntimeError(f'expected 6 bytes, not {len(bytes)}')
    mac = ""
    for b in bytes:
        if len(mac) > 0:
            mac = "-" + mac
        mac = mac + f'{b:0>2X}'
    return mac
