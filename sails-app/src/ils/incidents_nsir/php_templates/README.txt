The PHP files included in this directory are templates that may be used to query for
information from the ARIA oncology information system, version 11.0 (Varian Medical Systems, Inc., Palo Alto, California).

These scripts are called within the investigation.js file (ils/incidents_nsir/static/incidents_nsir/js/investigation.js), and return a JSON dictionary containing the results. Thus, if the scripts are modified, investigation.js must be modified accordingly.

To access the functionality offered by these scripts:

1) Copy the files to a new directory on your server that is served to clients, and adjust the PHP_DIR setting in the secret settings file for this project accordingly.

2) In all query files (i.e. named query*.php):
- provide the URL at which your ARIA database is accessible, within the constant ARIA_DB at the top of each script.
- provide the username and password that may be used to query your ARIA database, within the constants ARIA_USERNAME and ARIA_PASSWORD respectively.

3) In downloadPDF.php:
- provide the absolute path and URL at which documents in ARIA may be retrieved, in the loc_docpath and ext_docpath variables respectively.
- provide the absolute path and URL at which the temporarily generated PDF documents (if document needed to be converted to PDF) will be stored (temporarily), in the loc_pdfpath and ext_pdfpath variables respectively.


PLEASE NOTE: Regarding queryTreatment.php:
- The script was designed to retrieve treatment info and facilitate auto-population of Treatment data elements in NSIR-RT. An alogrithm is included in the script to determine a value of the Radiation Treatment Technique data element, but may be specific to the centre in which SaILS was developed (e.g. stereo treatments are identified by presence of specific technical unit notes, but this is unlikely the case at other centres). If you wish to included this functionality, you will need to modify accordingly.