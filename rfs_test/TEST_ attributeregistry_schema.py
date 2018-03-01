# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

#####################################################################################################
# File: TEST_attributeregistry_schema.py
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
# Name: Assertion_ATTR124(self, log) :Attribute Registry                                           
# Assertion text: 
#The value of this property shall be a boolean describing the read-only state of attribute. A 
#read-only attribute cannot be modified, and should be grayed out in user interfaces. The 
#read-only state of an attribute might be affected by the results of evaluating the 'Dependencies' 
#array.
###################################################################################################

'''
Step 1: Try performing an HTTP PATCH on a read-only attribute. 
Step 2: If a 204 No Content response is recived, fail the assertion or else pass the assertion. 
'''

## end Assertion_ATTR124

###################################################################################################
# Name: Assertion_ATTR125(self, log) :Attribute Registry                                           
# Assertion text: 
#The value of this property shall be a boolean describing the write-only state of this attribute. 
#A write-only attribute reverts back to it's initial value after settings are applied.
###################################################################################################

'''
Step 1: Try performing an HTTP PATCH on a WriteOnly attribute. 
Step 2: If a 204 No Content response is not recived, fail the assertion or else pass the assertion
else proceed to next step. 
Step 3: If the write only attribute does not revert back to it's inital value, fail the assertion 
or else pass the assertion. 
'''

## end Assertion_ATTR125

###################################################################################################
# Name: Assertion_ATTR126(self, log) :Attribute Registry                                           
# Assertion text: 
#The value of this property shall be a boolean describing the gray-out state of this attribute. 
#When set to true, a grayed-out attribute should be grayed out in user interfaces. But, unlike
#ReadOnly, the value of grayed-out attributes might still be be modified. The grayout state of an 
#attribute might be affected by the results of evaluating the 'Dependencies' array.
###################################################################################################

'''
Step 1: If GrayOut property is set to true for an attribute proceed to Step 2 else WARN. 
Step 2: If the attribute is grayed out in the User Interface, pass the assertion, else fail the
assertion. 
'''

## end Assertion_ATTR126

###################################################################################################
# Name: Assertion_ATTR127(self, log) :Attribute Registry                                           
# Assertion text: 
#The value of this property shall be a boolean describing the visibility state of this attribute. 
#When set to true, a hidden attribute should be hidden in user interfaces. The hidden state of an 
#attribute might be affected by the results of evaluating the 'Dependencies' array.
###################################################################################################

'''
Step 1: If the HiddenyOut property is set to true for an attribute proceed to Step 2 else WARN. 
Step 2: If the attribute is hidden in the User Interface, pass the assertion, else fail the
assertion. 
'''

## end Assertion_ATTR127