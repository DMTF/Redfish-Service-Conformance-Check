# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_accountservice_schema.py
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
import string
import random
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import time
from time import gmtime, strftime

accSerData = None
testAccountId = None

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.2.2"

# Helper Functions

def createDummyAccount(self):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {
        'UserName': 'test_id',
        'Password': 'test_pswd',
        'RoleId': 'Administrator'
    }
    json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

    acc_collection = json_payload_get['Accounts']['@odata.id']

    json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService/' + acc_collection + '/test']['url'], rq_headers, authorization)
    testAccountId = json_payload['Id']

    return status

def deleteDummyAccount(self):
    authorization = 'on'
    rq_headers = self.request_headers()
    json_payload, headers, status = self.http_DELETE(self.sut_toplevel_uris['Accounts']['url'] + testAccountId, rq_headers, authorization)



def failAuthorization(self):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {
        'UserName': 'test_id',
        'Password': 'wrong_pswd'
    }

    json_payload, headers, status = self.http_POST(self.sut_toplevel_uris['SessionService/Sessions']['url'], rq_headers, rq_body, authorization)

    # The status code for authentication credentials included with this request being missing or invalid.
    return status == 401
    
# Question: Does this method redquire authorization in order to perform the Reset action on LogService ?
def clearLog(self): 
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {
      
    }

    json_payload, headers, status = self.http_POST(self.sut_toplevel_uris['Managers/MultiBladeBMC/LogServices/Log/Actions/LogService.Reset']['url'], rq_headers, rq_body, authorization)
    
    return status == 200 or status == 201 or status == 202 or status == 204


###################################################################################################
# Name: Assertion_ACCO101(self, log) :Account Service
# Assertion text:
# The value of this property shall be a boolean indicating whether this service is enabled.  If
# this is set to false, the AccountService is disabled.  This means no users can be created,
# deleted or modified.  Any service attempting to access the Account Service, like the Session
# Service, will fail accessing.  Thus new sessions cannot be started with the service disabled
# (though established sessions may still continue operating).  Note: this does not affect Basic
# AUTH connections.
###################################################################################################

def Assertion_ACCO101(self, log):

    log.AssertionID = 'ACCO101'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload_get, headers, status = self.http_GET(
        self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

    try:
        isEnabled = json_payload_get['ServiceEnabled']

        if isEnabled:
            patch_key = 'ServiceEnabled'
            patch_value = False
            rq_body = {patch_key: patch_value}
            json_payload, headers, status = self.http_PATCH(self.sut_toplevel_uris['AccountService']['url'],
                            rq_headers, rq_body, authorization)
            if status == 405: 
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'ServiceEnabled\' property is Read Only")
                return assertion_status
            
            try:
                acc_collection = json_payload_get['Accounts']['@odata.id']

                status = createDummyAccount(self)

                if not (status >= 400 and status <= 500) :
                    assertion_status = log.FAIL
                    log.assertion_log(assertion_status, None)
                    log.assertion_log('line', "Assertion Failed")
                    return assertion_status

                patch_value = False
                rq_body = {patch_key: patch_value}
                json_payload, headers, status = self.http_PATCH(self.sut_toplevel_uris['AccountService']['url'],rq_headers, rq_body, authorization)
                
            except:
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Accounts\' not found in the payload from GET %s" % ('/redfish/v1/AccountService'))
                return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'ServiceEnabled\' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status

# end Assertion_ACCO101

###################################################################################################
# Name: Assertion_ACCO102(self, log) :Account Service
# Assertion text:
# This property shall reference the threshold for when an authorization failure is logged.  This
# represents a modulo function value, thus the failure shall be logged every nth occurrence where
# n represents the value of this property.
###################################################################################################


def Assertion_ACCO102(self, log):

    log.AssertionID = 'ACCO102'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()

    if not clearLog(self):
        assertion_status = log.WARN
        log.assertion_log('line', "Could not clear the Service Log")
        return assertion_status

    try:
        authorization = 'on'
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)
        authFailureThreshold = json_payload['AuthFailureLoggingThreshold']
        attempt = 0
        authFailureisLogged = False; 

        while(not authFailureisLogged):
            
            if not failAuthorization(self): 
                assertion_status = log.WARN
                log.assertion_log('line', "Could not fail the authorization")
                return assertion_status

            try: 
                authorization = 'on'
                json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['Managers/MultiBladeBMC/LogServices/Log/Entries/']['url'], rq_headers, authorization)
                log_collection = (json_payload['Members'])
                
                if attempt == authFailureThreshold:
                    assertion_status = log.PASS
                    log.assertion_log('line', "Assertion Passed")
                    return assertion_status

            except:     
                print("'Members\' not found in the payload from GET %s" % ('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/'));
         
            attempt += 1

            if attempt > authFailureThreshold:
                log.assertion_log('line', "Assertion Failed")
                return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status

# end Assertion_ACCO102


###################################################################################################
# Name: Assertion_ACCO103(self, log) :Account Service
# Assertion text:
# This property shall reference the minimum password length that the implementation will allow a
# password to be set to.
###################################################################################################


