###################################################################################################
# File: rf_client.py
# Description: This module is responsible for setting up client tool with settings provided in 
#   properties.json as well as gathering preliminary Redfish Service information of SUT such as 
#   Service versions, schema directory, schemas (also serialize schemas), top level uris, 
#   relative uris etc.
#
# Licensed under the Apache license: http://www.apache.org/licenses/LICENSE-2.0
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel 
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
#   Copyright (c) 2015 Intel Corporation
#
# Note: Current implementation for schemas found in local directory (or remotely retrieved) does not 
#       guarantee that SUT service is using the same version of the schema files. It is a WIP for this tool. 
#       Please make sure that schema file version found in $metadata for SUT is the same as the 
#       version of files in the directory to get correct results...     
###################################################################################################
import ssl
import json
import argparse
import base64
import warnings
import shutil
from datetime import datetime
import gzip
import os
import re
import zipfile
import collections
import sys
import xml.etree.ElementTree as ET
from schema import SchemaModel
import rf_utility
import rfs_test
from rf_sut import SUT

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, responses
    import urllib2
    from urllib import URLopener, urlopen
    from HTMLParser import HTMLParser
else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from io import StringIO, BytesIO
    from http.client import HTTPSConnection, HTTPConnection, responses
    import urllib.request
    from urllib.request import URLopener, urlopen
    from html.parser import HTMLParser

# tracking tool release revision with a date stamp -  month:day:year   
RedfishServiceCheck_Revision = "01.05.17"
## The file containing server authorization parameters required for test access.
## Users must edit and set the parameters within this file prior to running this test...		
Server_Auth_Json_File = 'properties.json'
json_directory = 'json-schema'
xml_directory = 'metadata'
 
###############################################################################################
# Name: init_service_obj(SUT_prop)                        
#   Takes SUT's properies and intializes a Service class instance with SUT's properties         
###############################################################################################
def init_sut_obj(sut_prop):
    sut = SUT(sut_prop)
    return sut

###############################################################################################
# Name: verify_sut_prop(sut_prop)                                          
#   Takes sut property object, reads it into a dictionary and returns the dictionary
#   redundant, to be removed
# Return:
#   sut properties obj          
###############################################################################################
def verify_sut_prop(sut_prop):
    if 'DnsName' not in sut_prop or 'LoginName' not in sut_prop or 'Password' not in sut_prop or 'DisplayName' not in sut_prop:
        print('SUT properties are not set correctly in properties.json. One or more required property is missing. \
        Please see the readme.txt file for required SUT properties to resolve issue and try running the tool again.')
        exit(0)

    return sut_prop
    #required_properties = ['DnsName', 'LoginName', 'Password', 'DisplayName']
    #Check if keys/values exist
    #for req_property in required_properties:
       # if req_property not in sut_prop or not sut_prop[req_property]:
       #     print('SUT properties are not set correctly in properties.json. One or more required property is missing. \
        #    Please see the readme.txt file for required SUT properties to resolve issue and try running the tool again.')
        #    exit(0)

                                
###############################################################################################
# Name: get_sut_prop(server_index = None)                                             
#   Takes server index i.e index of SUTs from properties.json. Based on the index, reads the 
#   config properties for the sut at that index. If no index is provided, it reads the SUT's one
#   by one
# Return: 
#   Yields the sut property object         
###############################################################################################
def get_sut_prop(server_index = None) :      
	# keys into the json file for the SUT information
    json_SUT_key = "RedfishServiceCheckTool_SUTConfiguration"
    json_SUT_subkey = "SUTs"			

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File )
        
    try:
        with open(file_name) as data_file: 
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(0)			
            else:
                if server_index is not None:
                    try:
                        rf_sut = data[json_SUT_key][json_SUT_subkey][server_index]
                        #return server
                        yield verify_sut_prop(rf_sut)                       
                    except KeyError:
                        print ('Operational ERROR: Decoding JSON configuration file %s - invalid key/keys. Please correct the key values and try again.' % (file_name))	
                        data_file.close()				
                        exit(0)
                    except StopIteration:
                        pass
                    except IndexError:
                        print('SUT at index requested not found. Correct the index number and try again.')
                        exit(0)

                else:
                    try:
                        for rf_sut in data[json_SUT_key][json_SUT_subkey]:
                            #yield server
                            yield verify_sut_prop(rf_sut)
                    except KeyError:
                        print ('Operational ERROR: Decoding JSON configuration file %s - invalid key/keys. Please correct the key values and try again.' % (file_name))
                        data_file.close()
                        exit(0)

            data_file.close()
                                                    
    except ValueError: 
        print ('Operational ERROR: Opening/parsing the JSON configuration file %s' % (file_name))
        data_file.close()
        exit(0)
  
