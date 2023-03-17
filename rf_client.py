# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/main/LICENSE.md

###################################################################################################
# File: rf_client.py
# Description: This module is responsible for setting up client tool with settings provided in
#   properties.json as well as gathering preliminary Redfish Service information of SUT such as
#   Service versions, schema directory, schemas (also serialize schemas), top level uris,
#   relative uris etc.
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
#
# Note: Current implementation for schemas found in local directory (or remotely retrieved) does not
#       guarantee that SUT service is using the same version of the schema files. It is a WIP for this tool.
#       Please make sure that schema file version found in $metadata for SUT is the same as the
#       version of files in the directory to get correct results...
###################################################################################################
import io
import json
import os
import requests
import shutil
import sys
import tempfile
from urllib.parse import urljoin
import zipfile
from schema import SchemaModel
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
        exit(1)

    return sut_prop
    # required_properties = ['DnsName', 'LoginName', 'Password', 'DisplayName']
    # Check if keys/values exist
    # for req_property in required_properties:
    #     if req_property not in sut_prop or not sut_prop[req_property]:
    #         print('SUT properties are not set correctly in properties.json. One or more required property is missing. \
    #         Please see the readme.txt file for required SUT properties to resolve issue and try running the tool again.')
    #         exit(0)


###############################################################################################
# Name: get_sut_prop(server_index = None)                                             
#   Takes server index i.e index of SUTs from properties.json. Based on the index, reads the 
#   config properties for the sut at that index. If no index is provided, it reads the SUT's one
#   by one
# Return: 
#   Yields the sut property object         
###############################################################################################
def get_sut_prop(server_index=None):
    # keys into the json file for the SUT information
    json_SUT_key = "RedfishServiceCheckTool_SUTConfiguration"
    json_SUT_subkey = "SUTs"

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File)

    try:
        with open(file_name) as data_file:
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(1)
            else:
                if server_index is not None:
                    try:
                        rf_sut = data[json_SUT_key][json_SUT_subkey][server_index]
                        # return server
                        yield verify_sut_prop(rf_sut)
                    except KeyError:
                        print(
                            'Operational ERROR: Decoding JSON configuration file %s - invalid key/keys. Please correct the key values and try again.' % (
                                file_name))
                        data_file.close()
                        exit(1)
                    except StopIteration:
                        pass
                    except IndexError:
                        print('SUT at index requested not found. Correct the index number and try again.')
                        exit(1)

                else:
                    try:
                        for rf_sut in data[json_SUT_key][json_SUT_subkey]:
                            # yield server
                            yield verify_sut_prop(rf_sut)
                    except KeyError:
                        print(
                            'Operational ERROR: Decoding JSON configuration file %s - invalid key/keys. Please correct the key values and try again.' % (
                                file_name))
                        data_file.close()
                        exit(1)

            data_file.close()

    except ValueError:
        print('Operational ERROR: Opening/parsing the JSON configuration file %s' % (file_name))
        exit(1)


