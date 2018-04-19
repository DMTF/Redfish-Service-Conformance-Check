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

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.2.2"


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

    json_payload, headers, status = self.http_GET(
        '/redfish/v1/AccountService', rq_headers, authorization)

    try:
        isEnabled = json_payload['ServiceEnabled']

        if isEnabled:
            patch_key = 'ServiceEnabled'
            patch_value = False
            rq_body = {patch_key: patch_value}
            self.http_PATCH('/redfish/v1/AccountService',
                            rq_headers, rq_body, authorization)

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'ServiceEnabled\' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status
    else:
        try:
            acc_collection = (json_payload['Accounts'])['@odata.id']
        except:
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'Accounts\' not found in the payload from GET %s" % (
                '/redfish/v1/AccountService'))
            return assertion_status
        else:

            rq_body = {'Name': 'Test'}

            json_payload, headers, status = self.http_POST(
                acc_collection + '/test', rq_headers, rq_body, authorization)

            if status == 201:
                assertion_status = log.FAIL
                log.assertion_log(assertion_status, None)
                log.assertion_log('line', "Assertion Failed")
                return assertion_status

            try:
                json_payload, headers, status = self.http_GET(
                    acc_collection, rq_headers, authorization)
                members_collection = (json_payload['Members'])
            except:
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Members\' not found in the payload from GET %s" % (
                    '/redfish/v1/AccountService'))
                return assertion_status
            else:
                for member in members_collection:
                    key = '@odata.id'
                    member_link = member[key]
                    json_payload, headers, status = self.http_PUT(
                        member_link, rq_headers, rq_body, authorization)
                    if status == 201:
                        assertion_status = log.FAIL
                        log.assertion_log(assertion_status, None)
                        log.assertion_log('line', "Assertion Failed")
                        return assertion_status

    log.assertion_log(assertion_status, log.PASS)
    log.assertion_log('line', "Assertion Passes")

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

    try:
        authorization = 'on'
        json_payload, headers, status = self.http_GET('/redfish/v1/AccountService', rq_headers, authorization)
        authFailureThreshold = json_payload['AuthFailureLoggingThreshold']
        attempt = 0
        authFailureisLogged = False; 

        while(not authFailureisLogged):
            try: 
                authorization = 'off'
                json_payload, headers, status = self.http_GET('/redfish/v1/AccountService', rq_headers, authorization)
            except:
                  print("~ \'AccountsService\' not found in the payload from GET %s" % ('/redfish/v1/AccountService'))

            try: 
                authorization = 'on'
                json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
                log_collection = (json_payload['Members'])

            except:     
                print("'Members\' not found in the payload from GET %s" % ('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/'));
                return assertion_status
         
            attempt += 1

            if attempt > authFailureThreshold:
                log.assertion_log('line', "Assertion Failed")
                return assertion_status
      
        assertion_status = log.PASS
        log.assertion_log('line', "Assertion Passed")
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
        json_payload, headers, status = self.http_GET(
            '/redfish/v1/AccountService', rq_headers, authorization)

        MinPasswordLength = json_payload['MinPasswordLength']

        if MinPasswordLength != 0:
            rq_body = {'Name': 'Test',
                        'Password': ''}

            json_payload, headers, status = self.http_POST(
            acc_collection + '/test', rq_headers, rq_body, authorization)
    
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
        json_payload, headers, status = self.http_GET(
            '/redfish/v1/AccountService', rq_headers, authorization)

        MaxPasswordLength = json_payload['MinPasswordLength']

        rq_body = {'Name': 'Test',
                    'Password': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(MaxPasswordLength + 1))}

        json_payload, headers, status = self.http_POST(
        acc_collection + '/test', rq_headers, rq_body, authorization)

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

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(
        '/redfish/v1/AccountService', rq_headers, authorization)

    try:
        AccountLockoutThreshold = json_payload['AccountLockoutThreshold']

        for i in range(0, AccountLockoutThreshold):
            authorization = 'off'
            json_payload, headers, status = self.http_GET('/redfish/v1/AccountService', rq_headers, authorization) 
            try: 
                authorization = 'on'
                json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
                log_collection = (json_payload['Members'])
            except: 
                print("'Members\' not found in the payload from GET %s" % ('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/'));

        try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
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

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(
        '/redfish/v1/AccountService', rq_headers, authorization)

    try:
        AccountLockoutThreshold = json_payload['AccountLockoutThreshold']
        AccountLockoutCounterResetAfter = json_payload['AccountLockoutCounterResetAfter']
        authorization = 'off'

        for i in range(0, AccountLockoutThreshold):
            json_payload, headers, status = self.http_GET(
            '/redfish/v1/AccountService', rq_headers, authorization) 

        try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
            log_collection = (json_payload['Members'])

            start = time.time()

            while not isUnlocked: # Needs to know the procedure for finding if an account is unlocked.

                end = time.time()
                
                if end - start == AccountLockoutCounterResetAfter: 
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

###################################################################################################
# Name: Assertion_ACCO107(self, log) :Account Service
# Assertion text:
# This property shall reference the threshold of time in seconds from the last failed login attempt
# at which point the AccountLockoutThreshold counter (that counts number of failed login attempts)
# is reset back to zero (at which point AccountLockoutThreshold failures would be required before
# the account is locked).  This value shall be less than or equal to AccountLockoutDuration. The
# threshold counter also resets to zero after each successful login.
###################################################################################################

'''
Step 1: Simulate failed login attempts preiodically with a time interval more that of
AccountLockoutCounterResetAfter value. 
Step 2: Check if AccountLockoutThreshold counter is reset to 0. 
Step 3: Pass the assertion if Step 2 returns true. 
'''

def Assertion_ACCO107(self, log):

    log.AssertionID = 'ACCO107'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(
        '/redfish/v1/AccountService', rq_headers, authorization)

    try:
        AccountLockoutCounterResetAfter = json_payload['AccountLockoutCounterResetAfter']
        AccountLockoutCounter = json_payload['AccountLockoutCounter'] # Assumption: There exist an AccountLockoutCounter property. 
        AccountLockoutThreshold = json_payload['AccountLockoutThreshold']


        for i in range(0, AccountLockoutThreshold):
            json_payload, headers, status = self.http_GET(
            '/redfish/v1/AccountService', rq_headers, authorization) # Needs to know the procedure for providing credentials to acess a Redfish server. 

        try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
            log_collection = (json_payload['Members'])

            while not time.time() == AccountLockoutCounterResetAfter: 
            
                if AccountLockoutCounter == 0: # Assumption: There exist an AccountLockoutCounter property. : 
                    log.assertion_log(assertion_status, None)
                    log.assertion_log('line', "Assertion Passes")
                    return assertion_status

                else: 
                    assertion_status = log.FAIL
                    log.assertion_log('line', "Assertion Failed")
                    return assertion_status
        except:
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % (
                '/redfish/v1/AccountService'))
            return assertion_status

    except:
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'AccountsService\' not found in the payload from GET %s" % (
            '/redfish/v1/AccountService'))
        return assertion_status


# end Assertion_ACCO107



# Testing

def run(self, log):
    
    '''
    assertion_status = Assertion_ACCO101(self, log)
    assertion_status = Assertion_ACCO102(self, log)
    assertion_status = Assertion_ACCO103(self, log)
    assertion_status = Assertion_ACCO104(self, log)
    assertion_status = Assertion_ACCO105(self, log)
    assertion_status = Assertion_ACCO106(self, log)
    assertion_status = Assertion_ACCO107(self, log)
    '''
