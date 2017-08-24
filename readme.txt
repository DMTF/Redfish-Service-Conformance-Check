  
  
  Tool Revision history:
    01.15.16 : 	Jan 15, 2016 initial push to the DMTF/SPMF repository https://github.com/DMTF/spmf.git. 
               	This tool revision has been verified against only 1 Redfish Service 1.0 enabled production
	       	server (the only one we could get our hands on to develop this code in Q4'15). 
 
    02.17.16 : Feb 17, 2016
               	1. added command line options : perform http methods on URIs - GET, POST, PUSH etc. - see 
                  'Command Line Options' section below.
               	2. added assertion coverage for  Section 8 : Events 
               	3. added assertion coverage for section 9 : Authentication/Security
               	4. increased assertion coverage for section 6 : Protocol
               	5. added rfs_utility.py to consolodate useful/common functions
               	6. add user config. parameters for Event Service subscription and Test Event to properties.json
               	7. add user config. parameters for Metadata file location to properties.json
               	8. support for python 3.4.2 has been added/verified

    03.21.16 : March 21, 2016
               	1. this tool revision has been run on a second OEM production level Service
                  - code changes were made to the http connection functions
                  - assertions were 'normalized' based on the 2 Service interpretations of the Redfish spec 
               	2. increased assertion coverage for Sections 6, 8 and 9
               	3. utility fuction support for section 7: map schema namespace to URI for related json payload

    04.12.16 : April 12, 2016
               	1. utility class/function support added:
                  - properties.json controls added: download schema files from dmtf URI/location
                  - utilty functions added to exaustively parse/scan schema/metadata files
               	2. added Assertion coverage for section 7 Data Model & Schema

    07.11.16 : July 7, 2016
		1. Code changes in rf_client.py, It is now a script that is used to setup the tool for any given sut
	       	2. added schema.py with schemamodel class to serialize/parse schema files into appropriate structures representing CSDL elements used for section 6 and 7 assertions. 
		   Added search functions for these structures
	       	3. retrieved relative uris (nested resources) starting from service root so the scope of assertions can be expanded to run on all the resources exposed by the service
		4. added an option to retrieve DMTF schemas locally on system or remotely from http://redfish.dmtf.org/schemas with proxy settings, if applicable (see work in progress item below)
		5. refactored classes/functions for more flexible usage 
		6. created a seperate class for sut and log (rf_sut.py and logger.py). rf_sut also serves as an API for rf_utililty which does more HTTP related work under the hood 
		7. Updated log to generate a new excel result file everyone tool runs according to date time stamp
		8. created assertion test files for each section of the redfish specification in rfs_test
		9. added a sample_run file to demonstrate how the tool runs  
		10. Added Redfish Service Check Tool Help document to demonstrate use of tool's modules and their functionalities via python command line or code/script
		
	04.13.17 : April 13, 2017
		   1. Initial Tool Testing 
		   2. Updated the assertion file with current version of specification 
	           3. Tested the existing assertions and added more assertions for the Protocol and Data Model Testing
		   4. Tested with both Mockup and Real Server 
		   5. A UI - client_gui for the tool is developed to enter credentials and clear out the login information at the end of the testing. This way no need to enter the credential details in properties.json file. The UI will take care of it.

   ----

  Redfish Service conformance check tool - Operational notes...
  
 
  This tool checks an operational Redfish Service to see that it conforms to the 
    normative statements from the Redfish specification (see assertions in 
    redfish-assertions.xlxs).   Assertion coverage is growing (development in process)
    and future revisions of the tool will increase coverage of the Assertions. To see
    which Assertions are covered by a revision - run the tool and look at the markup to 
    the SUTs copy of the xlxs file after the check is run (see below).

  SUT: System under test
 
  Files included in this package:
     - client_gui.py - this file displays the UI for redfish conformance test. The Run_Conformance_Test button calls rf_client.py. Tere are dependencies to run this file for eg. tkinter. In this version pythongui.py will be the starting file (set as startup file) that will internally call other python files. This also updates the SUTs in the properties.json file with the information entered, this information is furthur used by rf_client. 
    - rf_client.py - sets up Redfish Check client w.r.t SUT
    - rf_utility.py: Basic HTTP connection and requests functions, and functions related to http request/response headers and body
    - rfs_test: contains implementation of assertions provided in script_dir/assertions/rf-assertions.xlxs
    - rf_sut.py: SUT class which stores sut related information per instance and functions related to requesting/using redfish service and resources available on SUT.
    - schema.py : This module contains data structures as per CSDL format and Class to store serialized CSDL schema files with functions related to verify/search/return items in the serialized schemas
    - logger.py : This module contains functionalities for logging for this tool. Currently it can handle command line, excel spreadsheet logging and a simple text logging based on parameters passed.
    - sample_run.py : Provides a sample script for running the tool to run assertions.
    - properties.json: Server location and authorization paramenters are read from 
      this file.  This is where you enter parameters to allow this tool to locate 
      your Redfish Service and connect - see step 4 below.
    - redfish-assertions.xlxs: this file contains the 'assertions' (rules/normatives) 
      derived from the Redfish specification which the assertion code is written to verify.
      During a test run, a copy of this .xls file is made to script_dir/logs/<DisplayName>/<timestamp>_rf-assertions-run.xlxs and 
      then marked to show which assertions have been run (pass/fail/warn) - where <DisplayName> is 
      read from the properties.json file by rf_client and set by rfs_test at test initialization
 .
 
  Verified/operational Python revisions (Windows OS):
        2.7.10
        3.4.3

 
  Setup:
    1. install one of the python revisions noted as 'verified' (any 2.7+ or 3.4+ "should" work... but
       the current release was checked only with the 'Verified/operational' ones)
    2. This tool imports openpyxl:
       openpyxl is not a default install for python - you will need to install it using 'pip'... 
         -- to install it...
            cd to where your python.exe is installed and then into the /Scripts subdirectory 
            to run pip.exe... 
 	        note: if you are behind a firewall you may need to specify a proxy server to get 
                to the installation server..
 
            C:\your_python>  pip --proxy <hostname>:<port> install openpyxl
 
    3. copy the 'files included in this test package' into the python.exe installation directory (or put 
       python.exe in your PATH)
    4. Run client_gui.py which will take care of all the credentials enterance in SUT and in the end will provide you an option to delete those credentials for the security purpose or edit properties.json 
    5. If you choose to edit properties.json file manually:
       a. set the login and location parameters for your Redfish Service SUTs 
          in the properties.json file.  
            - "SUTs[]" collection, You can batch SUTs by adding them to the "SUTs[]" 
               collection to include them in the next run of rf_client.py.  
	    - DisplayName(required) is a string for your choice of display name for the SUT
	    - DnsName(required) is the domain name or ip address of the SUT
	    - LoginName(required) is the Login id for the SUT
            - Password(required) is the password for the SUT
            - "AllowAction_LogServiceClearLog": A couple of the assertions verify Actions by
              sending an Action to Clear the System Log --- if you want to run those (and clear the
              system log) set "AllowAction_LogServiceClearLog" to "yes" 
              -- "no" (or any other string besides "yes") will disable these Clear Log assertions
       b. set the parameters for Metadata file download include proxy setting, if applicable or set values to 'none'
       c. set the parameters for Event Subscription and related Test Event generation. Note that the Event related 
          assertions do not verify that a Test Event actually gets delivered to the "Destination" you specify - but the 
          assertions will create a Subscription and request that the Service issue a Test Event to the 
          Subscription "Destination" using the Test Event parameters you set here
 
  Operation/results:
    5. open a dos box and cd to the directory where you placed the files included with this 
       package (example C:\rf_client_dir) and then run client_gui.py which will internally call rf_client.py
        C:\rf_client_dir> python client_gui.py (make sure openpyxl is installed with this version of python else it will error out)
 
 
    6. Check results: rf_client.py will log results to rf-assertions-log.txt (append) and 
       creates a <timestamp>_rf-assertions-run.xlxs under script_dir/logs/<DisplayName>/ folder.
       The text log is an appended log for all test runs for SUT <DisplayName> but the xlxs files are created each time assertions are run 
       run for <DisplayName>.  For example if properties.json has SUTs['DisplayName']  "Contoso_server1"
       then "log/ContosoServer1/ will be created and <timestamp>_rf-assertions-run.xlxs" will be created each time you run 
       rf_client.py with "ContosoServer1" configured in properties.json.  Red/Yellow/Green = Fail/Warn/Pass.
       The Assertions which are not covered by the check are not color marked in the xlxs.
  
  Work in progress items/limitations:
	1. Work in progress items are either annotated with 'WIP' or 'todo'. They dont affect the completed portion of the tool which should successfully run.
	

  