###############################################################################################
# Name: get_sut_schema_settings()                                               
#   Read properties.json for Redfish schemas directory "LocalSchemaDirectoryFolder"
#   and "RetrieveDMTFSchemas". If RetrieveDMTFSchemas is 'Yes', then read properties.json
#   further for SchemaRepository and ClientProxy and load it in schema_url and proxy_Dict resp.
# Return:
#   retrieve_dmtf_schemas: yes/no, schema directory path, schema repo url and proxy setting
#   else exits tool if any issue found in reading properties.json with error message
###############################################################################################
def get_sut_schema_settings():
    schema_directory = ''
    schema_repo_url = ''
    schema_zipfile = ''
    schema_zip_url = ''
    proxy_Dict = {}
    retrieve_dmtf_schemas = ''

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File)

    print('')
    try:
        with open(file_name) as data_file:
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(1)
            else:
                # top level keys into the json file for the schema file location info
                Metadata_key = "RedfishServiceCheckTool_SchemaFiles"
                LocalDir_key = "LocalSchemaDirectoryFolder"
                GetSchemaYesNo_key = "RetrieveDMTFSchemas"
                DMTFSchemas_key = "DMTF_SPMFSchemas"

                try:
                    schema_directory = data[Metadata_key][LocalDir_key]
                except:
                    print('Operational ERROR: Decoding JSON failed (%s : %s)' % (Metadata_key, LocalDir_key))
                    data_file.close()
                    exit(1)

                try:
                    retrieve_dmtf_schemas = data[Metadata_key][GetSchemaYesNo_key]
                except:
                    print('Operational ERROR: Decoding JSON failed (%s : %s)' % (Metadata_key, GetSchemaYesNo_key))
                    data_file.close()
                    exit(1)
                else:
                    retrieve_dmtf_schemas = retrieve_dmtf_schemas.lower()
                    if retrieve_dmtf_schemas not in ['yes', 'no', 'auto']:
                        print(
                            'Operational ERROR: "{}" key "{}" in {} has a value of "{}". It must have a value of "yes", "no" or "auto".'
                            .format(Metadata_key, GetSchemaYesNo_key, file_name, retrieve_dmtf_schemas))
                        data_file.close()
                        exit(1)

                    if retrieve_dmtf_schemas == 'no':
                        data_file.close()
                    else:
                        DMTFSchemas_subkey = "SchemaRepository"
                        try:
                            schema_repo_url = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey]
                        except:
                            print('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (
                                Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                            data_file.close()
                            exit(1)
                        else:
                            try:
                                DMTFSchemas_subkey = "SchemaZipFileName"
                                schema_zipfile = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey]
                            except:
                                print('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (
                                    Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                                data_file.close()
                                exit(1)

                            if not schema_repo_url.endswith('/'):
                                schema_repo_url += '/'
                            schema_zip_url = urljoin(schema_repo_url, schema_zipfile)
                            print('Schemas zip URL = {}'.format(schema_zip_url))

                            DMTFSchemas_subkey = "ClientProxy"
                            https_subkey = 'https_proxy'
                            http_subkey = 'http_proxy'
                            try:
                                http_proxy = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey][http_subkey]
                                if http_proxy is not None and http_proxy.lower() != "none":
                                    proxy_Dict['http'] = http_proxy
                                https_proxy = data[Metadata_key][DMTFSchemas_key][DMTFSchemas_subkey][https_subkey]
                                if https_proxy is not None and https_proxy.lower() != "none":
                                    proxy_Dict['https'] = https_proxy
                                print('Schema download proxies = {}'.format(proxy_Dict))
                            except:
                                print('Operational ERROR: Decoding JSON failed (%s : %s : %s)' % (
                                    Metadata_key, DMTFSchemas_key, DMTFSchemas_subkey))
                                data_file.close()
                                exit(1)

            data_file.close()

    except ValueError:
        print('Operational ERROR: Opening/parsing the JSON configuration file %s' % file_name)
        exit(1)

    return retrieve_dmtf_schemas, schema_directory, schema_zip_url, proxy_Dict


###############################################################################################
# Name: get_eventservice_params                                             
#   Read the config json file for the event service parameters
# Return:
#  exit(1) on syntax error reading json file
###############################################################################################
def get_eventservice_params():
    # keys into the json file
    Event_key = "RedfishServiceCheckTool_Event"
    Subscription_subkey = "Subscription"
    Submit_test_event_subkey = "SubmitTestEvent"
    Event_Subscription = {}
    Submit_Test_Event = {}

    script_dir = os.path.dirname(__file__)
    file_name = os.path.join(script_dir, Server_Auth_Json_File)

    try:
        with open(file_name) as data_file:
            try:
                data = json.load(data_file)
            except ValueError as err:
                print("Error trying to load JSON from %s - check your JSON syntax" % file_name)
                print(err)
                data_file.close()
                exit(1)
            else:
                try:
                    event_subscription = data[Event_key][Subscription_subkey]
                except:
                    print("ERROR: Decoding JSON configuration file %s - unable to find %s %s keys" % (
                    file_name, Event_key, Subscription_subkey))
                    exit(1)

                try:
                    EVENT_subscription = {
                        # grab info from the JSON file...
                        'Destination': event_subscription['Destination'],
                        'EventTypes': event_subscription['EventTypes'],
                        'Context': event_subscription['Context'],
                        'Protocol': event_subscription['Protocol']
                    }
                    Event_Subscription = EVENT_subscription

                except:
                    print('- ERROR decoding %s - one or more %s:%s subkeys is invalid' % (
                    file_name, Event_key, Subscription_subkey))
                    print('- expecting keys: Destination, EventTypes, Context, Protocol, HttpHeaders')
                    data_file.close()
                    exit(1)

                try:
                    submit_event_subscription = data[Event_key][Submit_test_event_subkey]
                except:
                    print("ERROR: Decoding JSON configuration file %s - unable to find %s %s keys" % (
                    file_name, Event_key, Subscription_subkey))
                    exit(1)

                try:
                    TEST_event = {
                        # grab info from the JSON file...
                        'Action': submit_event_subscription['Action'],
                        'EventType': submit_event_subscription['EventType'],
                        'EventId': submit_event_subscription['EventId'],
                        'EventTimestamp': submit_event_subscription['EventTimestamp'],
                        'Severity': submit_event_subscription['Severity'],
                        'Message': submit_event_subscription['Message'],
                        'MessageId': submit_event_subscription['MessageId'],
                        'MessageArgs': submit_event_subscription['MessageArgs'],
                        'OriginOfCondition': submit_event_subscription['OriginOfCondition']
                    }
                    Submit_Test_Event = TEST_event

                except:
                    print('- ERROR decoding %s - one or more %s:%s subkeys is invalid' % (
                    file_name, Event_key, Submit_test_event_subkey))
                    print(
                        '- expecting keys: Action, EventType, EventId, EventTimestamp, Severity, Message, MessageId, MessageArgs, OriginOfCondition')
                    data_file.close()
                    exit(1)

            data_file.close()

    except ValueError:
        print('Operational ERROR: Opening/parsing the JSON configuration file %s' % file_name)
        exit(1)

    return Event_Subscription, Submit_Test_Event


