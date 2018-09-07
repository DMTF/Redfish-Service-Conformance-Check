# Copyright Notice:
# Copyright 2016-2017 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

###################################################################################################
# File: rf_utility.py
#   This module contains basic HTTP connection and request functions (Based on Redfish requirement),
#   Redfish service relevant HTTP status codes, request header and response payload helper functions to running assertions
#   on SUT
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      - Intel
#   Fatima Saleem   - Intel
#   Priyanka Kumari ~ Texas Tech University
###################################################################################################
import sys
from schema import SchemaModel
from collections import OrderedDict

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from urlparse import urljoin
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, responses
    import urllib2
    from urllib import URLopener

else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from urllib.parse import urljoin
    from io import StringIO, BytesIO
    from http.client import HTTPSConnection, HTTPConnection, responses
    import urllib.request
    from urllib.request import URLopener

import ssl
import json
import argparse
import base64
import warnings
import shutil
from datetime import datetime
import gzip
from xml.etree import ElementTree as ET
import os
import zipfile
import re
import requests
from bs4 import BeautifulSoup



###################################################################################################
# Name: service class                                             
# Description: 
#               
###################################################################################################
	    
accept_type = {\
    'json' : 'application/json',\
    'xml' : 'application/xml',\
    'bad' : 'snooop/dog' ,\
    'json_utf8' : 'application/json;charset=utf-8' ,\
    'xml_utf8' : 'application/xml;charset=utf-8'
}
content_type = {\
    'utf8' : 'application/json; charset=utf-8' ,\
    'json' : 'application/json',\
    'xml' : 'application/xml; charset=utf-8' \
}

# some status codes referenced during test
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_NOTIMPLEMENTED = 501
HTTP_METHODNOTALLOWED = 405
HTTP_BADREQUEST = 400
HTTP_NOTMODIFIED = 304
HTTP_MOVEDPERMANENTLY = 301
HTTP_MOVEDTEMPORARILY = 307
HTTP_MEDIATYPENOTSUPPORTED = 415
HTTP_NOTACCEPTABLE = 406
   
default_odata_version = '4.0'

###############################################################################################
# Name: Connect_Server_NoSSL                                               
# Description:   
#   get an http(s) connection to a server (disabled SSL).
#   if successful return the connection else return 0.
#	        
###############################################################################################
def Connect_Server_NoSSL(sut_prop, host_ip_addr) :
    if (sys.version_info.major == 2 and sys.version_info.minor == 7 and sys.version_info.micro >= 9) :
        # python 2.7.9 enables SSL by default but it was not enabled prior 2.7.9...  - disable it for the test connection...
        cont=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        cont.verify_mode = ssl.CERT_NONE
        try:
            svr_conn = HTTPSConnection(host=sut_prop['DnsName'], strict=True, context=cont)
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

    elif (Python3 == False) : # Python 2 but prior to 2.7.9
        try:
            conn = HTTPSConnection(host=host_ip_addr, strict=True)
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

    elif (Python3 == True) :
        #if 3.4.2
        if (sys.version_info.major == 3 and sys.version_info.minor == 4 and sys.version_info.micro <= 3) :
            cont=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            cont.verify_mode = ssl.CERT_NONE
            try:
                svr_conn = HTTPSConnection(host=host_ip_addr, context=cont)
            except:
                exc_str = sys.exc_info()[0]
                svr_conn = 0 # failure
        else:
            try:
                cntxt = ssl._create_unverified_context()
            except:
                exc_str = sys.exc_info()[0]
                svr_conn = 0 # failure

            try:
                svr_conn = HTTPSConnection(sut_prop['DnsName'], context=cntxt)
            except:
                exc_str = sys.exc_info()[0]
                svr_conn = 0 # failure

    if (svr_conn == 0) :
        print("OPERATIONAL ERROR (%s) - Unable to  connect to the Server %s -- exiting test..." % (exc_str, sut_prop['DnsName']))
        print("Check the parameters configured for %s in the properties.json file" % sut_prop['DisplayName'])
        ## game over.
        exit(0)

    return(svr_conn)
#
## end Connect Server No SSL

