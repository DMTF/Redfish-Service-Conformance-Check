# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

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
from rfs_test import TEST_accountservice_schema
from rfs_test import TEST_assembly_schema
from rfs_test import TEST_computersystem_schema
from rfs_test import TEST_actioninfo_schema
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
    if 'SingleAssertion' in sut.SUT_prop and len(sut.SUT_prop.get('SingleAssertion')) > 0:
        # Run single assertion
        run_single([TEST_protocol_details, TEST_datamodel_schema], sut, log)
    else:
        # Run all assertions
        #TEST_protocol_details.run(sut, log) # Takes a long time. 
        #TEST_security.run(sut, log) # Assertion: 9.3.1.4 is lagging
        #TEST_service_details.run(sut, log) # This test is running fine
        
        #TEST_computersystem_schema.run(sut, log)
        #TEST_accountservice_schema.run(sut, log)
        #TEST_assembly_schema.run(sut, log)
        TEST_actioninfo_schema.run(sut, log)
        #TEST_attributeregistry_schema.run(sut, log)
        # end: assertion verification
    ## close log files
    #-log.assertion_log('CLOSE', None)
# end run


###################################################################################################
# Name: run_single(modules, sut, log)
# Run a single assertion. The 'SingleAssertion' property in the SUT config specifies the name of
# the assertion function to run.
# modules == the list of modules to search for the named assertion
# sut == the instance of SUT type obj (rf_sut.py) for which the assertion is being run
# log ==  the log instance to use for logging results
###################################################################################################
def run_single(modules, sut, log):
    if 'SingleAssertion' in sut.SUT_prop and len(sut.SUT_prop.get('SingleAssertion')) > 0:
        assertion = sut.SUT_prop.get('SingleAssertion')
    else:
        print('ERROR: run_single() called to run single assertion, but no "SingleAssertion" property found in SUT')
        return
    func = None
    for mod in modules:
        if hasattr(mod, assertion) and callable(getattr(mod, assertion)):
            func = getattr(mod, assertion)
            break
    if func is not None:
        print('Running single assertion "{}"'.format(assertion))
        func(sut, log)
    else:
        print('ERROR: "SingleAssertion" property was specified in config, but function named "{}" was not found'
              .format(assertion))
# end run_single
