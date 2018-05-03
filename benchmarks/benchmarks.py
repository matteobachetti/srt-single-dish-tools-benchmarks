# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.
from __future__ import (absolute_import, division,
                        print_function)
import numpy as np

import os

from srttools import ScanSet
from srttools.simulate import simulate_map
from srttools.io import mkdir_p
import os

def _2d_gauss(x, y, sigma=2.5 / 60.):
    """A Gaussian beam"""
    return np.exp(-(x ** 2 + y ** 2) / (2 * sigma**2))


def gauss_src_func(x, y):
    return 25 * _2d_gauss(x, y, sigma=2.5 / 60)


def sim_config_file(filename, add_garbage=False, prefix=None):
    """Create a sample config file, to be modified by hand."""
    string0 = """
[local]
workdir : .
datadir : .

[analysis]
projection : ARC
interpolation : spline
prefix : test_
list_of_directories :
    gauss_ra
    gauss_dec
    defective
"""
    string1 = """
calibrator_directories :
    calibration
"""
    string2 = """

skydip_directories :
    gauss_skydip

noise_threshold : 5

pixel_size : 0.8

[debugging]

debug_file_format : eps

"""
    if prefix is None:
        prefix = os.getcwd()
    import tempfile
    string = string0
    with open(filename, 'w') as fobj:
        print(string0, file=fobj)
        if add_garbage:
            for _ in range(100):
                garbage = '    ' + \
                    tempfile.NamedTemporaryFile(prefix=prefix).name[1:]
                print(garbage, file=fobj)
                string += garbage + '\n'
        print(string1, file=fobj)
        string += string1
        if add_garbage:
            for _ in range(100):
                garbage = '    ' + \
                    tempfile.NamedTemporaryFile(prefix=prefix).name[1:]
                print(garbage, file=fobj)
                string += garbage + '\n'
        print(string2, file=fobj)
        string += string2
    return string


def sim_map(obsdir_ra, obsdir_dec):
    simulate_map(count_map=gauss_src_func,
                 length_ra=30.,
                 length_dec=30.,
                 outdir=(obsdir_ra, obsdir_dec), mean_ra=180,
                 mean_dec=45, speed=1.5,
                 spacing=0.5, srcname='Dummy', channel_ratio=0.8,
                 baseline="flat")


curdir = os.path.dirname(__file__)
datadir = os.path.join(curdir, 'data')
sim_dir = os.path.join(datadir, 'sim')

obsdir_ra = os.path.join(datadir, 'sim', 'gauss_ra')
obsdir_dec = os.path.join(datadir, 'sim', 'gauss_dec')
config_file = \
    os.path.abspath(os.path.join(sim_dir, 'test_config_sim.ini'))
caldir = os.path.join(datadir, 'sim', 'calibration')
simulated_flux = 0.25


# First off, simulate a beamed observation  -------
class TimeImager:
    def setup(klass):
        import os

        mkdir_p(datadir)
        mkdir_p(sim_dir)
        sim_config_file(config_file, add_garbage=True,
                        prefix="./")

        mkdir_p(obsdir_ra)
        mkdir_p(obsdir_dec)
        print('Fake map: Point-like (but Gaussian beam shape), '
              '{} Jy.'.format(simulated_flux))

        sim_map(obsdir_ra, obsdir_dec)

    def time_1_load_image(self):
        scanset = ScanSet(config_file, nosub=False,
                                norefilt=False,
                                debug=True)

    def teardown(self):
        import shutil
        shutil.rmtree(datadir)


class MemImager:
    def setup(klass):
        mkdir_p(datadir)
        mkdir_p(sim_dir)
        sim_config_file(config_file, add_garbage=True,
                        prefix="./")

        mkdir_p(obsdir_ra)
        mkdir_p(obsdir_dec)
        print('Fake map: Point-like (but Gaussian beam shape), '
              '{} Jy.'.format(simulated_flux))
        sim_map(obsdir_ra, obsdir_dec)

    def mem_1_load_image(self):
        scanset = ScanSet(config_file, nosub=False,
                                norefilt=False,
                                debug=True)
    def teardown(self):
        import shutil
        shutil.rmtree(datadir)

# class TimeSuite:
#     """
#     An example benchmark that times the performance of various kinds
#     of iterating over dictionaries in Python.
#     """
#     def setup(self):
#         self.d = {}
#         for x in range(500):
#             self.d[x] = None
#
#     def time_keys(self):
#         for key in self.d.keys():
#             pass
#
#     def time_iterkeys(self):
#         for key in self.d.iterkeys():
#             pass
#
#     def time_range(self):
#         d = self.d
#         for key in range(500):
#             x = d[key]
#
#     def time_xrange(self):
#         d = self.d
#         for key in xrange(500):
#             x = d[key]


