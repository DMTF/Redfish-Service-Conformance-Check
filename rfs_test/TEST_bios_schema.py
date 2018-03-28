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
# Name: Assertion_BIOS101(self, log) :Bios                                           
# Assertion text: 
# This action shall perform a reset of the BIOS attributes to their default values.
###################################################################################################

log.AssertionID = 'BIOS101'
assertion_status = log.PASS
log.assertion_log('BEGIN_ASSERTION', None)

relative_uris = self.relative_uris
authorization = 'on'
rq_headers = self.request_headers()

# Request for an Action 
rq_body = {'ResetType': 'On'}

json_payload, headers, status = self.http_POST('/redfish/v1/Systems/1/Actions/Bios.ResetBios', 
rq_headers, rq_body, authorization)


## end Assertion_BIOS105

###################################################################################################
# Name: Assertion_BIOS105(self, log) :Bios                                           
# Assertion text: 
# This action shall perform a change of the selected BIOS password.
###################################################################################################

log.AssertionID = 'BIOS105'
assertion_status = log.PASS
log.assertion_log('BEGIN_ASSERTION', None)

relative_uris = self.relative_uris
authorization = 'on'
rq_headers = self.request_headers()

# Request for an Action 
rq_body = {'OldPassword': 'admin', 'NewPassword': 'test', 'PasswordName': 'AdminPassword'}

json_payload, headers, status = self.http_POST('/redfish/v1/Systems/1/Actions/Bios.ChangePassword', 
rq_headers, rq_body, authorization)


## end Assertion_BIOS105