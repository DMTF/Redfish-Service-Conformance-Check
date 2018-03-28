# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_assembly_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Windows OS) :
#       3.5.2
#
# Initial code released : 02/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

###################################################################################################
# Name: Assertion_ASSE114(self, log) : Assembly                                          
# Assertion text: 
#The value of this property shall be a URI at which the Service provides for the download of the 
#OEM-specific binary image of the assembly data.  An HTTP GET from this URI shall return a response 
#payload of MIME time application/octet-stream. An HTTP PUT to this URI, if supported by the 
#Service, shall replace the binary image of the assembly.
###################################################################################################

'''
Step 1: Try performing an HTTP GET on BinaryDataURI
Step 2: If Step 1 returns MIME time application/octet-stream proceed to STEP 3 else fail the 
assertion
Step 3: Perform an HTTP PUT request to the URI obtained from Step 1 if supported else WARN. 
Step 4: If STEP 3 replaces the binary image of the assembly, pass the assertion. 

'''

def Assertion_ASSE114(self, log):

    log.AssertionID = 'ASSE114'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(
        '/redfish/v1/Assembly', rq_headers, authorization)

    try:
        binaryDataURI = json_payload['BinaryDataURI']

        json_payload, headers, status = self.http_GET(
            binaryDataURI, rq_headers, authorization)

        if headers['Content-Type'] == 'application/octet-stream': 
            json_payload, headers, status = self.http_PUT(
            binaryDataURI, rq_headers, authorization)

            if status == 405: 
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'BinaryDataURI\'  HTTP PUT Request not supported %s" % (
                '/redfish/v1/Assembly'))
                return assertion_status
            else:
                # Check for binary image replacement unknown. 
                assertion_status = log.PASS
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', "Assertion Passed")
                return assertion_status

        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion Failed")
            return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'BinaryDataURI\' not found in the payload from GET %s" % (
            '/redfish/v1/Assembly'))
        return assertion_status


## end Assertion_ASSE114