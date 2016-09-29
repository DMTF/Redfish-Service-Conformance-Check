Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# Redfish Service Conformance Check Tool
This tool checks an operational Redfish Service to see that it conforms to the normative statements from the Redfish specification (see assertions in redfish-assertions.xlxs).   Assertion coverage is growing (development in process) and future revisions of the tool will increase coverage of the Assertions. To see which Assertions are covered by a revision - run the tool and look at the markup to the SUTs copy of the xlxs file after the check is run.

This program has been tested with Python 2.7.10 and 3.4.3.
## Installation and Invocation ##
1. Install one of the python revisions noted as 'verified' (any 2.7+ or 3.4+ "should" work... but the current release was checked only with the 'Verified/operational' ones)
2. This tool imports openpyxl. openpyxl is not a default install for python - you will need to install it using 'pip'. Execute the following command:

    C:\your_python>  pip --proxy <hostname>:<port> install openpyxl
3. Copy the 'files included in this test package' into the python.exe installation directory (or put python.exe in your PATH)
4. Edit properties.json
	- Set the login and location parameters for your Redfish Service SUTs in the properties.json file.  
    	- "SUTs[]" collection, You can batch SUTs by adding them to the "SUTs[]" collection to include them in the next run of rf_client.py.  
	    - DisplayName(required) is a string for your choice of display name for the SUT
	    - DnsName(required) is the domain name or ip address of the SUT
	    - LoginName(required) is the Login id for the SUT
		- Password(required) is the password for the SUT
		- "AllowAction_LogServiceClearLog": A couple of the assertions verify Actions by sending an Action to Clear the System Log --- if you want to run those (and clear the system log) set "AllowAction_LogServiceClearLog" to "yes" -- "no" (or any other string besides "yes") will disable these Clear Log assertions
	- Set the parameters for Metadata file download include proxy setting, if applicable or set values to 'none'
	- Set the parameters for Event Subscription and related Test Event generation. Note that the Event related assertions do not verify that a Test Event actually gets delivered to the "Destination" you specify - but the assertions will create a Subscription and request that the Service issue a Test Event to the Subscription "Destination" using the Test Event parameters you set here
5. For operational results, open a DOS box and cd to the directory where you placed the files included with this package (example C:\rf_client_dir) and then run rf_client.py. (Make sure openpyxl is installed with this version of python else it will error out.)
 
    C:\rf_client_dir> python rf_client.py 
6. Check results:
	- rf_client.py will log results to rf-assertions-log.txt (append) and creates a <timestamp>_rf-assertions-run.xlxs under script_dir/logs/<DisplayName>/ folder.
    - The text log is an appended log for all test runs for SUT <DisplayName> but the xlxs files are created each time assertions are run for <DisplayName>.
    	- For example, if properties.json has SUTs['DisplayName'] "Contoso_server1" then "log/ContosoServer1/ will be created and <timestamp>_rf-assertions-run.xlxs" will be created each time you run rf_client.py with "ContosoServer1" configured in properties.json.
    - Red/Yellow/Green = Fail/Warn/Pass.
    - The Assertions which are not covered by the check are not color marked in the xlxs.


## Work in progress items/limitations:
1. Work in progress items are either annotated with 'WIP' or 'todo'. They dont affect the completed portion of the tool which should successfully run.
2. Current implementation for schemas found in local directory (or remotely retrieved) does not guarantee that SUT service is using the same version of the schema files. It is a WIP for this tool. Please make sure that schema file version found in $metadata for SUT is the same as the version of files in the directory to get correct results	