def extract_schema_files(schema_url, zip_file, temp_dir_name, schema_path, file_ext, schema_type):
    """
    Extract schema files of the given extension into a temp dir and then move them to the target dir
    :param schema_url: the URL of the zip file holding the schemas
    :param zip_file: the ZipFile object
    :param temp_dir_name: the name of the temp dir to extract into
    :param schema_path: target dir to move the schema files into
    :param file_ext: the file extension of the schemas to extract
    :param schema_type: a description string for the type of schemas to be extracted
    :return: True on success, False otherwise
    """
    try:
        members = [file for file in zip_file.namelist() if file.endswith(file_ext)]
        for member in members:
            file = zip_file.extract(member=member, path=temp_dir_name)
            os.rename(file, os.path.join(schema_path, os.path.basename(file)))
        print('Downloaded {} schema files into directory {}'.format(schema_type, schema_path))
    except Exception as e:
        print('Unable to extract {} schema files from zip {}. Exception is "{}"'
              .format(schema_type, schema_url, e), file=sys.stderr)
        return False
    return True


def download_schemas(schema_zip_url, dest_directory, proxies):
    """
    Download schema files into sub-dirs dest_directory/json-schema/ and dest_directory/metadata/.
    :param schema_zip_url: URL of the location of the schemas ZIP file (e.g. http://redfish.dmtf.org/schemas/DSP8010_2017.3.zip)
    :param dest_directory: local directory where the schemas will be extracted into
    :param proxies: proxies dictionary for downloading schemas via a proxy
    :return: True on success, False otherwise
    """
    json_path = os.path.normpath(os.path.join(os.getcwd(), dest_directory, 'json-schema'))
    csdl_path = os.path.normpath(os.path.join(os.getcwd(), dest_directory, 'metadata'))

    # Remove old schemas if needed
    if os.path.exists(json_path):
        shutil.rmtree(json_path)
    if os.path.exists(csdl_path):
        shutil.rmtree(csdl_path)

    # Create dirs if needed
    try:
        if not os.path.isdir(json_path):
            os.makedirs(json_path)
        if not os.path.isdir(csdl_path):
            os.makedirs(csdl_path)
    except OSError as e:
        print('Error creating target subdirectories {} and/or {}. Exception is "{}"'
              .format(json_path, csdl_path, e), file=sys.stderr)
        return False

    # Fetch schemas zip file if needed
    z = temp_dir = temp_dir_name = None
    # create temp dir to hold extracted zip files
    try:
        temp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
        temp_dir_name = temp_dir.name
    except Exception as e:
        print('Unable to create temp dir for schema extraction. Exception is "{}"'.format(e), file=sys.stderr)
        if temp_dir is not None:
            temp_dir.cleanup()
        return False
    # fetch the remote zip file
    try:
        r = requests.get(schema_zip_url, stream=True, proxies=proxies)
        if r.status_code != requests.codes.ok:
            print('Unable to retrieve schemas zip at {}, status code = {}'
                  .format(schema_zip_url, r.status_code), file=sys.stderr)
            if temp_dir is not None:
                temp_dir.cleanup()
            return False
        z = zipfile.ZipFile(io.BytesIO(r.content), mode='r')
    except Exception as e:
        print('Unable to read schemas zip at {}. Exception is "{}"'.format(schema_zip_url, e), file=sys.stderr)
        if temp_dir is not None:
            temp_dir.cleanup()
        return False

    # Extract JSON schemas
    rc = extract_schema_files(schema_zip_url, z, temp_dir_name, json_path, '.json', 'JSON')

    # Extract CSDL schemas
    if rc:
        rc = extract_schema_files(schema_zip_url, z, temp_dir_name, csdl_path, '.xml', 'CSDL')

    if temp_dir is not None:
        temp_dir.cleanup()

    return rc