def Assertion_ACCO103(self, log):

    log.AssertionID = 'ACCO103'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

        MinPasswordLength = json_payload['MinPasswordLength']
        
        authorization = 'on'
        rq_headers = self.request_headers()
        rq_body = {
            'UserName': 'test_min',
            'Password': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(MinPasswordLength + 1)),
            'RoleId': 'Administrator'
        }
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

        # 201 is the only status when a request has created a new resource successfully

        if status == 201:
            assertion_status = log.FAIL
            log.assertion_log('line', "Assertion Failed")
            return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\MinPasswordLength' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status

    log.assertion_log(assertion_status, None)
    log.assertion_log('line', "Assertion Passes")
    return assertion_status


# end Assertion_ACCO103

###################################################################################################
# Name: Assertion_ACCO104(self, log) :Account Service
# Assertion text:
# This property shall reference the maximum password length that the implementation will allow a
# password to be set to.
###################################################################################################

def Assertion_ACCO104(self, log):

    log.AssertionID = 'ACCO104'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

        MaxPasswordLength = json_payload['MaxPasswordLength']
        
        authorization = 'on'
        rq_headers = self.request_headers()
        rq_body = {
            'UserName': 'test_max',
            'Password': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(MaxPasswordLength + 1)),
            'RoleId': 'Administrator'
        }
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

        # 201 is the only status when a request has created a new resource successfully

        if status == 201:
            assertion_status = log.FAIL
            log.assertion_log('line', "Assertion Failed")
            return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\MaxPasswordLength' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status

    log.assertion_log(assertion_status, None)
    log.assertion_log('line', "Assertion Passes")
    return assertion_status


# end Assertion_ACCO104


###################################################################################################
# Name: Assertion_ACCO105(self, log) :Account Service
# Assertion text:
# This property shall reference the threshold of failed login attempts at which point the user's
# account is locked.  If set to 0, no lockout shall ever occur.
###################################################################################################

def Assertion_ACCO105(self, log):

    log.AssertionID = 'ACCO105'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    if not clearLog(self):
        assertion_status = log.WARN
        log.assertion_log('line', "Could not clear the Service Log")
        return assertion_status

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()
    
    json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

    try:
        AccountLockoutThreshold = json_payload['AccountLockoutThreshold']

        for i in range(0, AccountLockoutThreshold):
            if not failAuthorization(self): 
                assertion_status = log.WARN
                log.assertion_log('line', "Could not fail the authorization")
                return assertion_status 
            try: 
                authorization = 'on'
                json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['Managers/MultiBladeBMC/LogServices/Log/Entries/']['url'], rq_headers, authorization)
                log_collection = (json_payload['Members'])
            except: 
                print("'Members\' not found in the payload from GET %s" % ('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/'));

        try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['Managers/MultiBladeBMC/LogServices/Log/Entries/']['url'], rq_headers, authorization)
            log_collection = (json_payload['Members'])
            log.assertion_log(assertion_status, None)
            log.assertion_log('line', "Assertion Passes")
            return assertion_status
        except: 
            assertion_status = log.FAIL
            log.assertion_log('line', "Assertion Failed")
            return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status

# end Assertion_ACCO105

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
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    if not clearLog(self):
        assertion_status = log.WARN
        log.assertion_log('line', "Could not clear the Service Log")
        return assertion_status

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

    try:
        AccountLockoutThreshold = json_payload['AccountLockoutThreshold']
        AccountLockoutCounterResetAfter = json_payload['AccountLockoutCounterResetAfter']

        for i in range(0, AccountLockoutThreshold):
            if not failAuthorization(self): 
                assertion_status = log.WARN
                log.assertion_log('line', "Could not fail the authorization")
                return assertion_status 

        try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET(self.sut_toplevel_uris['Managers/MultiBladeBMC/LogServices/Log/Entries/']['url'], rq_headers, authorization)
            log_collection = (json_payload['Members'])

            start = time.time()

            while True: 

                end = time.time()
                
                if int(end - start) % 60 == AccountLockoutCounterResetAfter: 

                    authorization = 'on'
                    rq_headers = self.request_headers()
                    rq_body = {
                        'UserName': 'test_id',
                        'Password': 'test_pswd'
                    }
                    json_payload, headers, status = self.http_POST(self.sut_toplevel_uris['SessionService/Sessions']['url'], rq_headers, rq_body, authorization)
                    
                    if status == 200 or status == 201 or status == 202 or status == 204: 
                        assertion_status = log.PASS
                        log.assertion_log(assertion_status, None)
                        log.assertion_log('line', "Assertion Passes")
                        return assertion_status

                    else: 
                        assertion_status = log.FAIL
                        log.assertion_log('line', "Assertion Failed")
                        return assertion_status
          
        except: 
            assertion_status = log.FAIL
            log.assertion_log('line', "Failure attempt was not logged in after failed login attempts reached the threshold referenced by AccountLockoutThreshold")
            return assertion_status
    
    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % ('/redfish/v1/AccountService'))
        return assertion_status

# end Assertion_ACCO106

# Testing

def run(self, log):
    createDummyAccount(self)
    assertion_status = Assertion_ACCO101(self, log)
    assertion_status = Assertion_ACCO102(self, log)
    assertion_status = Assertion_ACCO103(self, log)
    assertion_status = Assertion_ACCO104(self, log)
    assertion_status = Assertion_ACCO105(self, log)
    assertion_status = Assertion_ACCO106(self, log)
    deleteDummyAccount(self)