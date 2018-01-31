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
# Name: Assertion_ACCO100(self, log) :Account Service                                            
# Assertion text: 
# This resource shall be used to represent a management account service for a Redfish 
# implementation.         
###################################################################################################


def Assertion_ACCO100(self, log): 
    
    log.AssertionID = 'ACCO100'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)    
    
    
    if  status == 200:
        
        http = urllib3.PoolManager()
        r = http.request('GET', 'http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService')
        
        global accSerData
        
        accSerData = json.loads(r.data.decode('utf8'))

        assertion_status = log.PASS
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', "Assertion passed.")  
        return assertion_status
    
    else:
        
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO100

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
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if accSerData.get('ServiceEnabled') == True or accSerData.get('ServiceEnabled') == False :
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non boolean property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status
    
## end Assertion_ACCO101

###################################################################################################
# Name: Assertion_ACCO102(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the threshold for when an authorization failure is logged.  This 
#represents a modulo function value, thus the failure shall be logged every nth occurrence where 
#n represents the value of this property.
###################################################################################################


def Assertion_ACCO102(self, log):
    
    log.AssertionID = 'ACCO102'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('AuthFailureLoggingThreshold'), int):
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO102

###################################################################################################
# Name: Assertion_ACCO103(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the minimum password length that the implementation will allow a 
# password to be set to.
###################################################################################################

def Assertion_ACCO103(self, log):
    
    log.AssertionID = 'ACCO103'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('MinPasswordLength'), int):
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO103

###################################################################################################
# Name: Assertion_ACCO104(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the maximum password length that the implementation will allow a 
# password to be set to.
###################################################################################################

def Assertion_ACCO104(self, log):
    
    log.AssertionID = 'ACCO104'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('MaxPasswordLength'), int):
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO104


###################################################################################################
# Name: Assertion_ACCO105(self, log) :Account Service                                            
# Assertion text: 
# This property shall reference the threshold of failed login attempts at which point the user's 
# account is locked.  If set to 0, no lockout shall ever occur.
###################################################################################################

def Assertion_ACCO105(self, log):
    
    log.AssertionID = 'ACCO105'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('AccountLockoutThreshold'), int):
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

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

def Assertion_ACCO106(self, log):
    
    log.AssertionID = 'ACCO106'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('AccountLockoutDuration'), int) or accSerData.get('AccountLockoutDuration') == None:
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the a non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

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

def Assertion_ACCO107(self, log):
    
    log.AssertionID = 'ACCO107'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if isinstance(accSerData.get('AccountLockoutCounterResetAfter'), int):
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property or non number property value type.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO107

###################################################################################################
# Name: Assertion_ACCO108(self, log) :Account Service                                            
# Assertion text: 
# This property shall contain the link to a collection of type ManagerAccountCollection.
###################################################################################################

def Assertion_ACCO108(self, log):
    
    log.AssertionID = 'ACCO108'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        path = accSerData.get('Accounts')
 
        if path != None:
        
            http = urllib3.PoolManager()
            
            r = http.request('GET', 'http://' + self.SUT_prop.get('DnsName') + accSerData.get('Accounts').get('@odata.id'))
                    
            acc = json.loads(r.data.decode('utf8'))
            
            if acc.get('@odata.type') == "#ManagerAccountCollection.ManagerAccountCollection":
                
                assertion_status = log.PASS
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', "Assertion passed.")  
                return assertion_status
            
            else:
                
                assertion_status = log.FAIL
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', 'Assertion failed due to the absence of link to a collection of type ManagerAccountCollection.') 
                return assertion_status
        
        else: 
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property Accounts.') 
            return assertion_status
            
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status 
        
## end Assertion_ACCO108


###################################################################################################
# Name: Assertion_ACCO109(self, log) :Account Service                                            
# Assertion text: 
# This property shall contain the link to a collection of type RoleCollection.
###################################################################################################

