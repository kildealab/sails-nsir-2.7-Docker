<?php
    header("Access-Control-Allow-Origin: *");

    // Manually identify the path to the files which will be converted/served
    // When calling exec() command in php, use the 'loc' prefix variables
    // When setting Content_Disposition header & calling readfile() use 'ext' prefix variables
    $ext_docpath = ""; # URL where documents are stored
                       # e.g. http://127.0.0.1/url/path/
    $loc_docpath = ""; # absolute path where documents are stored
                       # e.g. /absolute/path/to/documents/


    // Location where generated PDF will be stored temporarily until after served to user
    $ext_pdfpath = ""; # URL where temporary PDF will be created
                       # e.g. http://127.0.0.1/temp/folder/
    $loc_pdfpath = ""; # absolute path where temporary PDF will be created
                       # e.g. /absolute/path/to/temp/folder/

    // Store the POSTed filename in a variable, set path to those documents manually
    $inputname = $_POST['filename'];
    // Get extension of input file (e.g doc or pdf), does not include period
    $inputext = pathinfo($inputname, PATHINFO_EXTENSION);

    // if the file is not a PDF file, need to convert to pdf before giving to user:
    if ($inputext != "pdf"){

        // Output a file of same name, but with pdf extension
        $outputname = basename($inputname, ".".$inputext).".pdf";

        // convert the file
        exec('/opt/libreoffice4.3/program/soffice.bin --writer --headless --convert-to pdf --nologo --outdir ' . $loc_pdfpath . ' ' . $loc_docpath . $inputname, $output, $return);

        // Open the file in a new tab
        header("Content-type: application/pdf");
        header("Content-Disposition: inline; filename=\"".basename($ext_pdfpath.$outputname)."\"");
        readfile($ext_pdfpath.$outputname);

        // OR: download the file
        // header("Content-Disposition: attachment; filename=\"".basename($ext_pdfpath.$outputname)."\"");
        // readfile($ext_pdfpath.$outputname);

        // remove the temporary PDF file after serving
        exec('rm ' . $loc_pdfpath . $outputname, $output, $return);

        // if returning via json (ajax post), uncomment the following 3 lines:
        // $json = array();
        // $json = array('a'=>$output, 'b'=>$return);
        // echo json_encode($json);
    } 
    // if the file is a PDF file, just give it to the user (do not call LibreOffice):
    else {
        // Open the file in a new tab
        header("Content-type: application/pdf");
        header("Content-Disposition: inline; filename=\"".basename($ext_docpath.$inputname)."\"");
        readfile($ext_docpath.$inputname);

        // OR: download the file
        // header("Content-Disposition: attachment; filename=\"".basename($ext_docpath.$inputname)."\"");
        // readfile($ext_docpath.$inputname);
    }
?>