###############################################################################################
# Name: Connect_Server_NoSSL_NoHTTPS                                               
# Description:   
#   get an http(s) connection to a server (disabled SSL).
#   if successful return the connection else return 0.
#	        
###############################################################################################
def Connect_Server_NoSSL_NoHTTPS(sut_prop, host_ip_addr) :

    if (sys.version_info.major == 2 and sys.version_info.minor == 7 and sys.version_info.micro >= 9) :
        # python 2.7.9 enables SSL by default but it was not enabled prior 2.7.9...  - disable it for the test connection...
        cont=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        cont.verify_mode = ssl.CERT_NONE
        try:
            svr_conn = HTTPConnection(host=sut_prop['DnsName'])
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

    elif (Python3 == False) : # Python 2 but prior to 2.7.9
        try:
            conn = HTTPConnection(host=host_ip_addr)
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

    elif (Python3 == True) :
        try:
            cntxt = ssl._create_unverified_context()
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

        try:
            svr_conn = HTTPConnection(sut_prop['DnsName'])
        except:
            exc_str = sys.exc_info()[0]
            svr_conn = 0 # failure

    if (svr_conn == 0) :
        print("OPERATIONAL ERROR (%s) - Unable to  connect to the Server %s -- exiting test..." % (exc_str, sut_prop['DnsName']))
        print("Check the parameters configured for %s in the properties.json file" % sut_prop['DisplayName'])
        ## game over.
        exit(0)

    return(svr_conn)
#
## end Connect Server No SSL

###############################################################################################
# Name: http__set_auth_header()                                              
# Description:  
#  common code for the http requests -- this function:
#  sets up the authorization header and centralizes code to ease
#  support accross python 2.x and 3.x
#  
# Arguments:
#   rq_headers - dict() for the reqeust headers
#   login : login name
#   password : password
#
# Returns:                                                 
###############################################################################################
def http__set_auth_header(rq_headers, login, password) :
    if (Python3 == True):
        bstr = login + ":" + password
        bencode =   base64.b64encode(bstr.encode(), altchars=None)              
        rq_headers['Authorization'] = ("Basic " + bencode.decode())
    else: # python 2.x
        rq_headers['Authorization'] = ("Basic " + base64.b64encode(login + ":" + password))
 
#
## end http__set_auth_header

###############################################################################################
# Name: get_auth_encoded                                            
# Description:  
#  get authorization string encoded -- this function:
#  returns the encoded authorization for request header
#  supports accross python 2.x and 3.x
#  
# Arguments:
#   login : login name
#   password : password
#
# Returns: encoded authorization header value                                                              
###############################################################################################
def get_auth_encoded(login, password) :
    if (Python3 == True):
        bstr = login + ":" + password
        bencode =   base64.b64encode(bstr.encode(), altchars=None)              
        authorization = ("Basic " + bencode.decode())
    else: # python 2.x
        authorization = ("Basic " + base64.b64encode(login + ":" + password))

    return authorization
 
## end get_auth_encoded


###############################################################################################
# Name: http__req_resp()                                              
# Description:  
#  common code for the http requests -- this function:
#   1. sets up the authorization header
#   2. posts the requests
#   3. recieves the response
#  
# Arguments:
#   http_req:  the request type (GET, DELETE... etc)
#   resource_uri: the uri of the redfish resource
#   rq_headers: the reqeuest headers
#   rq_body: the body of the request in json format
#   auth_on_off: if set to 'on' then authorization is enabled for the request 
#       by adding the 'Authorization' header to the request; else the request
#       is made without this function adding authorization parameters into 
#       the request headers
#
# Returns:
#   response:  the response recieved                                                  
###############################################################################################
def http__req_resp(sut_prop, http_req, resource_uri, rq_headers, rq_body, auth_on_off) :

    if (rq_headers == None):
        rq_headers = create_request_headers()

    # default to https unless overridden via "UseHttp" in the SUT config
    proto = "https"
    if "UseHttp" in sut_prop:
        use_http = sut_prop.get("UseHttp").lower()
        if use_http in ["yes", "true", "on"]:
            proto = "http"

    url = None
    # if dsn name is not prepended to the uri, then prepend uri with https protocol and dnsname as per redfish service requirement
    if sut_prop['DnsName'] not in resource_uri:
        url = urlparse(proto + "://" + sut_prop['DnsName'] + resource_uri)
    else:
        url = urlparse(resource_uri)
    
    if not url:
        print('Could not parse the url %s' % resource_uri)
        exit(0)
    else:
        url_ip = url.netloc
        url_path = url.path

        if url.scheme == 'https':
        ### get fresh connection
            server_connection = Connect_Server_NoSSL(sut_prop, url_ip)
            # handle http, for conformance test purpose, sometimes we use http
        elif url.scheme == 'http':
            server_connection = Connect_Server_NoSSL_NoHTTPS(sut_prop, url_ip)
        else:
            server_connection = Connect_Server_NoSSL(sut_prop, url_ip)

        # setup auth header: set login name and password for the sut_prop...
        if (auth_on_off == 'on'):
            http__set_auth_header(rq_headers, sut_prop['LoginName'], sut_prop['Password'])

        # issue the http request
        try:
            server_connection.request(http_req, url_path, headers=rq_headers, body=rq_body)
        except:
            exc_str = sys.exc_info()[0]
            print ('OPERATIONAL ERROR: %s Request for %s FAILED with exeption: %s' % (http_req, url_path, exc_str)) 
            return     
        else:
            # receive the response and payload
            try:
                response = server_connection.getresponse()
            except:
                exc_str = sys.exc_info()[0]
                print ('OPERATIONAL ERROR: %s getresponse() for %s failed with exeption: %s - exiting test..' % (http_req, url_path, exc_str))
                return
            else:
                return(response)
