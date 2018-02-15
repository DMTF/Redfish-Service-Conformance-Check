# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

#####################################################################################################
# File: rfs_check.py
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
# Name: Assertion_ACCO101(self, log) :Account Service                                            
# Assertion text: 
#The value of this property shall be a boolean indicating whether this service is enabled.  If 
#this is set to false, the AccountService is disabled.  This means no users can be created, 
#deleted or modified.  Any service attempting to access the Account Service, like the Session 
#Service, will fail accessing.  Thus new sessions cannot be started with the service disabled 
#(though established sessions may still continue operating).  Note: this does not affect Basic 
#AUTH connections.
###################################################################################################

def Assertion_ACCO101(self, log):

    log.AssertionID = 'ACCO101'
    assertion_status =  log.PASS 
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on' 
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)

    try:
        isEnabled = json_payload['ServiceEnabled']
    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % ('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService'))
        return assertion_status
    else:
        try:
            key = 'Accounts'
            acc_collection = (json_payload[key])['@odata.id']
        except:
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'Accounts\' not found in the payload from GET %s" % ('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService'))
            return assertion_status
        else:
            if isEnabled:
                rq_body = {'Name': 'Test'}
                
                json_payload, headers, status = self.http_PUT('http://' + self.SUT_prop.get('DnsName') + acc_collection + '/test', rq_headers, rq_body, authorization)
                
                if status == 201:
                    assertion_status = log.FAIL
                    log.assertion_log(assertion_status, None)
                    log.assertion_log('line', "Assertion Failed")  
                    return assertion_status

                try:
                    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + acc_collection, rq_headers, authorization)
                    key = 'Members'
                    members_collection = (json_payload[key])
                except:
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ \'Members\' not found in the payload from GET %s" % ('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService'))
                    return assertion_status
                else:
                    for member in members_collection:
                        key = '@odata.id'
                        member_link = member[key]
                        json_payload, headers, status = self.http_PUT('http://' + self.SUT_prop.get('DnsName') + member_link, rq_headers, rq_body, authorization)
                        if status == 201:
                            assertion_status = log.FAIL
                            log.assertion_log(assertion_status, None)
                            log.assertion_log('line', "Assertion Failed")  
                            return assertion_status
            
    log.assertion_log(assertion_status, None)
    log.assertion_log('line', "Assertion Passes") 

    return assertion_status
    
## end Assertion_ACCO101

###################################################################################################
# Name: Assertion_ACCO102(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the threshold for when an authorization failure is logged.  This 
#represents a modulo function value, thus the failure shall be logged every nth occurrence where 
#n represents the value of this property.
###################################################################################################




## end Assertion_ACCO102

###################################################################################################
# Name: Assertion_ACCO103(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the minimum password length that the implementation will allow a 
# password to be set to.
###################################################################################################

    
    
## end Assertion_ACCO103

###################################################################################################
# Name: Assertion_ACCO104(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the maximum password length that the implementation will allow a 
# password to be set to.
###################################################################################################


## end Assertion_ACCO104


###################################################################################################
# Name: Assertion_ACCO105(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the threshold of failed login attempts at which point the user's 
# account is locked.  If set to 0, no lockout shall ever occur.
###################################################################################################


## end Assertion_ACCO105

###################################################################################################
# Name: Assertion_ACCO106(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the period of time in seconds that an account is locked after the 
# number of failed login attempts reaches the threshold referenced by AccountLockoutThreshold, 
# within the window of time referenced by AccountLockoutCounterResetAfter.  The value shall be 
# greater than or equal to the value of AccountLockoutResetAfter.  If set to 0, no lockout shall 
# occur.
###################################################################################################


## end Assertion_ACCO106

###################################################################################################
# Name: Assertion_ACCO107(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the threshold of time in seconds from the last failed login attempt 
# at which point the AccountLockoutThreshold counter (that counts number of failed login attempts) 
# is reset back to zero (at which point AccountLockoutThreshold failures would be required before 
# the account is locked).  This value shall be less than or equal to AccountLockoutDuration. The 
# threshold counter also resets to zero after each successful login.
###################################################################################################


## end Assertion_ACCO107

###################################################################################################
# Name: Assertion_ACCO108(self, log) :Account Service                                            
# Assertion text: 
# This property shall contain the link to a collection of type ManagerAccountCollection.
###################################################################################################
    
    
## end Assertion_ACCO108


###################################################################################################
# Name: Assertion_ACCO109(self, log) :Account Service                                            
# Assertion text: 
# This property shall contain the link to a collection of type RoleCollection.
###################################################################################################

## end Assertion_ACCO109

###################################################################################################
# Name: Assertion_ACCO110(self, log) :Account Service                                            
# Assertion text: 
# The value of this property shall be a link to a resource of type PrivilegeMappoing that defines 
# the privileges a user context needs in order to perform a requested operation on a URI associated 
# with this service.
###################################################################################################

   
## end Assertion_ACCO110

#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO111(self, log) :Account Service                                            
# Assertion text: 
# The Actions property shall contain the available actions for this resource.
###################################################################################################


## end Assertion_ACCO111

#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO112(self, log) :Account Service                                            
# Assertion text: 
# The Actions property shall contain the available actions for this resource.
###################################################################################################

    
## end Assertion_ACCO112
 
#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO113(self, log) :Account Service                                            
# Assertion text: 
# This type shall contain any additional OEM actions for this resource.
###################################################################################################


## end Assertion_ACCO113


#Testing

def run(self, log):

    assertion_status = Assertion_ACCO101(self, log)
    

    
    

    
    



    
