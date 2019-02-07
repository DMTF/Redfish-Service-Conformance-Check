Copyright 2016-2018 DMTF. All rights reserved.

# Redfish Service Conformance Check Tool

This tool checks an operational Redfish Service to see that it conforms to the normative statements from the Redfish specification (see assertions in redfish-assertions.xlxs).   Assertion coverage is growing (development in process) and future revisions of the tool will increase coverage of the Assertions. To see which Assertions are covered by a revision - run the tool and look at the markup to the SUTs copy of the xlxs file after the check is run.

This program has been tested with Python 2.7.10 and 3.4.3.

## Installation and Invocation

1. Install one of the python revisions noted as 'verified' (any 2.7+ or 3.4+ "should" work... but the current release was checked only with the 'Verified/operational' ones)
2. This tool imports `openpyxl`, `requests` and `beautifulsoup4`, which are not installed by default in python. You will need to install them using 'pip'. Execute the following command:

    `pip install -r requirements.txt`
3. Copy the 'files included in this test package' into the python.exe installation directory (or put python.exe in your PATH)
4. Edit `properties.json`
    - Set the login and location parameters for your Redfish Service System Under Test (SUT) in the `properties.json` file.
        - `"SUTs"[]` collection: You can batch SUTs by adding them to the `"SUTs"[]` collection to include them in the next run of rf_client.py.
        - `"DisplayName"` (required) is a string for your choice of display name for the SUT
        - `"DnsName"` (required) is the domain name or ip address of the SUT
        - `"LoginName"` (required) is the login name for the SUT
        - `"Password"` (required) is the password for the SUT
        - `"AllowAction_LogServiceClearLog"` (optional): A couple of the assertions verify Actions by sending an Action to Clear the System Log --- if you want to run those (and clear the system log) set `"AllowAction_LogServiceClearLog"` to "yes" -- "no" (or any other string besides "yes") will disable these Clear Log assertions
        - `"SingleAssertion"` (optional): Specify this parameter if you wish to just run a single assertion for this SUT. The parameter value should be the name of one of the test assertion functions, for example `"Assertion_6_1_0"`. If the SingleAssertion parameter is missing or the length of its value is zero, the entire suite of assertions will be run.
        - `"UseHttp"` (optional): By default `https` will be used to connect to the target SUT. To use `http` instead, specify the `"UseHttp"` parameter with a value of `"yes"`.
        - `"NumUrisToCache"` (optional): To reduce runtime, a sampling of the URIs in the SUT can be read and the GET responses cached. If the property is missing, less than or equal to zero, or not an integer, all the URIs in the SUT are processed. If the property specifies a positive integer, that number of URIs are sampled and their GET responses cached.
	- Set the parameters for Schema file download in the `"RedfishServiceCheckTool_SchemaFiles"` section of the `properties.json` file.
	  - `"SchemaZipFileName"` specifies the name of the Redfish Schemas ZIP file to download (e.g. `"DSP8010_2018.3.zip"`)
	  - Under `"ClientProxy"`, set the `"http_proxy"` and/or `"https_proxy"` values as needed use a proxy to reach the redfish.dmtf.org website. Leave them as `"none"` if no proxy is needed.
	  - `"RetrieveDMTFSchemas"` specifies the behavior for schema download. It should normally be left at the default value of `"auto"`. This setting will download a copy of the schemas if they are not already locally present, otherwise it will not download them again. Set the value to `"yes"` to force the tool to download a copy of the schema files. If set to `"no"`, the tool will not perform the download.
	- Set the parameters for Event Subscription and related Test Event generation. Note that the Event related assertions do not verify that a Test Event actually gets delivered to the "Destination" you specify - but the assertions will create a Subscription and request that the Service issue a Test Event to the Subscription "Destination" using the Test Event parameters you set here
5. For operational results, open a terminal window and cd to the directory where you placed the files included with this package (example `C:\rf_client_dir` or `$HOME/rf_client_dir`) and then run rf_client.py at the the command prompt:
 
    `python rf_client.py`
6. Check results:
    - rf_client.py will log results to rf-assertions-log.txt (append) and creates \<timestamp\>_rf-assertions-run.xlxs under script_dir/logs/\<DisplayName\>/ folder.
    - The text log is an appended log for all test runs for SUT \<DisplayName\> but the xlxs files are created each time assertions are run for \<DisplayName\>.
        - For example, if properties.json has SUTs['DisplayName'] "Contoso_server1" then "log/ContosoServer1/ will be created and \<timestamp\>_rf-assertions-run.xlxs" will be created each time you run rf_client.py with "ContosoServer1" configured in properties.json.
    - Red/Yellow/Green = Fail/Warn/Pass.
    - The Assertions which are not covered by the check are not color marked in the xlxs.
    - In order to view the assertion log in an HTML format. Excecute the following command:
     
     `bash viewLog.sh`
        - If a web browser is unavailable due to an SSH/CLI connection with the server, the file HTML_Log_Viewer/AssertionLogs.json can be copied and pasted to a local computer with Redfish Conformance Checker.

## Work in progress items/limitations:

1. Work in progress items are either annotated with 'WIP' or 'todo'. They dont affect the completed portion of the tool which should successfully run.
2. Current implementation for schemas found in local directory (or remotely retrieved) does not guarantee that SUT service is using the same version of the schema files. It is a WIP for this tool. Please make sure that schema file version found in $metadata for SUT is the same as the version of files in the directory to get correct results	

## Release Process

1. Update `CHANGELOG.md` with the list of changes since the last release
2. Update the `Version` property in `HTML_Log_Viewer/Version.json` to reflect the new tool version
3. Push changes to Github
4. Create a new release in Github