#
## end http__req_resp


###############################################################################################
# Name: http__req_common()                                              
# Description:  
#  common code for the http requests -- this function processes response headers
#  for gzip as well as redirect prior to returning the payload
#   
# Arguments:
#   http_req:  the request type (GET, DELETE... etc)
#   resource_uri: the uri of the redfish resource
#   rq_headers: the reqeuest headers
#   rq_body: the body of the request in json format
#   auth_on_off: if set to 'on' then authorization is enabled for the request 
#       by adding the 'Authorization' header to the request; else the request
#       is made without this function adding authorization parameters into 
#       the request headers
#
# Returns:
#   r_payload: this is the response payload.  If the response headers specify
#       gzip encoding then the payload is un-gzip'd prior to return - otherwise
#       it is returned as recieved from the server
#   r_headers: response headers (keys converted to lower case)
#   response.status:  the http status code returned from the request                                                 
###############################################################################################
def http__req_common(sut_prop, http_req, resource_uri, rq_headers, rq_body, auth_on_off, cookie_info = None) :
    ## issue the base request/get the response
    r_response = http__req_resp(sut_prop, http_req, resource_uri, rq_headers, rq_body, auth_on_off)
    if r_response:
        try:
            r_payload = r_response.read()
        except:
            exc_str = sys.exc_info()[0]
            print("Error trying to read http response: %s" % exc_str)
        else:
            # get the headers associated with the resp
            # convert the keys to lowercase so that string searches can be made w/o concern for case..    
            r_headers = dict()
            for key, value in r_response.getheaders():
                key = key.lower()
                if key in r_headers:
                    r_headers[key] += ',' + value
                else:
                    r_headers[key] = value

            #handle any http redirect... recursive call here...  
            if ("location" in r_headers.keys()) and (r_headers['location'] != resource_uri and r_response.status>= 300 and r_response.status < 400):
                redirected_resource_uri = urlparse(r_headers['location'])
                return(http__req_common(sut_prop, http_req, redirected_resource_uri.path, rq_headers, rq_body, auth_on_off, cookie_info))

            if not r_response.status:
                print('SERVICE ERROR: No Response Status found for request %s:%s' % (http_req, resource_uri))

            if cookie_info:
                cookie_detail = tuple()
                #set cookie True if Set-Cookie is found, service is not expected to return Cookies in the header
                if 'set-cookie' in r_headers.keys():
                    cookie_info[0] = True
                    cookie_info[2] += 1
                    # set details of request type and url where cookie was found
                    cookie_detail = (http_req , resource_uri)
                    cookie_info[1].append(cookie_detail)
        

            # check to  see if the payload is gzip'd - if so un-gzip it
            if ('content-encoding' in r_headers.keys()):
                if (r_headers['content-encoding'] == 'gzip'):
                    #un-gzip the payload
                    try:
                        if (Python3 == True):
                            gz_payload = gzip.GzipFile(fileobj=BytesIO(r_payload))

                        else: # Python2
                            gz_payload = gzip.GzipFile(fileobj=StringIO(r_payload))
                
                        r_payload = gz_payload.read()

                    except:
                        exc_str = sys.exc_info()[0]
                        print("Error trying to un-gzip payload: %s" % exc_str)

            # if a payload is returned in json format then load it into a json dictionary here...
            is_json = False
            if 'content-type' in r_headers.keys() :
                if ('application/json' in r_headers['content-type']):
                    is_json = True
                    if (r_payload) : # if there is a resp payload ...
                        try:
                            r_payload = json.loads(r_payload.decode('utf-8'))
                        except:
                            exc_str = sys.exc_info()[0]
                            print ("Error trying load %s payload to JSON: %s" % (resource_uri, exc_str))
            ''' 
            #log dump                   
                # dump the response headers and payload to the text log file
                if (is_json == True):
                    if (r_payload):
                        print("response: %s %s" % (json_string(r_headers), json_string(r_payload)) )
                    else:
                        print("response: %s" % json_string(r_headers) )
 
                else:
                    if (r_payload):
                        print("response: %s %s" % (r_headers, r_payload))                                                                                      
                    else:
                        print("response: %s" % r_headers)   
            '''

            return (r_payload, r_headers, r_response.status)

    else:
        #print('WARN: No response retreived from %s' %(resource_uri))
        return None, None, None