###############################################################################################
# Name: get_sut_schema_settings()                                               
#   Read properties.json for Redfish schemas directory "LocalSchemaDirectoryFolder"
#   and "RetrieveDMTFSchemas". If RetrieveDMTFSchemas is 'Yes', then read properties.json
#   further for SchemaRepository and ClientProxy and load it in schema_url and proxy_Dict resp.
# Return:
#   retrieve_dmtf_schemas: yes/no, schema directory path, schema repo url and proxy setting
#   else exits tool if any issue found in reading properties.json with error message
###############################################################################################
def get_sut_schema_settings() :
    schema_directory = ''
    schema_repo_url = ''
    proxy_Dict = ''

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File )
        
    try:
        with open(file_name) as data_file: 
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(0)			
            else:
	            # top level keys into the json file for the schema file location info
                Metadata_key = "RedfishServiceCheckTool_SchemaFiles"                	
                LocalDir_key = "LocalSchemaDirectoryFolder"
                GetSchemaYesNo_key = "RetrieveDMTFSchemas"
                DMTFSchemas_key = "DMTF_SPMFSchemas"
 
                try:
                    schema_directory = data[Metadata_key][LocalDir_key]
                except: 
                    print ('Operational ERROR: Decoding JSON failed (%s : %s)' % (Metadata_key, LocalDir_key))
                    data_file.close()
                    exit(0)	                    

                try:
                    retrieve_dmtf_schemas = data[Metadata_key][GetSchemaYesNo_key]
                except:
                    print ('Operational ERROR: Decoding JSON failed (%s : %s)' % (Metadata_key, GetSchemaYesNo_key))
                    data_file.close()
                    exit(0)
                else:
                    retrieve_dmtf_schemas = retrieve_dmtf_schemas.lower()

                    if (retrieve_dmtf_schemas != 'yes'):            
                        data_file.close()
                    else:
                        try:
                            DMTFSchemas_subkey = "SchemaRepository"
                            schema_repo_url = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey]
                        except:
                            print ('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                            data_file.close()
                            exit(0)                
                        else:
                            '''
                            try:
                                DMTFSchemas_subkey = "SchemaZipFileName"
                                schema_zipfile = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey]
                            except:
                                print ('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                                return False
                                '''        

                            DMTFSchemas_subkey = "ClientProxy"
                            https_subkey = 'https_proxy'
                            http_subkey = 'http_proxy'
                            try:
                                proxy_Dict = {\
                                    'https': data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey][https_subkey],\
                                    'http' : data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey][http_subkey]
                                    }
                            except:
                                print ('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                                data_file.close()
                                exit(0)
                                                
            data_file.close()

    except ValueError: 
        print ('Operational ERROR: Opening/parsing the JSON configuration file %s' % file_name)
        exit(0)

    return retrieve_dmtf_schemas, schema_directory, schema_repo_url, proxy_Dict
        
###############################################################################################
# Name: get_eventservice_params                                             
#   Read the config json file for the event service parameters
# Return:
#  exit(0) on syntax error reading json file        
###############################################################################################
def get_eventservice_params() :
	# keys into the json file
    Event_key =  "RedfishServiceCheckTool_Event"
    Subscription_subkey = "Subscription"
    Submit_test_event_subkey = "SubmitTestEvent"			

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File )
        
    try:
        with open(file_name) as data_file: 
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(0)			
            else:
                try:
                    event_subscription = data[Event_key][Subscription_subkey]
                except:
                    print ("ERROR: Decoding JSON configuration file %s - unable to find %s %s keys" % (file_name, Event_key, Subscription_subkey))


                try:
                    EVENT_subscription = {\
                        # grab info from the JSON file...
                        'Destination' : event_subscription['Destination'],\
                        'EventTypes' : event_subscription['EventTypes'],\
                        'Context' : event_subscription['Context'],\
                        'Protocol' : event_subscription['Protocol']
                    }
                    Event_Subscription = EVENT_subscription         

                except:
                    print('- ERROR decoding %s - one or more %s:%s subkeys is invalid' % (file_name, Event_key, Subscription_subkey))             						
                    print('- expecting keys: Destination, EventTypes, Context, Protocol, HttpHeaders')
                    data_file.close()
                    exit(0)


                try:
                    submit_event_subscription = data[Event_key][Submit_test_event_subkey]
                except:
                    print ("ERROR: Decoding JSON configuration file %s - unable to find %s %s keys" % (file_name, Event_key, Subscription_subkey))


                try:
                    TEST_event = {\
                        # grab info from the JSON file...
                        'Action' : submit_event_subscription['Action'],\
                        'EventType' : submit_event_subscription['EventType'],\
                        'EventId' : submit_event_subscription['EventId'],\
                        'EventTimestamp' : submit_event_subscription['EventTimestamp'],\
                        'Severity' : submit_event_subscription['Severity'],\
                        'Message' : submit_event_subscription['Message'],\
                        'MessageId' : submit_event_subscription['MessageId'],\
                        'MessageArgs' : submit_event_subscription['MessageArgs'],\
                        'OriginOfCondition' : submit_event_subscription['OriginOfCondition']
                    }
                    Submit_Test_Event = TEST_event         

                except:
                    print('- ERROR decoding %s - one or more %s:%s subkeys is invalid' % (file_name, Event_key, Submit_test_event_subkey))             						
                    print('- expecting keys: Action, EventType, EventId, EventTimestamp, Severity, Message, MessageId, MessageArgs, OriginOfCondition')
                    data_file.close()
                    exit(0)

            data_file.close()

    except ValueError: 
        print ('Operational ERROR: Opening/parsing the JSON configuration file %s' % file_name)
        exit(0)

    return Event_Subscription, Submit_Test_Event

