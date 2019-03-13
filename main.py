# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 23:30:50 2018

@author: r.realrangel
"""
from pathlib2 import Path

import lib.data_manager as dmgr

config = dmgr.Configurations('config.toml')
input_list = dmgr.list_inputs(input_dir=config.input_dir, extension='.txt')

for input_file in input_list[2022:]:
    # ???: There is an error detected on 1899/12/30 (line 8334).
    # ???: Instead the date string, there is the string "12:00:00".
    # ???: This issue was detected in files 09048.txt and 14030.txt.
    # FIXME: Consider this situation for v1.0.1
    X = dmgr.read_bdcn_file(input_file=input_file)
    output_dir = Path(config.output_dir) / str(input_file).split('/')[-2]
    output_dir.mkdir(parents=False, exist_ok=True)
    X.to_netcdf(output_dir / ('bdc_100_' + input_file.stem + '.nc4'))
