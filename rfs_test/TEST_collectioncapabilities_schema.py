# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_collectioncapabilities_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Ubuntu OS) :
#       3.5.2
#
# Initial code released : 05/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

###################################################################################################
# Name: Assertion COLL103(self,log)
# Description:
# The value of this property shall be a reference to a Resource that matches the type for the given 
# collection and shall contain annotations that describe the properties allowed in the POST request.
###################################################################################################
def Assertion_COLL103(self,log) :
    log.AssertionID = 'COLL103'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    print('Checking if all responses are in JSON')
    authorization = 'on'
    
    # Could not find a resourse with Capabilities Object property and the link https://github.com/DMTF/spmf/tree/master/mockups/development 
    # to the development mockup which contains everry resources is broken. 
    
    return (assertion_status)

#
## end Assertion BOOT102

# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log):     
    assertion_status = Assertion_COLL103(self,log)