###############################################################################################
# Name: retrieve_schemas_in_local_directory(schemas_uri, dest_directory, proxy_dict)
#   Takes schemas remote uri, proxy settings, and local destination directory path and retrieves 
#   schema files(.xml and .json) from schemas_uri using proxy settings to bypass firewall and 
#   places them in dest_directory
# Return:
#   True if all is good; else False
###############################################################################################      
def retrieve_schemas_in_local_directory(schemas_uri, dest_directory, proxy_dict = None):
    json_dirname = 'json-schema'
    xml_dirname = 'metadata'

    json_dir = os.path.join(dest_directory, json_dirname)
    xml_dir = os.path.join(dest_directory, xml_dirname)

    class MyHTMLParser(HTMLParser):
        def handle_data(self,data):
            schema_file_source_path = None
            local_file_path = None  
            schema_file_source_path = schemas_uri + data
            if data.endswith('.xml'):
                local_file_path = os.path.join(xml_dir, data)
            elif data.endswith('.json'):
                local_file_path = os.path.join(json_dir, data)

            try:
                if local_file_path:
                    if Python3 == True:
                        urllib.request.urlretrieve(schema_file_source_path, local_file_path)
                    else:
                        urlprox.retrieve(schema_file_source_path, local_file_path)

            except:
                print("Error trying to retreive schema file %s" % schema_file_source_path)
                return(False)
                
    if not (schemas_uri.endswith('/')):
        schemas_uri += '/'

    #remove existing folder and files, TODO only delete sub-folders/files
    if (os.path.exists(dest_directory)):            
        shutil.rmtree(dest_directory)
        
    if not os.path.isdir(dest_directory):
        os.makedirs(dest_directory)
        os.chmod(dest_directory,0o777)
        os.makedirs(json_dir)
        os.makedirs(xml_dir)
    else:
        print("Folder %s exists and an attempt to delete it failed. Please make sure that folder %s is deleted and run the tool agian." % dest_directory, dest_directory)
        exit(0)

    if Python3 == True:
        if proxy_dict:
            proxy_handler = urllib.request.ProxyHandler(proxy_dict)
            urlopener = urllib.request.build_opener(proxy_handler)
            urlprox = urllib.request.install_opener(urlopener)

            try:
                urlfile = urlopener.open(schemas_uri)
            except:
                print("Error trying to open %s with proxy=%s" % (schemas_uri, proxy_dict))
                return(False)
        #not tested
        else:
            try:
                urlfile = urllib.request.urlopen(schemas_uri)
            except:
                print("Error trying to open %s" % (schemas_uri))
                return(False)

    else:
        if proxy_dict:
            urlprox = URLopener(proxies=proxy_dict)
            try:
                urlfile = urlopen(schemas_uri, proxies=proxy_dict)
            except:
                print("Error trying to open %s with proxy=%s" % (schemas_uri, proxy_dict))
                return(False)
        else:
            try:
                urlfile = urlopen(schemas_uri)
            except:
                print("Error trying to open %s" % (schemas_uri))
                return(False)

    parser = MyHTMLParser()
        
    try:
        htmlstring = urlfile.read()
        
        if Python3 == True:
            htmlstring = htmlstring.decode('unicode_escape')
            
    except:
        print("Error trying to read from %s" % schemas_uri)
        return(False)

    try:
        parser.feed(htmlstring)
    except Exception as inst:
        print (type(inst))     # the exception instance
        print (inst.args)

    return(True)

