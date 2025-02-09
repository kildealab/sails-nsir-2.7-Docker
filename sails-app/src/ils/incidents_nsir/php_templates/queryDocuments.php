<?php
    header("Access-Control-Allow-Origin: *");
    define( "ARIA_DB", "" ); # e.g. URL used to access the EMR 127.0.0.1:PORT#\\database
    define( "ARIA_USERNAME", "" );
    define( "ARIA_PASSWORD", "" );

    $link = mssql_connect(ARIA_DB, ARIA_USERNAME, ARIA_PASSWORD);

    if (!$link) {
        die('Something went wrong while connecting to MSSQL');
    }

    $patientID = $_POST['patientID']; // get patient ID from the calling function

    $sql = "
    SELECT DISTINCT
    Patient.LastName,
    Patient.FirstName,
    Patient.PatientId,
    convert(date, visit_note.note_tstamp) AS CreationDate,
    note_typ.note_typ_desc,
    visit_note.appr_flag,
    author.user_last_name,
    approved.user_last_name,
    visit_note.doc_file_loc,
    visit_note.external_document_link,
    creator.user_last_name,
    signed.user_last_name

    FROM
    variansystem.dbo.Patient Patient,
    varianenm.dbo.pt pt,
    varianenm.dbo.note_typ note_typ,
    varianenm.dbo.visit_note visit_note 
    INNER JOIN varianenm.dbo.userid author ON visit_note.author_stkh_id=author.stkh_id
    LEFT JOIN varianenm.dbo.userid approved ON visit_note.appr_stkh_id=approved.stkh_id
    INNER JOIN varianenm.dbo.userid creator ON visit_note.trans_log_userid=creator.stkh_id
    LEFT JOIN varianenm.dbo.userid signed ON visit_note.signed_stkh_id=signed.stkh_id

    WHERE 
    pt.pt_id = visit_note.pt_id 
    AND pt.patient_ser = Patient.PatientSer
    AND (Patient.PatientId = '$patientID' OR Patient.PatientId2 = '$patientID' )
    AND note_typ.note_typ = visit_note.note_typ
    ORDER BY CreationDate DESC
    ";

    // $query holds results of SQL query in unreadable format
    $query = mssql_query($sql);

    // Create array to hold reable results of the query
    $json = array();

    // Loop through rows in the result of the query
    // Each row is different document
    while($row = mssql_fetch_array($query)){
        if (is_null($row[7])){
            $row[7] = "";
        }
        if (is_null($row[11])){
            $row[11] = "";
        }

        if ($row[5] == "E") {
            $row[5] = "Unapproved";
        }
        elseif ($row[5] == "A") {
            $row[5] = "Approved";
        }

        $rowArray = array(
            'FirstName' => $row[1],
            'LastName' => $row[0],
            'DocName' => $row[4],
            'Author' => $row[6],
            'CreatedBy' => $row[10],
            'ApprovedBy' => $row[7],
            'SignedBy' => $row[11],
            'ServiceDate' => $row[3],
            'URL' => $row[8],
            'ApprovalStatus' => $row[5]
        );
        array_push($json,$rowArray);
    }

    echo json_encode($json);

    /* Free statement and connection resources. */
    if (!$query) {
        die('Query failed.');
    }

    // Free the query result
    mssql_free_result($query);
?>