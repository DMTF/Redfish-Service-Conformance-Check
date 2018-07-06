# Change Log

## [1.1.0] - 2018-07-06
- Added change to use a higher level of TLS
- Changed default password used for test cases
- Fixes to tests that check for resource changes after a PATCH

## [1.0.9] - 2018-06-01
- Updated schema bundle to use the 2018.1 release

## [1.0.8] - 2018-05-04
- Fixed schema download to use a zip file instead of downloading them individually

## [1.0.7] - 2018-04-27
- Made fix to allow for the Oem property to be inside of Actions

## [1.0.6] - 2018-04-13
- Added type checking of responses to ensure they're JSON objects

## [1.0.5] - 2018-03-16
- Fixed test cases that validated redirect handling
- Corrected primitive type checking done in schemas

## [1.0.4] - 2018-03-09
- Fixed bug where it was not able to handle multiple properties of the same name in different objects in the same payload
- Fixed bug where the members of a collection were not being handled properly when validating the usage of `@odata.nextLink`
- Fixed test cases where it was validating the response of an Action, but not handling corner cases appropriately
- Corrected check for the HEAD method; this is not required to be supported on a service
- Corrected Allow header check; this is only mandatory when the HTTP status code is 405

## [1.0.3] - 2018-03-02
- Corrected the enforcement of the Allow header on GET requests
- Hardened the validation of error responses
- Added initial test cases for validating normative language in the AccountService schema

## [1.0.2] - 2018-02-15
- Modified tests for POST to a collection and DELETE from a collection to use the SessionService instead of AccountService

## [1.0.1] - 2018-02-02
- Modified assertion 6.1.8.4 to perform create/delete testing on Sessions rather than Accounts

## [1.0.0] - 2018-01-26
- Various bug fixes; getting into standard release cadence

## [2016.09] - 2016-09-22
- Initial Release to public

## [2016.07] - 2016-07-07
- Code changes in rf_client.py, It is now a script that is used to setup the tool for any given sut (system under test)
- Added schema.py with schemamodel class to serialize/parse schema files into appropriate structures representing CSDL elements used for section 6 and 7 assertions. Added search functions for these structures
- Retrieved relative uris (nested resources) starting from service root so the scope of assertions can be expanded to run on all the resources exposed by the service
- Added an option to retrieve DMTF schemas locally on system or remotely from http://redfish.dmtf.org/schemas with proxy settings, if applicable (see work in progress item below)
- Refactored classes/functions for more flexible usage 
- Created a seperate class for sut and log (rf_sut.py and logger.py). rf_sut also serves as an API for rf_utililty which does more HTTP related work under the hood 
- Updated log to generate a new excel result file everyone tool runs according to date time stamp
- Created assertion test files for each section of the redfish specification in rfs_test
- Added a sample_run file to demonstrate how the tool runs - Added Redfish Service Check Tool Help document to demonstrate use of tool's modules and their functionalities via python command line or code/script

## [2016.04] - 2016-04-12
- Added utility class/function support:
    - properties.json controls added: download schema files from dmtf URI/location
    - utilty functions added to exaustively parse/scan schema/metadata files
- Added Assertion coverage for section 7 (Data Model & Schema)

## [2016.03] - 2016-03-21
- This tool revision has been run on a second OEM production level Service
- Code changes were made to the HTTP connection functions
- Assertions were 'normalized' based on the 2 Service interpretations of the Redfish spec 
- Increased assertion coverage for Sections 6, 8 and 9
- Utility fuction support for section 7: map schema namespace to URI for related json payload

## [2016.02] - 2016-02-17

- Added command line options : perform HTTP methods on URIs - GET, POST, PUSH etc.
- Added assertion coverage for  Section 8 (Events) 
- Added assertion coverage for section 9 (Authentication/Security)
- Increased assertion coverage for section 6 (Protocol)
- Added rfs_utility.py to consolodate useful/common functions
- Add user config. parameters for Event Service subscription and Test Event to properties.json
- Add user config. parameters for Metadata file location to properties.json
- Support for python 3.4.2 has been added/verified

## [2016.01] - 2016-01-15
- Initial push to the DMTF/SPMF repository https://github.com/DMTF/spmf.git. 
- This tool revision has been verified against only one Redfish Service 1.0 enabled production server (the only one available in Q4'15). 