###############################################################################################
# Name: retrieve_schemas_in_local_directory_zip(zip_schemas_uri, proxy_dict, schema_zipfilename, 
#   dest_directory)
#   Takes zipped schemas remote uri, zipped schemas file name, proxy settings, and local 
#   destination directory path and retrieves the zip file from zip_schemas_uri using
#   proxy settings to bypass firewall, unzips it and places it in dest_directory
# Return:
#   Full pathname of the unzipped metatdata files; else None on Failure
# 
###############################################################################################
def retrieve_schemas_in_local_directory_zip(zip_schemas_uri, proxy_dict, schema_zipfilename, dest_directory):
    # crack open a connection via the proxy...
    try:
        schema_zip_file = URLopener(proxies=proxy_dict)
    except:
        print("urllib.URLopener error: %s" % (proxy_dict))
        return None

    # if the local schema directory does not exist - error
    if not (os.path.exists(dest_directory)):
        try:
            os.makedirs(dest_directory)
 
        except ValueError as err:
            print("Unable to create the schema files directory %s" % dest_directory)
            print(err)
            return None

    # full pathname of the target
    zip_file_path = dest_directory + schema_zipfilename              

    # retrieve the zip file from the url
    try:
        zip_url_path = zip_schemas_uri + schema_zipfilename
        schema_zip_file.retrieve(zip_url_path, zip_file_path)
    except:
        print("Error retrieving %s to %s with proxy=%s" % (zip_url_path, zip_file_path, proxy_dict))
        print("...this could be due to %s not being available at %s or an invalid proxy setting." % (schema_zipfilename, zip_schemas_uri))
        return None

    # unzip it
    with zipfile.ZipFile(zip_file_path, "r") as zfile:
        try:
            zfile.extractall(dest_directory)                                               
        except:
            print("Error unzipping %s" % zip_file_path)
            return None 

    # locate the "ServiceRoot" (either json or xml) in the zip file... this will yeild
    # the subpath below "dest_directory" where the schema files were loaded into (and unloaded from)
    # the source zipfile.  This subpath is needed for the tool to have a full pathname to the schema files 
    # 
    unzip_metadata_subpath = None
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zfile:
            for fname in zfile.namelist():
                # find the path within the zip file for the metadata files
                if "metadata" in fname and "ServiceRoot" in fname and fname.__str__().endswith(".xml") and ("MAC" not in fname):
                    str_idx = fname.find("ServiceRoot")
                    unzip_metadata_subpath = fname[0:str_idx]
                    break
    except:
        print("Error processing the zip file %s while searching for a \'ServiceRoot\' metadata file" % zip_file_path)
        return None

    if (unzip_metadata_subpath == None):
        print("Error: %s does not appear to be a valid DMTF/SPMF metadata zip file..." % zip_file_path) 
        print("  Unable to locate the \'ServiceRoot'\ xml file below the \'metadata'\ in the zipfile %s" % zip_file_path)
        return False

    # return the full path to the unzipped metadata files
    return dest_directory + unzip_metadata_subpath  

