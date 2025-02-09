<?php
    header("Access-Control-Allow-Origin: *");
    define( "ARIA_DB", "" ); # e.g. URL used to access the EMR 127.0.0.1:PORT#\\database
    define( "ARIA_USERNAME", "" ); #
    define( "ARIA_PASSWORD", "" );

    $link = mssql_connect(ARIA_DB, ARIA_USERNAME, ARIA_PASSWORD);

    if (!$link) {
        die('Something went wrong while connecting to MSSQL');
    }

    $patientID = $_POST['patientID'];

    $sql = "
    SELECT DISTINCT
    Patient.LastName,
    Patient.FirstName,
    DATEPART(mm, Patient.DateOfBirth) AS DateOfBirth_mm,
    DATEPART(yyyy, Patient.DateOfBirth) AS DateOfBirth_yyyy,
    Patient.Sex

    FROM

    variansystem.dbo.Patient

    WHERE

    Patient.PatientId = '$patientID'
    ";

    $query = mssql_query($sql);

    $json = array();

    // Should only be one row (i.e. one matching patient)
    while($row = mssql_fetch_array($query)){
        $rowArray = array(
            'LastName' => $row[0],
            'FirstName' => $row[1],
            'DateOfBirth_mm' => $row[2],
            'DateOfBirth_yyyy' => $row[3],
            'Sex' => $row[4]
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