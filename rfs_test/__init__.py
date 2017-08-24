# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

###################################################################################################
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
####################################################################################################

import logger
from rfs_test import TEST_protocol_details
from rfs_test import TEST_datamodel_schema
from rfs_test_in_progress import TEST_service_details
from rfs_test_in_progress import TEST_security

###################################################################################################
# Name: run(sut)
# sut == the instance of SUT type obj (rf_sut.py) for which these assertions are being run.
###################################################################################################
def run(sut):
    # create logger obj
    log = logger.Log()
    # initialize assertions excel sheet at this point
    log.init_xl()
    ## Open/initialize the log files
    log.assertion_log('OPEN', None, sut.SUT_prop, sut.Redfish_URIs['Service_Root'])
    # Run assertions
    TEST_protocol_details.run(sut, log)
    TEST_datamodel_schema.run(sut, log)
    #TEST_service_details.run(sut, log)
    #TEST_security.run(sut, log)
    ## end: assertion verification
    ## close log files
    #-log.assertion_log('CLOSE', None)
# end run