###############################################################################################
# Name: verify_local_files(schema_directory)                                      
#   Takes local schema directory path and verifies if the required subfolders are present and 
#   not empty
# Return:
#   True if all is good, else the tool exits
# Condition:
#   If schema folder/files are not found in the directory, tool exits with an error message
###############################################################################################
def verify_local_schemas(schema_directory):
    # check for valid metadata dir ... check to see that the directory specified for metadata files 
    # contains ServiceRoot
    # 
    if not (os.path.exists(schema_directory)):
        print("Error: %s specified as the path for metadata files does not exist" % schema_directory)
        exit(0)
    else:
        # check if directory contains sub-directories and files within them as expected 
        metadata_files_found = False
        if not os.listdir(schema_directory):
            print('Directory %s found empty' % (schema_directory))
            print(" ...either set configuration values to allow retrieval of the DMTF Schemas")
            print(" or to a local pathname where the metadata files can be found (see properties.json)")
        else:
            for dirpath, dirnames, files in os.walk(schema_directory):
                if dirpath == schema_directory:
                    if xml_directory in dirnames and json_directory in dirnames:
                        continue
                    else:
                            break
                if not files:
                    print("Error: %s does not appear to contain schema files" % dirpath)
                    print(" ...either set configuration values to allow retrieval of the DMTF Schemas")
                    print(" or to a local pathname where the schema files can be found (see properties.json)")
                    exit(0)

###############################################################################################
# Name: get_remote_schemas(schemas_uri, proxy_Dict, schema_directory)                                      
#   Takes remote schemas uri, proxy settings and local schema directory found in properties.json
#   verifies which proxy setting to use based on the schemas uri (http or https), and triggers
#   the retreival of the schemas
# Return:
#   If schema retrieval is successful, returns True, else tool exits
# Condition:
#   If remote schema retrieval fails, tool exits with error message 
###############################################################################################
def get_remote_schemas(schemas_uri, proxy_Dict, schema_directory):
    # retrieve DMTF/SPMF metadata files from the paths/url specified in properties.json
    # select the proxy...
    proxy_key = None
    if (schemas_uri.startswith("https")):
        proxy_key = 'https'
    elif (schemas_uri.startswith("http")):
        proxy_key = 'http'

    if (proxy_key == None) or (proxy_Dict[proxy_key] == 'none'):
        use_proxy = None
    else:
        use_proxy = {proxy_key : proxy_Dict[proxy_key]}

    # retrieve DMTF schema files
    print("Note: downloading schema files from %s to %s..." % (schemas_uri, schema_directory))

    if (retrieve_schemas_in_local_directory(schemas_uri, schema_directory,  use_proxy) != True) :
        print("...Error retrieving schema files: you can try to resolve the retrieval issue or disable Retrieval of DMTF schemas ...")
        print("and then reset %s to a local pathname where the metadata files can be found" % schema_directory)
        exit(0)
    else:
        print("...schema files downloaded successfully.")
        return True
            
    '''
    DMTF_SPMF_schema_pathname = retrieve_schemas_in_local_directory_zip(schemas_uri, use_proxy, schema_zipfile, schema_directory)

    if (DMTF_SPMF_schema_pathname == None):
        print("Error retrieving/unzipping schema files: you can try to resolve the retrieval issue or disable Retrieval of DMTF schemas ...")
        print("and then reset %s to a local pathname where the metadata files can be found" % schema_directory)
        exit(0)
    else:
        # point the tool to the download
        schema_directory = DMTF_SPMF_schema_pathname
        print("Note: schema files successfully downloaded from %s to %s" % (schemas_uri, schema_directory))
        return True

    '''