#
## end http__req_common

###############################################################################################
# Name: http__modify_resource()                                              
# Description: issue a request to the server connection/URI which
#   modifies a resource (POST, PATCH, PUT)
#  
# Arguments:
#   rq_type:  POST, PATCH or PUT
#   resource_uri: the uri of the redfish resource
#   rq_headers: the request headers. If Content-Type is not specified
#       then this routine will set it to json before making the request.  
#   rq__body: the body of the request.  this can be json or a python dict - this routine 
#       converts it to json for the reqeust
#   auth_on_off: if set to 'on' then authorization is enabled for the request 
#       by adding the 'Authorization' header to the request; else the request
#       is made with no authorization parameters specified in the request headers 
#
# Returns:
#   r_payload: this is the json response payload
#   r_headers: response headers (keys converted to lower case)
#   r_status:  the http status code returned from the request
###############################################################################################
def http__modify_resource(sut_prop, rq_type, resource_uri, rq_headers, rq_body, auth_on_off) :

    if (rq_headers == None):
        rq_headers = create_request_headers()
         
    # this routine can take a python dictionary as a request body... or json
    # make sure the request is json format..
    rq_body = json.dumps(rq_body)        

    # issue the request
    return(http__req_common(sut_prop, rq_type, resource_uri, rq_headers, rq_body, auth_on_off ))

#
## end http__modify_resource

###############################################################################################
# Name: http__GET(sut_prop, resource_uri, rq_headers, auth_on_off, cookie_info = None)                                              
#   Issue a GET request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, authorization 'on' or 'off'
#   optional cookie info to track cookies in request response
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request                                        
###############################################################################################
def http__GET(sut_prop, resource_uri, rq_headers, auth_on_off, cookie_info = None ) :      
    if (rq_headers == None):
        rq_headers = create_request_headers()
    # issue the GET on the resource...
    return (http__req_common(sut_prop, "GET", resource_uri, rq_headers, None, auth_on_off, cookie_info))

#
## end http__GET

###############################################################################################
# Name: http__POST(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off)                                              
#   Issue a POST request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, request body authorization 
#   'on' or 'off'
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request     
###############################################################################################
def http__POST(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__modify_resource(sut_prop, "POST", resource_uri, rq_headers, rq_body, auth_on_off))

#
## end http__POST

###############################################################################################
# Name: http__TRACE(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off, cookie_info = None)                                              
#   Issue a TRACE request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, request body authorization 
#   'on' or 'off'. optional cookie info to track cookies in request response
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request  
###############################################################################################
def http__TRACE(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off, cookie_info = None) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__req_common(sut_prop, "TRACE", resource_uri, rq_headers, rq_body, auth_on_off, cookie_info ))

#
## end http__TRACE

###############################################################################################
# Name: http__OPTIONS(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off)                                              
#   Issue a OPTIONS request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, request body authorization 
#   'on' or 'off'. optional cookie info to track cookies in request response
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request  
###############################################################################################
def http__OPTIONS(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off, cookie_info = None) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__req_common(sut_prop, "OPTIONS", resource_uri, rq_headers, rq_body, auth_on_off, cookie_info ))

#
## end http__OPTIONS

###############################################################################################
# Name: http__PATCH(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off)                                              
#   Issue a PATCH request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, request body authorization 
#   'on' or 'off'
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request           
###############################################################################################
def http__PATCH(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__modify_resource(sut_prop, "PATCH", resource_uri, rq_headers, rq_body, auth_on_off))
#
## end http__PATCH

###############################################################################################
# Name: http__PUT(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off)                                              
#   Issue a PUT request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, request body authorization 
#   'on' or 'off'
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request          
###############################################################################################
def http__PUT(sut_prop, resource_uri, rq_headers, rq_body, auth_on_off) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__modify_resource(sut_prop, "PUT", resource_uri, rq_headers, rq_body, auth_on_off))

#
## end http__PUT

