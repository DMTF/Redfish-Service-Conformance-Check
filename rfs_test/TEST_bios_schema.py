# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_bios_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Windows OS) :
#       3.5.2
#
# Initial code released : 03/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

###################################################################################################
# Name: Assertion_ATTR124(self, log) :Bios                                           
# Assertion text: 
#The value of this property shall be a boolean describing the read-only state of attribute. A 
#read-only attribute cannot be modified, and should be grayed out in user interfaces. The 
#read-only state of an attribute might be affected by the results of evaluating the 'Dependencies' 
#array.
###################################################################################################