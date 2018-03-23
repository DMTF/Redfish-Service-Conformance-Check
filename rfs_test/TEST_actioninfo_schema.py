# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_actioninfo_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Windows OS) :
#       3.5.2
#
# Initial code released : 01/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

import urllib3
import json
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from time import gmtime, strftime

accSerData = None

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.2.2"


###################################################################################################
# Name: Assertion_ACTI104(self, log) :Action Info                                          
# Assertion text: 
#This property shall return true if the parameter is required to be present to perform the 
#associated Action, and shall be false if the parameter is not required (optional) to perform the
#associated Action.
###################################################################################################

'''
Step 1: Try performing an action without the parameter.
Step 2: If Step 1 failed and Required property is False, fail the assertion. 
Step 3: Else, pass the assertion. 
'''

## end Assertion_ACTI104

#Testing

def run(self, log):

    assertion_status = Assertion_ACTI104(self, log)


    

    
    

    
    



    