###############################################################################################
# Name: verify_local_files(schema_directory)                                      
#   Takes local schema directory path and verifies if the required subfolders are present and 
#   not empty
# Return:
#   True if all is good, else False
# Condition:
#   If schema folder/files are not found in the directory, tool exits with an error message
###############################################################################################
def verify_local_schemas(schema_directory):
    xml_path = os.path.join(schema_directory, xml_directory)
    json_path = os.path.join(schema_directory, json_directory)
    if not os.path.isdir(schema_directory) or not os.listdir(schema_directory):
        return False
    if not os.path.isdir(xml_path) or not os.listdir(xml_path):
        return False
    if not os.path.isdir(json_path) or not os.listdir(json_path):
        return False
    return True


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
def get_remote_schemas(schema_zip_url, proxy_Dict, schema_directory):
    # retrieve DMTF/SPMF metadata files from the paths/url specified in properties.json
    print("Downloading schema files from %s to directory %s" % (schema_zip_url, schema_directory))

    if not download_schemas(schema_zip_url, schema_directory, proxy_Dict):
        print('Error retrieving/unzipping schema files.')
        print('Either set "{}" to "no" to disable retrieval of the'.format('RetrieveDMTFSchemas'))
        print('DMTF Schemas or set "{}" to a local pathname where the'.format('LocalSchemaDirectoryFolder'))
        print('metadata files can be found (see properties.json).')
        exit(1)
    else:
        print("Schema files successfully downloaded to {}.".format(schema_directory))
        return True


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
    # 1.Get schema file settings from properties.json
    retrieve_dmtf_schemas, schema_directory, schema_zip_url, proxy_Dict = get_sut_schema_settings()
    ## Remove the following 2 lines of script if a custom schema directory is provided in the properties.json 
    ## current script file directory, folders should be in this directory
    script_dir = os.path.dirname(__file__)
    # this is the folder where we read/write schema files
    schema_directory = os.path.join(script_dir, schema_directory)

    # 2. Configuration settings successfully parsed; check if local/online metadata is to be
    # used or retrieved remotely
    if retrieve_dmtf_schemas == 'yes':
        print('RetrieveDMTFSchemas is "yes"; will download schemas')
        get_remote_schemas(schema_zip_url, proxy_Dict, schema_directory)
    elif retrieve_dmtf_schemas == 'no':
        print('RetrieveDMTFSchemas is "no"; will not download schemas')
        if not verify_local_schemas(schema_directory):
            print('Local schema directory {} does not appear to contain schemas.'.format(schema_directory))
            print('Either set "{}" to "yes" or "auto" to enable retrieval of the'.format('RetrieveDMTFSchemas'))
            print('DMTF Schemas or set "{}" to a local pathname where the'.format('LocalSchemaDirectoryFolder'))
            print('metadata files can be found (see properties.json).')
            exit(1)
    else:  # 'auto' case
        print('RetrieveDMTFSchemas is "auto"; will download schemas if needed')
        if not verify_local_schemas(schema_directory):
            get_remote_schemas(schema_zip_url, proxy_Dict, schema_directory)

    # 3. Schema files successfully retrieved, walk down the directory to serialize each schema
    # file. xml_directry is where we expect CSDL (.xml) schema files
    xml_directory_path = os.path.join(schema_directory, xml_directory)
    # json_directory_path
    json_directory_path = os.path.join(schema_directory, json_directory)

    # verify files are available in dir
    if xml_directory_path:
        if not os.listdir(xml_directory_path):
            print(
                'CSDL schemas not found in %s. Please make sure files are in place or proper properties.json settings are set for schema files and try running the tool again.' % (
                    xml_directory_path))
            exit(1)
        else:
            print('\nSerializing CSDL Schemas located at: %s' % (xml_directory_path))
            for dirpath, dirnames, files in os.walk(xml_directory_path):
                for schema_file in files:
                    csdl_schema_model.serialize_schema(os.path.join(dirpath, schema_file))

    # verify files are available in dir
    if json_directory_path:
        if not os.listdir(json_directory_path):
            print(
                'JSON schemas not found in %s. Please make sure files are in place or proper properties.json settings are set for schema files and try running the tool again.' % (
                    json_directory_path))
            exit(1)

    # 4. save the instance of schema model and directory paths in sut
    sut.csdl_schema_model = csdl_schema_model
    sut.schema_directory = schema_directory
    sut.xml_directory = xml_directory_path
    sut.json_directory = json_directory_path

    return True

    # TODOS
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
        print("Protocol version and Service Root uri could not be retrieved through '%s', assuming spec mandated values"
              % (sut.Redfish_URIs['Protocol_Version']))
        protocol_version, service_root = 'v1', '/redfish/v1/'
    # 2.1 Set protocol version for this sut in the tool
    sut.set_protocol_version(protocol_version)
    # 2.2 set appropraite values for sut's redfish-defined uris based on its service root 
    sut.set_redfish_defined_uris(service_root)

    # 3. gets service top level resources links by parsing service odata document
    odata_context, odata_values = sut.parse_odatadoc_payload(sut.Redfish_URIs['Service_Odata_Doc'])
    # 3.1 Set odatacontext for this tool
    sut.set_odata_context(odata_context)
    # 3.2 Set odatavalues for this tool
    sut.set_odata_values(odata_values)

    # 4. gets service top level resources links by parsing service root uri
    sr_toplevel_uris = sut.parse_serviceroot_toplevel_uris(sut.Redfish_URIs['Service_Root'])
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

    print('\nSerializing SUT metadata document: %s ...' % (sut.Redfish_URIs['Service_Metadata_Doc']))
    # 7. parsing $metadata in a structure for several good information, 
    # WIP verifying odata versions, retreiving schema version, and identifying service errors, if any
    metadata_document_structure = sut.parse_metadata_document(sut.Redfish_URIs['Service_Metadata_Doc'])
    if metadata_document_structure:
        sut.set_metadata_document_structure(metadata_document_structure)
    else:
        print('Unable to parse Service Metadata Document %s' % (sut.Redfish_URIs['Service_Metadata_Doc']))

    # 8. set up schema documents for this sut's redfish service
    setup_schemas(sut)

    # 9. optional if running assertion 8.x
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
    print('Setting up Redfish Service Check Tool Revision: %s : %s:%s' % (
        RedfishServiceCheck_Revision, sut_prop['DisplayName'], sut_prop['DnsName']))
    # tool initiates service object
    sut = init_sut_obj(sut_prop)
    # setup sut obj for sut
    if setup_sut_obj(sut):
        print('\nRedfish Service Check Tool setup for SUT %s successfully completed' % (sut_prop['DnsName']))
        return sut
    else:
        print('\nSetup of client tool was not successful, Redfish Service Check Tool will exit...')
        exit(1)


###############################################################################################
# Name: main
# Start up function. Invokes appropriate setup functions to run Redfish Service Check Tool
###############################################################################################
def main():
    # step through the json server configuration file, checking the assertions against each server/SUT...
    SUTs = get_sut_prop()
    for sut_prop in SUTs:
        if sut_prop:
            # initialize tool before anything else..this sets up all the necessary variables for this sut in this tool
            sut = setup_tool(sut_prop)
            print('Running assertions on SUT %s...' % (sut_prop['DnsName']))
            rfs_test.run(sut)
        else:
            print(
                'No SUT found in properties.json. Please add an SUT following the format provided in readme.txt and try running the Redfish Service Check Tool again')
            exit(1)


if __name__ == "__main__":
    main()
