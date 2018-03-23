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

## end Assertion_ASSE114