def Assertion_ACCO109(self, log):
    
    log.AssertionID = 'ACCO109'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        path = accSerData.get('Roles')
 
        if path != None:
        
            http = urllib3.PoolManager()
            
            r = http.request('GET', 'http://' + self.SUT_prop.get('DnsName') + accSerData.get('Roles').get('@odata.id'))
                    
            acc = json.loads(r.data.decode('utf8'))
            
            if acc.get('@odata.type') == "#RoleCollection.RoleCollection":
                
                assertion_status = log.PASS
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', "Assertion passed.")  
                return assertion_status
            
            else:
                
                assertion_status = log.FAIL
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', 'Assertion failed due to the absence of link to a collection of type RoleCollection.') 
                return assertion_status
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property Roles.') 
            return assertion_status 
            
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status 

## end Assertion_ACCO109

###################################################################################################
# Name: Assertion_ACCO110(self, log) :Account Service                                            
# Assertion text: 
# The value of this property shall be a link to a resource of type PrivilegeMappoing that defines 
# the privileges a user context needs in order to perform a requested operation on a URI associated 
# with this service.
###################################################################################################

def Assertion_ACCO110(self, log):
    
    log.AssertionID = 'ACCO110'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        path = accSerData.get('PrivilegeMap')
 
        if path != None:
            
            http = urllib3.PoolManager()
            
            r = http.request('GET', 'http://' + self.SUT_prop.get('DnsName') + path.get('@odata.id'))
                    
            acc = json.loads(r.data.decode('utf8'))
            
            if acc.get('@odata.type') == "#PrivilegeMappoing.PrivilegeMappoing":
                
                assertion_status = log.PASS
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', "Assertion passed.")  
                return assertion_status
            
            else:
                
                assertion_status = log.FAIL
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', 'Assertion failed due to the absence of link to a resource of type PrivilegeMappoing.') 
                return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property PrivilegeMappoing.') 
            return assertion_status 
            
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status 
   
## end Assertion_ACCO110

#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO111(self, log) :Account Service                                            
# Assertion text: 
# The Actions property shall contain the available actions for this resource.
###################################################################################################

def Assertion_ACCO111(self, log):
    
    log.AssertionID = 'ACCO111'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if accSerData.get('Actions') != None:
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO111

#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO112(self, log) :Account Service                                            
# Assertion text: 
# The Actions property shall contain the available actions for this resource.
###################################################################################################
    
def Assertion_ACCO112(self, log):
    
    log.AssertionID = 'ACCO112'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if accSerData.get('Actions') != None:
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status
    
## end Assertion_ACCO112
 
#Needs further development. 

###################################################################################################
# Name: Assertion_ACCO113(self, log) :Account Service                                            
# Assertion text: 
# This type shall contain any additional OEM actions for this resource.
###################################################################################################


def Assertion_ACCO113(self, log):
    
    log.AssertionID = 'ACCO113'
    
    assertion_status =  log.PASS 
    
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'on' 

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET('http://' + self.SUT_prop.get('DnsName') + '/redfish/v1/AccountService', rq_headers, authorization)
    
    if status == 200:
        
        if accSerData.get('OemActions') != None:
            assertion_status = log.PASS
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion passed.")  
            return assertion_status
        
        else:
            assertion_status = log.FAIL
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', 'Assertion failed due to the absence of the property.') 
            return assertion_status
    
    else:
        assertion_status = log.FAIL
        log.assertion_log(assertion_status, None)
        log.assertion_log('line', 'Assertion failed due to the absence of the resource.') 
        return assertion_status

## end Assertion_ACCO113


#Testing

def run(self, log):

    assertion_status = Assertion_ACCO100(self, log)
    
    assertion_status = Assertion_ACCO101(self, log)
    
    assertion_status = Assertion_ACCO102(self, log)
    
    assertion_status = Assertion_ACCO103(self, log)
    
    assertion_status = Assertion_ACCO104(self, log)
    
    assertion_status = Assertion_ACCO105(self, log)
    
    assertion_status = Assertion_ACCO106(self, log)
    
    assertion_status = Assertion_ACCO107(self, log)
    
    assertion_status = Assertion_ACCO108(self, log)

    assertion_status = Assertion_ACCO109(self, log)
    
    assertion_status = Assertion_ACCO110(self, log)
    
    assertion_status = Assertion_ACCO111(self, log)
    
    assertion_status = Assertion_ACCO112(self, log)

    assertion_status = Assertion_ACCO113(self, log)



    
    

    
    



    