###############################################################################################
# Name: setup_schemas(sut)                                      
#  Takes sut's service object and sets up schemas for this SUT in the tool in the following 
#  manner:
#  1. gets the schema settings from properties.json such as retrieval method, uris, directory path
#  2. depeding on the settings triggers appropriate schemas retrieval function and
#  3. passes each schema file to a function which serializes it via schema model class. 
# Return:
# True if all is good, else tool exits
# Condition:
#   If anything goes wrong and schemas are not set up correctly, the tool exits with error msg
###############################################################################################
def setup_schemas(sut):
    # create class instance which stores all the serialized schemas
    csdl_schema_model = SchemaModel() 
    '''comment out for now
    #set log file for schema
    log = logger.Log()
    loghandle , logfilepath = log.init_logfile('schema-run')
    log.schema_log('OPEN', loghandle, logfilepath)
    '''
    #1.Get schema file settings from properties.json
    retrieve_dmtf_schemas, schema_directory, schema_repo_url, proxy_Dict  = get_sut_schema_settings() 
    ## Remove the following 2 lines of script if a custom schema directory is provided in the properties.json 
    ## current script file directory, folders should be in this directory
    script_dir = os.path.dirname(__file__)
    # this is the folder where we read/write schema files
    schema_directory = os.path.join(script_dir, schema_directory)

    #2. Configuration settings successfully parsed; check if local/online metadata is to be 
    # used or retrieved remotely
    if (retrieve_dmtf_schemas == 'no'):
        verify_local_schemas(schema_directory)
    else:
        get_remote_schemas(schema_repo_url, proxy_Dict, schema_directory)

    #3. Schema files successfully retrieved, walk down the directory to serialize each schema
    # file. xml_directry is where we expect CSDL (.xml) schema files
    xml_directory_path = os.path.join(schema_directory, xml_directory)
    # json_directory_path
    json_directory_path = os.path.join(schema_directory, json_directory)

    #verify files are available in dir
    if xml_directory_path:
        if not os.listdir(xml_directory_path):
            print('CSDL schemas not found in %s. Please make sure files are in place or proper properties.json settings are set for schema files and try running the tool again.' %(xml_directory_path))
            exit(0)
        else:
            print('\nSerializing CSDL Schemas located at: %s' % (xml_directory_path))
            for dirpath, dirnames, files in os.walk(xml_directory_path):
                for schema_file in files:
                    csdl_schema_model.serialize_schema(os.path.join(dirpath,schema_file))

    #verify files are available in dir
    if json_directory_path:
        if not os.listdir(json_directory_path):
            print('JSON schemas not found in %s. Please make sure files are in place or proper properties.json settings are set for schema files and try running the tool again.' %(json_directory_path))
            exit(0)

    #4. save the instance of schema model and directory paths in sut
    sut.csdl_schema_model = csdl_schema_model
    sut.schema_directory = schema_directory
    sut.xml_directory = xml_directory_path
    sut.json_directory = json_directory_path

    return True

    #TODOS
    # Check if version used by this service is same as local files, else invoke client to 
    # update settings in properties.json to get remote files and run again.
    # could also check if all schema files required by $metadata document are present in the 
    # directory and report files not available.

