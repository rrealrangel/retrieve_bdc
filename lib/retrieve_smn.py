# -*- coding: utf-8 -*-
"""
Created on Tue Jan 03 10:19:26 2017

@author: rreal
"""

from pathlib2 import Path
import urllib


def build_url(station):
    root = "https://smn.cna.gob.mx/tools/RESOURCES/Diarios/"
    return(root + str(int(station)) + '.txt')


def state_iso(num):
    """Returns the ISO 3166-2 codes for the states of Mexico for a
    given consecutive number as used in the National Climatological
    Database of Mexico (BDCN) by the National Meteorological Service
    (SMN).

    Parameters
        num: integer, float
            The consecutive number by which a state is identified in
            the BDCN. Commonly, these are assiged following an
            alphabetical order.
    """
    numiso = {1: 'agu', 2: 'bcn', 3: 'bcs', 4: 'cam', 5: 'coa',
              6: 'col', 7: 'chp', 8: 'chh', 9: 'cmx', 10: 'dur',
              11: 'gua', 12: 'gro', 13: 'hid', 14: 'jal', 15: 'mex',
              16: 'mic', 17: 'mor', 18: 'nay', 19: 'nle', 20: 'oax',
              21: 'pue', 22: 'que', 23: 'roo', 24: 'slp', 25: 'sin',
              26: 'son', 27: 'tab', 28: 'tam', 29: 'tla', 30: 'ver',
              31: 'yuc', 32: 'zac'}
    return(numiso[num])


for state in range(19, 20):
    parent_dir = str(state).zfill(2) + '_' + state_iso(state)
    output_dir = Path('/home/rrealrangel/Escritorio/smn_v2018.06') / parent_dir
    output_dir.mkdir(exist_ok=True)
    for seq in range(1, 999):
        station = format(state, '02d') + format(seq, '03d')
        output_file = output_dir / (str(station).zfill(5) + '.txt')
        test_file = urllib.URLopener()

        try:
            print("Trying to retrieve station {}".format(str(station).zfill(5)))
            test_file.retrieve(build_url(station), str(output_file))

        except IOError:
            pass
