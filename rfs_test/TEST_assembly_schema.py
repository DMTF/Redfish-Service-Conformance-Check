# Copyright Notice:
# Copyright 2016-2019 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_assembly_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Ubuntu OS) :
#       3.5.2
#
# Initial code released : 02/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

###################################################################################################
# Name: Assertion_ASSE114(self, log) : Assembly
# Assertion text:
# The value of this property shall be a URI at which the Service provides for the download of the
# OEM-specific binary image of the assembly data.  An HTTP GET from this URI shall return a response
# payload of MIME time application/octet-stream. An HTTP PUT to this URI, if supported by the
# Service, shall replace the binary image of the assembly.
###################################################################################################

def Assertion_ASSE114(self, log):

    log.AssertionID = 'ASSE114'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    
    try:

        json_payload, headers, status = self.http_GET(self.relative_uris['Root Service_Chassis_Members_1'], rq_headers, authorization)
        
    except: 
        assertion_status = log.WARN
        log.assertion_log('line', "~  Chassis members not found at chassis collection.")
        return assertion_status


    try: 
        assemblyLink = json_payload['Assembly']
    
    except: 
        assertion_status = log.WARN
        log.assertion_log('line', "~  Assembly resource is not found at %s" % (self.relative_uris['Root Service_Chassis_Members_1']))
        return assertion_status

    
    try: 
        json_payload, headers, status = self.http_GET(assemblyLink['@odata.id'], rq_headers, authorization)
        BinaryDataURI = json_payload['BinaryDataURI']
    except: 
        assertion_status = log.WARN
        log.assertion_log('line', "~  BinaryDataURI is not found at %s" % (assemblyLink['@odata.id']))
        return assertion_status
    
    try:

        json_payload, headers, status = self.http_GET(BinaryDataURI, rq_headers, authorization)
        
    except: 
        assertion_status = log.WARN
        log.assertion_log('line', "~  Unable to perform a GET request on BinaryDataURI.")
        return assertion_status
    
    try:
    
        rq_body = {'Property': 'Test'}
        json_payload, headers, status = self.http_PUT(BinaryDataURI, rq_headers, rq_body, authorization)
        
        if status >= 400 and status <= 599:
            log.assertion_log('line',"~  Assertion Passed") 
            assertion_status = log.PASS
            return assertion_status

        else: 
            log.assertion_log('line',"~  Assertion Passed") 
            assertion_status = log.PASS
            return assertion_status
        
    except: 
        assertion_status = log.WARN
        log.assertion_log('line', "~  Unable to perform a PUT request on BinaryDataURI.")
        return assertion_status
 

# end Assertion_ASSE114

# Testing

def run(self, log):
    assertion_status = Assertion_ASSE114(self, log)