###############################################################################################
# Name: setup_sut(sut)                                                
#   Takes sut's sut obj and gets sut's service's preliminary values such 
#   as protocol version, redfish defined uris, top level uris, schema documents, 
# Condition:
#   If there are any abnormilities, the tool exits reporting failure
###############################################################################################
def setup_sut_obj(sut):
    # 2. gets protocol and odata version for this service from GET /redfish
    protocol_version, service_root = sut.parse_protocol_version(sut.Redfish_URIs['Protocol_Version'])
    if not protocol_version and not service_root:
        print('Protocol version and/or Service Root uri could not be retreived through %s' %(sut.Redfish_URIs['Protocol_Version']))
        return False
    # 2.1 Set protocol version for this sut in the tool
    sut.set_protocol_version(protocol_version)
    # 2.2 set appropraite values for sut's redfish-defined uris based on its service root 
    sut.set_redfish_defined_uris(service_root)

    # 3. gets service top level resources links by parsing service odata document
    odata_context, odata_values = sut.parse_odatadoc_payload(sut.Redfish_URIs['Service_Odata_Doc'])
    #3.1 Set odatacontext for this tool
    sut.set_odata_context(odata_context)
    #3.2 Set odatavalues for this tool
    sut.set_odata_values(odata_values)

    # 4. gets service top level resources links by parsing service root uri
    sr_toplevel_uris = sut.parse_serviceroot_toplevel_uris(sut.Redfish_URIs['Service_Root'] )
    # 4.1 set service root top level links for this tool
    #   Precendence is given to odata values when setting top-level uris in the service object, if
    #   not avaialble, then we set service roots top level uris in the service object. If both are 
    #   unavaialble, tool exits. 
    #   TODO: we can remove service root top level uris here because specification only mentions odata
    #   document for providing top level links
    if not odata_values and sr_toplevel_uris:
        print('Service top level links could not be retreived.')
        return False

    if odata_values:
        sut.set_sut_toplevel_uris(odata_values)
    else:
        sut.set_sut_toplevel_uris(sr_toplevel_uris)

    # 6. explore service root to get all relative uris of this service
    print('\nCollecting all relative uris from Service Root: %s' % (sut.Redfish_URIs['Service_Root']))
    sut.collect_relative_uris(sut.Redfish_URIs['Service_Root'])
   
    print('\nSerializing SUT metadata document: %s ...' %(sut.Redfish_URIs['Service_Metadata_Doc']))
    # 7. parsing $metadata in a structure for several good information, 
    # WIP verifying odata versions, retreiving schema version, and identifying service errors, if any
    metadata_document_structure = sut.parse_metadata_document(sut.Redfish_URIs['Service_Metadata_Doc'])   
    if metadata_document_structure:
        sut.set_metadata_document_structure(metadata_document_structure)
    else:
        print('Unable to parse Service Metadata Document %s' %(sut.Redfish_URIs['Service_Metadata_Doc']))                 

    # 6. set up schema documents for this sut's redfish service
    setup_schemas(sut)   
    
    #7. optional if running assertion 8.x 
    Conformant_evt_rq_body, Submit_Test_Event = get_eventservice_params()
    # set in sut obj
    sut.set_event_params(Conformant_evt_rq_body, Submit_Test_Event) 
    
    return True

###############################################################################################
# Name: setup_tool(SUT_prop)                                               
#   Takes SUT's authentication dictionary retreieved from properties.json and starts prepping 
#   client tool for SUT, initializes SUT object and gathers information from SUT to be used
#   by the Redfish conformance tool. 
# Return:
#   sut object   
# Condition:
#   If there are any abnormilities, the tool setup exits reporting failure
###############################################################################################
def setup_tool(sut_prop):
    ## create a unique log header 
    print('Setting up Redfish Service Check Tool Revision: %s : %s:%s' % (RedfishServiceCheck_Revision, sut_prop['DisplayName'],sut_prop['DnsName'])) 
    # tool initiates service object
    sut = init_sut_obj(sut_prop)
    # setup sut obj for sut
    if setup_sut_obj(sut):
        print('\nRedfish Service Check Tool setup for SUT %s successfully completed' % (sut_prop['DnsName'] ))
        return sut
    else:
        print('\nSetup of client tool was not successful, Redfish Service Check Tool will exit...')
        exit(0)

###############################################################################################
# Name: main
# Start up function. Invokes appropriate setup functions to run Redfish Service Check Tool
###############################################################################################
def main():
     #  step through the json server configuration file, checking the assertions against each server/SUT...
    SUTs = get_sut_prop()
    for sut_prop in SUTs:
        if sut_prop:
            #initalize tool before anything else..this sets up all the necc variables for this sut in this tool
            sut = setup_tool(sut_prop)  
            print('Running assertions on SUT %s...' %(sut_prop['DnsName']))   
            rfs_test.run(sut)
        else:
            print('No SUT found in properties.json. Please add an SUT following the format provided in readme.txt and try running the Redfish Service Check Tool again')
            exit(0)
        
if __name__ == "__main__":
   main()
                











