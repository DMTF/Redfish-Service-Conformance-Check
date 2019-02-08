# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

###################################################################################################
# Name: sample_run
# Description: This sample module provides steps to run the client tool in order to run assertions
#   on SUT.
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
###################################################################################################

import rf_client
import rfs_test 
import logger

def run(self):
    # create logger obj                                
    log = logger.Log() 
    # initialize assertions excel sheet at this point
    log.init_xl()
    ## Open/initialize the log files
    log.assertion_log('OPEN', None, self.SUT_prop, self.Redfish_URIs['Service_Root'])
    rfs_test.TEST_protocol_details.Assertion_6_3_1(self, log)
    ## close log files
    log.assertion_log('CLOSE', None)

if __name__ == "__main__":
    SUTs = rf_client.get_sut_prop()
    for sut_prop in SUTs:
        if sut_prop:
            #initalize tool before anything else..this sets up all the necc variables for this sut in this tool
            sut = rf_client.setup_tool(sut_prop)  
            if sut:               
                #run(sut)
                rfs_test.run(sut)
        else:
            print('No SUT found in properties.json. Please add an SUT following the format provided in readme.txt and try running the tool again')
            exit(0)

                
