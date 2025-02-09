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
    SELECT
    Patient.FirstName,
    Patient.LastName,
    convert(VARCHAR(19), quick_note.note_tstamp) AS CreationDate,
    author.user_first_name,
    author.user_last_name,
    quick_note.appr_flag,
    convert(varchar(MAX), quick_note.quick_note_text) AS NoteText

    FROM
    variansystem.dbo.Patient Patient,  
    varianenm.dbo.pt pt,
    varianenm.dbo.quick_note quick_note
    INNER JOIN varianenm.dbo.userid author ON quick_note.author_userid=author.stkh_id

    WHERE 
    pt.pt_id = quick_note.pt_id 
    AND pt.patient_ser = Patient.PatientSer
    AND (Patient.PatientId = '$patientID' OR Patient.PatientId2 = '$patientID' )
    ";

    // $query holds results of SQL query in unreadable format
    $query = mssql_query($sql);

    // Create array to hold reable results of the query
    $json = array();

    // Loop through rows in the result of the query
    // Each row is different document
    while($row = mssql_fetch_array($query)){
        if ($row[5] == "Y") {
            $row[5] = "Approved";
        }
        elseif ($row[5] == "N") {
            $row[5] = "Pending";
        }

        $rowArray = array(
            'PatFirstName' => $row[0],
            'PatLastName' => $row[1],
            'CreationDate' => $row[2], // Date/time the note was created
            'AuthFirstName' => $row[3], // First name of person who created the note
            'AuthLastName' => $row[4], // Last name of person who created the note
            'ApprovalStatus' => $row[5], // Indicates whether note has been approved
            'NoteText' => $row[6] // Actual text of the note
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