###############################################################################################
# Name: http__HEAD(sut_prop, resource_uri, rq_headers, auth_on_off, cookie_info = None)                                              
#   Issue a HEAD request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, authorization 'on' or 'off'
#   optional cookie info to track cookies in request response
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request                
###############################################################################################
def http__HEAD(sut_prop, resource_uri, rq_headers, auth_on_off, cookie_info = None) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__req_common(sut_prop, "HEAD", resource_uri, rq_headers, None, auth_on_off, cookie_info))
#
## end http__HEAD


###############################################################################################
# Name: http__DELETE(sut_prop, resource_uri, rq_headers, auth_on_off)                                              
#   Issue a DELETE request for resource uri thru base http__req_common() 
#   Takes service connection prop, resource uri, request header dict, authorization 'on' or 'off'
# Returns:
#   - Response payload dict or string depending on 'content-type' in request header. If
#       'application/json' then payload will be a dict. 
#   - Response Headers dict: header keys in lower case
#   - Response Status code: http status code returned from the request  
###############################################################################################
def http__DELETE(sut_prop, resource_uri, rq_headers, auth_on_off) :
    if (rq_headers == None):
        rq_headers = create_request_headers()
    return(http__modify_resource(sut_prop, "DELETE", resource_uri, rq_headers, None, auth_on_off))

#
## end http__DELETE

###############################################################################################
# Name: create_request_headers()                                                
#   Creates required request header used globally throughout rfs_check.py additional headers 
#   can be added as per assertioin requirements
# Return:
#   request header dictionary
# Note: set all headers that are expected to be recognized by the service as per spec
###############################################################################################
def create_request_headers():
    rq_headers = dict()      
    rq_headers['Accept'] = accept_type['json']
    rq_headers['Content-Type'] = 'application/json'
    rq_headers['OData-Version'] = default_odata_version
    return rq_headers
    
###############################################################################################
# Name: HTTP_status_string(HTTP_status_code)                                               
#   Takes an HTTP status code in integer form and maps it to a string form
# Return:
#   String version of HTTP code               
###############################################################################################
def HTTP_status_string(HTTP_status_code):
    return (str(responses[HTTP_status_code]))

###############################################################################################
# Name: json_string(json_text)                                                                                         
#  Takes json payload in dictionary format and returns in a readable format       
###############################################################################################
def json_string(json_text) :
    return(json.dumps(json_text, indent=2, separators=(',', ': ')))

###############################################################################################
# Name: json_get_key_value(json_text, key)                                              
#   Takes a json payload dictionary and key. Finds and return a value for the key in the payload                                                 
###############################################################################################
def json_get_key_value(json_text, key) :
    status = False
    val = None

    for skey, value in json_text.items():
        if (key.lower() == skey.lower()):
            status = True
            # found the key...
            if value:
                if isinstance(value, dict):		
                    for val in value.keys():                      
                        break
                elif isinstance(value, str) or isinstance(value, list) :
                    val = value
            break

    return(status, val)

###############################################################################################
# Name: parse_odata_type(odata_type)
#   Parses an @odata.type into namespace and typename strings
# Retrun:
#   namespace string, typename string    
###############################################################################################  
def parse_odata_type(odata_type):
    namespace = None
    typename = None
    if '#' in odata_type:
        odata_type = odata_type.split('#')[1]

    split_type = odata_type.rsplit('.', 1)
    if len(split_type) > 1:
        namespace = split_type[0]
        typename = split_type[1] 

    return namespace, typename

###############################################################################################
# Name: parse_unversioned_odata_type(odata_type)
#   Parses an @odata.type into namespace and typename strings. Removes version from namespace 
# Retrun:
#   unversion namespace string, typename string 
###############################################################################################  
def parse_unversioned_odata_type(odata_type):
    namespace = None
    typename = None
    if '#' in odata_type:
        odata_type = odata_type.split('#')[1]

    split_type = odata_type.rsplit('.', 1)
    if len(split_type) > 1:
        namespace = split_type[0]
        typename = split_type[1] 

        if '.' in namespace:
            namespace = namespace.split('.')[0]

    return typename

###############################################################################################
# Name: get_resource_json_metadata(namespace, json_directory)
#   Takes namespace string and directory path for json schemas. Walks the direcotry to find the
#   json schema for that namespace and loads json in a string
# Return:
#   If found, returns string loaded with json schema and schema file path
###############################################################################################  
def get_resource_json_metadata(namespace, json_directory):                            
    for dirpath, dirnames, files in os.walk(json_directory):
        for schema_file in files:
            if (namespace + '.json') == schema_file:
                json_file = os.path.join(dirpath, schema_file)
                if json_file:
                    with open(json_file) as data_file:    
                        data = json.load(data_file)
                        return data, schema_file
        return None, None
