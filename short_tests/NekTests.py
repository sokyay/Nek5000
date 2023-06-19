#!/usr/bin/env python3

import sys
from shutil import copyfile
import os

if sys.version_info < (3, 6):
    print("Sorry, requires Python > 3.6")
    sys.exit(1)

from lib.nekTestCase import (
    NekTestCase,
    pn_pn_parallel,
    pn_pn_2_parallel,
    pn_pn_serial,
)

###############################################################################


class Tools(NekTestCase):
    def setUp(self):

        self.build_tools(["all"])

    @pn_pn_parallel
    def test_PnPn_Parallel(self):
        self.assertDelayedFailures()


###############################################################################

class RANSChannel(NekTestCase):
    example_subdir = "RANSChannel"
    case_name = "chan"

    def setUp(self):
        # Default SIZE parameters. Can be overridden in test cases
        self.size_params = dict(
            ldim="2", lx1="8", lxd="12", lx2="lx1-0", lelg="96", lx1m="lx1", ldimt="3"
        )

        self.build_tools(["genmap"])
        self.run_genmap()

    @pn_pn_parallel
    def test_Std_ktau(self):
        self.config_size()
        self.build_nek()
        self.config_parfile({"GENERAL": {"userParam01": "4"}})
        self.config_parfile({"GENERAL": {"startFrom": "ktau.fld + time=0"}})
        self.run_nek(step_limit=None)

        xerr = self.get_value_from_log("u_tau", column=-1, row=-1)
        dnsval = 4.1487e-2
        relerr = abs(xerr-dnsval)/dnsval

        self.assertAlmostEqualDelayed(
            relerr, target_val=0.0, delta=1e-02, label="u_tau"
        )

        self.assertDelayedFailures()



    @pn_pn_parallel
    def test_Reg_komega(self):
        self.config_size()
        self.build_nek()
        self.config_parfile({"GENERAL": {"userParam01": "0"}})
        self.config_parfile({"GENERAL": {"startFrom": "komega.fld + time=0"}})
        self.run_nek(step_limit=None)

        xerr = self.get_value_from_log("u_tau", column=-1, row=-1)
        dnsval = 4.1487e-2
        relerr = abs(xerr-dnsval)/dnsval

        self.assertAlmostEqualDelayed(
            relerr, target_val=0.0, delta=1e-02, label="u_tau"
        )

        self.assertDelayedFailures()

###############################################################        

class wallfunc(NekTestCase):
    example_subdir = "wallfunc"
    case_name = "chan"

    def setUp(self):
        # Default SIZE parameters. Can be overridden in test cases
        self.size_params = dict(
            ldim="2", lx1="6", lxd="12", lx2="lx1-0", lelg="60", lx1m="lx1", ldimt="4", lhis="1001"
        )

        self.build_tools(["genmap"])
        self.run_genmap()

    @pn_pn_parallel
    def test_Std_ktau_pfalse(self):
        self.config_size()
        self.build_nek()
        self.run_nek(step_limit=None)

        xerr = self.get_value_from_log("u_tau", column=-1, row=-1)
        dnsval = 4.1487e-2
        relerr = abs(xerr-dnsval)/dnsval

        self.assertAlmostEqualDelayed(
            relerr, target_val=0.0, delta=6e-02, label="u_tau"
        )

        self.assertDelayedFailures()

###############################################################        

class PipeRANS(NekTestCase):
    example_subdir = "PipeRANS"
    case_name = "pipe"

    def setUp(self):
        # Default SIZE parameters. Can be overridden in test cases
        self.size_params = dict(
            ldim="3", lx1="8", lxd="12", lx2="lx1-0", lelg="5000", lx1m="lx1", ldimt="6", lhis="1001"
        )

        self.build_tools(["genmap"])
        self.run_genmap()

    @pn_pn_parallel
    def test_Std_ktau(self):
        self.config_size()
        self.build_nek()
        self.config_parfile({"GENERAL": {"userParam01": "4"}})
        self.config_parfile({"GENERAL": {"startFrom": "ktau.fld + time=0"}})
        self.run_nek(step_limit=None)

        xerr = self.get_value_from_log("u_tau", column=-1, row=-1)
        dnsval = 0.0530 # 19k Re (5% error (goes down to 3% for 5k Re))

        relerr = abs(xerr-dnsval)/dnsval

        self.assertAlmostEqualDelayed(
            relerr, target_val=0.0, delta=1e-02, label="u_tau"
        )

        self.assertDelayedFailures()



    @pn_pn_parallel
    def test_Reg_komega(self):
        self.config_size()
        self.build_nek()
        self.config_parfile({"GENERAL": {"userParam01": "0"}})
        self.config_parfile({"GENERAL": {"startFrom": "komega.fld + time=0"}})
        self.run_nek(step_limit=None)

        xerr = self.get_value_from_log("u_tau", column=-1, row=-1)
        dnsval = 0.0530 # 19k Re (5% error)
        relerr = abs(xerr-dnsval)/dnsval

        self.assertAlmostEqualDelayed(
            relerr, target_val=0.0, delta=1e-02, label="u_tau"
        )

        self.assertDelayedFailures()

    ###############################################################
if __name__ == "__main__":
    import unittest
    import argparse

    # Get arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--f77",
        default="mpif77",
        help="The Fortran 77 compiler to use [default: mpif77]",
    )
    parser.add_argument(
        "--cc", default="mpicc", help="The C compiler to use [default: mpicc]"
    )
    parser.add_argument(
        "--ifmpi",
        default="true",
        choices=["true", "false"],
        help="Enable/disable parallel tests with MPI [default: true]",
    )
    parser.add_argument(
        "--nprocs",
        default="4",
        help="Number of processes to use for MPI tests [default: 4]",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # # Set environment
    os.environ["CC"] = args.cc
    os.environ["FC"] = args.f77
    os.environ["IFMPI"] = args.ifmpi
    os.environ["PARALLEL_PROCS"] = args.nprocs
    if args.verbose:
        os.environ["VERBOSE_TESTS"] = "true"
        ut_verbose = 2
    else:
        os.environ["VERBOSE_TESTS"] = "false"
        ut_verbose = 1

    testList = (
        Tools,
        RANSChannel,
        wallfunc,
    )

    suite = unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(t) for t in testList]
    )
    unittest.TextTestRunner(verbosity=ut_verbose, buffer=True).run(suite)
    
