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
    PatientNote.PatientNoteCode,
    convert(VARCHAR(19), PatientNote.DisplayDateTime) AS DisplayDate,
    PatientNote.Note,
    PatientNote.WrittenByAppUserName,
    PatientNote.ReadByAppUserName,
    convert(VARCHAR(19), PatientNote.HstryDateTime) AS SignedDate

    FROM
    variansystem.dbo.PatientNote PatientNote,
    variansystem.dbo.Patient Patient

    WHERE
    (Patient.PatientId = '$patientID' OR Patient.PatientId2 = '$patientID' )
    AND PatientNote.PatientSer = Patient.PatientSer
    ";

    // $query holds results of SQL query in unreadable format
    $query = mssql_query($sql);

    // Create array to hold reable results of the query
    $json = array();

    // Loop through rows in the result of the query
    // Each row is different document
    while($row = mssql_fetch_array($query)){
        if (is_null($row[6])){
            $row[6] = "";
        }

        if ($row[2] == "Read by") {
            $row[2] = "Signed";
        }
        elseif ($row[2] == "Open") {
            $row[2] = "Unsigned";
        }

        $rowArray = array(
            'PatFirstName' => $row[0],
            'PatLastName' => $row[1],
            'SignedOffStatus' => $row[2], // Status of the alert (canceled, open, read by)
            'DisplayDate' => $row[3], // "Date and time to display the note"
            'AlertText' => $row[4], // Actual text of the alert
            'AuthUsername' => $row[5], // "User ID of the AppUser who wrote the note"
            'SignedOffBy' => $row[6], // "User ID of the AppUser who read the note"
            'SignedOffDate' => $row[7] // "Date and time the doctor or staff member read the note"
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