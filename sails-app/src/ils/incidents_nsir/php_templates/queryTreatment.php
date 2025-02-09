<?php
    header("Access-Control-Allow-Origin: *");
    define( "ARIA_DB", "" ); # e.g. URL used to access the EMR 127.0.0.1:PORT#\\database
    define( "ARIA_USERNAME", "" );
    define( "ARIA_PASSWORD", "" );
    
    define("MAX_CP_STEP_SHOOT", 20);
    define("DAYS_CUTOFF_STEREO", 5);
    define("MIN_SBRT_DPF", 5.0); // In Gy
    define("MIN_SRS_DPF", 8.0); // In Gy

    // Available treatment modalities (verbose names)
    $mods_vlabel = array(
        "MOD_X_SIMPLE" => "Photon EBRT - simple",
        "MOD_X_CONF" => "Photon EBRT - 3DCRT",
        "MOD_X_STEP_SHOOT" => "Photon EBRT - 3DCRT (step and shoot)",
        "MOD_X_CONF_ARC" => "Photon EBRT - SBRT/SRS (dynamic arc)",
        "MOD_X_CONF_CONE" => "Photon EBRT - SBRT/SRS (cones)",
        "MOD_X_IMRT" => "Photon EBRT - IMRT",
        "MOD_X_ARC" => "Photon EBRT - VMAT",
        "MOD_X_SBRT" => "Photon EBRT - SBRT",
        "MOD_X_SRS" => "Photon EBRT - SRS",
        "MOD_X_TBI" => "Photon EBRT - TBI",
        "MOD_E_EBRT" => "Electron EBRT",
        "MOD_E_TSEI" => "TSEI",
        "MOD_BRACHY_LUM" => "Brachytherapy - intraluminal",
        "MOD_BRACHY_CAV" => "Brachytherapy - intracavitary",
        "MOD_BRACHY_SUR" => "Brachytherapy - surface",
        "MOD_BRACHY_INT" => "Brachytherapy - interstitial",
        "MOD_BRACHY_LDR" => "Brachytherapy - LDR",
        "MOD_BRACHY_HDR" => "Brachytherapy - HDR",
        "MOD_OTHER" => "Undetermined",
    );

    // Availabel treatment modalities (primary keys in SaILS)
    $mods_pk = array(
        "MOD_X_SIMPLE" => 1,
        "MOD_X_CONF" => 2,
        "MOD_X_STEP_SHOOT" => 2,
        "MOD_X_CONF_ARC" => 5,
        "MOD_X_CONF_CONE" => 5,
        "MOD_X_IMRT" => 3,
        "MOD_X_ARC" => 4,
        "MOD_X_SBRT" => 5,
        "MOD_X_SRS" => 5,
        "MOD_X_TBI" => 15,
        "MOD_E_EBRT" => 7,
        "MOD_E_TSEI" => 15,
        "MOD_BRACHY_LUM" => 8,
        "MOD_BRACHY_CAV" => 8,
        "MOD_BRACHY_SUR" => 8,
        "MOD_BRACHY_INT" => 9,
        "MOD_BRACHY_LDR" => 10,
        "MOD_BRACHY_HDR" => 12,
        "MOD_OTHER" => 15,
    );

    $link = mssql_connect(ARIA_DB, ARIA_USERNAME, ARIA_PASSWORD);
    //echo "Got a link<br>";

    if (!$link) {
        die('Something went wrong while connecting to MSSQL');
    }

    $patientID = $_POST['patientID']; // get patient ID from the calling function

    $sql = "
    use variansystem;
    SELECT DISTINCT
    pt.LastName,
    pt.FirstName,
    ci.ConfigValue,
    co.CourseId,
    ps.PlanSetupId,
    convert(date, ps.CreationDate) AS CreationDate,
    co.ClinicalStatus,
    ps.Status,
    ps.StatusUserName,
    rt.NoFractions,
    rt.PrescribedDose,
    rad.RadiationId,
    eng.RadiationType,
    mach.MachineId,
    mlc.MLCPlanType,
    mlc.IndexParameterType,
    tech.TechniqueId,
    COUNT(cp.ControlPointSer) AS NumControlPoints

    FROM
    Patient pt

    INNER JOIN Course co ON pt.PatientSer = co.PatientSer
    INNER JOIN PlanSetup ps ON co.CourseSer = ps.CourseSer
    INNER JOIN RTPlan rt ON ps.PlanSetupSer = rt.PlanSetupSer
    INNER JOIN Radiation rad ON ps.PlanSetupSer = rad.PlanSetupSer
    LEFT JOIN ControlPoint cp ON rad.RadiationSer = cp.RadiationSer
    LEFT JOIN ExternalFieldCommon efc ON rad.RadiationSer = efc.RadiationSer
    LEFT JOIN EnergyMode eng ON efc.EnergyModeSer = eng.EnergyModeSer
    INNER JOIN Technique tech ON efc.TechniqueSer = tech.TechniqueSer
    LEFT JOIN Machine mach ON rad.ResourceSer = mach.ResourceSer
    LEFT JOIN MLCPlan mlc ON rad.RadiationSer = mlc.RadiationSer
    INNER JOIN ConfigurationItem ci ON ci.ConfigurationItemId = 'Dose'

    WHERE
    (pt.PatientId = '$patientID' OR pt.PatientId2 = '$patientID')
    AND ps.Status IN ('TreatApproval', 'PlanApproval', 'Reviewed', 'Completed', 'Retired')
    AND efc.SetupFieldFlag = 0

    GROUP BY
    pt.LastName,
    pt.FirstName,
    ci.ConfigValue,
    co.CourseId,
    ps.PlanSetupId,
    ps.CreationDate,
    co.ClinicalStatus,
    ps.Status,
    ps.StatusUserName,
    rt.NoFractions,
    rt.PrescribedDose,
    rad.RadiationId,
    eng.RadiationType,
    mach.MachineId,
    mlc.MLCPlanType,
    mlc.IndexParameterType,
    tech.TechniqueId

    ORDER BY
    co.CourseId DESC,
    ps.PlanSetupId,
    rad.RadiationId
    ";

    // $query holds results of SQL query in unreadable format
    $query = mssql_query($sql);

    // Create array to hold reable results of the query
    $json = array();

    // Loop through rows in the result of the query
    $index = 0;
    while($row = mssql_fetch_array($query)){
        $json[$index] = $row;
        $index = $index + 1;
    }

    $numrows = sizeof($json); // holds number of entries (i.e. number of fields)

    //------------------------------------------------------------------------------------
    // Now query NonScheduled Activities to see if there are any Technical units to
    // indicate that the treatment is a stereo treatment (by comparing date of activity
    // to dates of plans). But this query just determines if there are any Stereo technical
    // units for the patient.
    mssql_free_result($query);

    $sbrt_sql = "
    use variansystem;
    SELECT DISTINCT
    pt.PatientId,
    act.ActivityCode,
    convert(date, sact.CreationDate) AS TaskDate

    FROM
    Patient pt
    INNER JOIN NonScheduledActivity sact ON pt.PatientSer = sact.PatientSer
    INNER JOIN ActivityInstance acti ON sact.ActivityInstanceSer = acti.ActivityInstanceSer
    INNER JOIN Activity act ON acti.ActivitySer = act.ActivitySer

    WHERE
    (pt.PatientId = '$patientID' OR pt.PatientId2 = '$patientID')
    AND (
        UPPER(act.ActivityCode) LIKE UPPER('%TX_FSRT%')
        OR UPPER(act.ActivityCode) LIKE UPPER('%TX_SRS%')
    )
    
    ORDER BY
    TaskDate DESC
    ";

    $sbrt_query = mssql_query($sbrt_sql);

    // Create array to hold reable results of the query
    $sbrt_json = array();

    // Loop through rows in the result of the query
    $index = 0;
    while($row = mssql_fetch_array($sbrt_query)){
        $sbrt_json[$index] = $row;
        $index = $index + 1;
    }

    $sbrt_numrows = sizeof($sbrt_json); // holds number of entries (i.e. number of fields)

    $index = 0;
    while($index < $sbrt_numrows){
        $sbrt_json[$index]["TaskDate"] = DateTime::createFromFormat("Y-m-d",$sbrt_json[$index]["TaskDate"]);
        $index = $index + 1;
    }

    //------------------------------------------------------------------------------------
    // Loop variables:
    $index = 0; // index of the loop, will count through # of rows from query
    $f_count = 0; // count # of Fields in the current Treatment Plan
    $p_count = 0; // count # of Treatment Plans in the current Course
    $c_count = 0; // count # of Courses for the patient

    $coursedict = array(); // array to hold the desired output
    $plan_mods = array(); // array to hold the modalities of a given plan
    $plan_mods_pk = array(); // array to hold the pks of modalities of a given plan
    if ($numrows != 0) {
        $coursedict["FirstName"] = $json[0]["FirstName"];
        $coursedict["LastName"] = $json[0]["LastName"];
        $coursedict["DoseUnits"] = $json[0]["ConfigValue"];
    }
    $initial = TRUE; // indicates if on initial loop (could just check if index is zero instead)
    while($index < $numrows){
        // Provides a dictionary with numeric keys (indexing similar to array)
        // NOTE: THE SQL MUST HAVE ORDERED BY CLAUSE: ORDER BY COURSE THEN PLAN

        // Names of current course/plan/field:
        $c_id = $json[$index]["CourseId"];
        $p_id = $json[$index]["PlanSetupId"];
        $f_id = $json[$index]["RadiationId"];

        // Determine which counters need to reset (i.e. if on new course or plan)
        if (!$initial) {
            // Same course as previous entry:
            if ($c_id == $json[$index-1]["CourseId"]) {
                // New field only
                if ($p_id == $json[$index-1]["PlanSetupId"]) {
                    $f_count+=1;
                }
                // New Plan
                else {
                    // If plan is stereo, replace other types (can modify this, see commented portion)
                    $stereo_mods_joined = determineStereo($json[$index-1]["CreationDate"], $json[$index-1]["PrescribedDose"], $json[$index-1]["NoFractions"], $sbrt_json, $sbrt_numrows, $mods_vlabel, $mods_pk);
                    $stereo_mods = $stereo_mods_joined[0];
                    $stereo_mods_pk = $stereo_mods_joined[1];
                    if (sizeof($stereo_mods) > 0) {
                        $plan_mods = $stereo_mods;
                        $plan_mods_pk = $stereo_mods_pk;
                    }
                    // $plan_mods = array_merge($plan_mods,$stereo_mods);
                    $coursedict[$c_count][$p_count]["mods"] = array_values(array_unique($plan_mods));
                    $coursedict[$c_count][$p_count]["mods_pk"] = array_values(array_unique($plan_mods_pk));
                    
                    // reset modalities for new plan
                    $plan_mods = array();
                    $plan_mods_pk = array();
                    $p_count+=1;
                    $f_count=0;
                }
            }
            // New Course:
            else {
                // If plan is stereo, replace other types (can modify this, see commented portion)
                $stereo_mods_joined = determineStereo($json[$index-1]["CreationDate"], $json[$index-1]["PrescribedDose"], $json[$index-1]["NoFractions"], $sbrt_json, $sbrt_numrows, $mods_vlabel, $mods_pk);
                $stereo_mods = $stereo_mods_joined[0];
                $stereo_mods_pk = $stereo_mods_joined[1];
                if (sizeof($stereo_mods) > 0) {
                    $plan_mods = $stereo_mods;
                    $plan_mods_pk = $stereo_mods_pk;
                }
                // $plan_mods = array_merge($plan_mods,$stereo_mods);
                $coursedict[$c_count][$p_count]["mods"] = array_values(array_unique($plan_mods));
                $coursedict[$c_count][$p_count]["mods_pk"] = array_values(array_unique($plan_mods_pk));
                
                // reset modalities for new plan
                $plan_mods = array();
                $plan_mods_pk = array();
                $c_count+=1;
                $p_count=0;
                $f_count=0;
            }
        }
        else {
            $initial = FALSE;
        }

        // Assign desired values from DB into the dictionary. Dictionary may be
        // indexed similarly to an array.
        $coursedict[$c_count]["name"] = $json[$index]["CourseId"];
        $coursedict[$c_count][$p_count]["name"] = $json[$index]["PlanSetupId"];
        $coursedict[$c_count][$p_count]["intent"] = $json[$index]["Intent"];
        $coursedict[$c_count][$p_count]["cstatus"] = $json[$index]["ClinicalStatus"];
        $coursedict[$c_count][$p_count]["status"] = $json[$index]["Status"];
        $coursedict[$c_count][$p_count]["status_user"] = $json[$index]["StatusUserName"];
        $coursedict[$c_count][$p_count]["dose"] = $json[$index]["PrescribedDose"];
        $coursedict[$c_count][$p_count]["nofractions"] = $json[$index]["NoFractions"];

        $coursedict[$c_count][$p_count]["date"] = $json[$index]["CreationDate"];

        $coursedict[$c_count][$p_count][$f_count]["name"] = $f_id;

        // Determine the modalities for the current field (current plan), add to existing
        // plans if distinct from existing entries
        $new_mods_joined = determineModalities($json[$index], $mods_vlabel, $mods_pk);
        $new_mods = $new_mods_joined[0];
        $new_mods_pk = $new_mods_joined[1];
        $plan_mods = array_merge($plan_mods,$new_mods);
        $plan_mods_pk = array_merge($plan_mods_pk,$new_mods_pk);

        $index += 1;
        //For the last iteration, assign the modality array for the plan
        if ($index >= $numrows) {
            // If plan is stereo, replace other types (can modify this, see commented portion)
            $stereo_mods_joined = determineStereo($json[$index-1]["CreationDate"], $json[$index-1]["PrescribedDose"], $json[$index-1]["NoFractions"], $sbrt_json, $sbrt_numrows, $mods_vlabel, $mods_pk);
            $stereo_mods = $stereo_mods_joined[0];
            $stereo_mods_pk = $stereo_mods_joined[1];

            if (sizeof($stereo_mods) > 0) {
                $plan_mods = $stereo_mods;
                $plan_mods_pk = $stereo_mods_pk;
            }
            // $plan_mods = array_merge($plan_mods,$stereo_mods);
            $coursedict[$c_count][$p_count]["mods"] = array_values(array_unique($plan_mods));
            $coursedict[$c_count][$p_count]["mods_pk"] = array_values(array_unique($plan_mods_pk));
        }
    }

    // Returns the json-ified dictionary to the calling jquery function
    // print_r ($coursedict);
    echo json_encode($coursedict);

    /* Free statement and connection resources. */
    if (!$query) {
        die('Query failed.');
    }

    // Free the query result
    mssql_free_result($sbrt_query);





    function determineModalities($row, $mods_vlabel, $mods_pk) {
        /**
         *Determine the treatment modalities of the provided field 
         *
         *@param array $row -Query information for the current field
         *@param array $mods_vlabel -Verbose names of treatment modalities (dictionary)
         *@param array $mods_pk -Primary keys (SaILS) of treatment modalities (dictionary)
         *
         *@return 2D array -1st dimension contains verbose names of the modalities, 2nd
         * dimesion contains pks of the modalities
        */
        $row_mods = array();
        $row_mods_pk = array();
        // Brachytherapy
        if ($row["MachineId"] == 'Brachytherapy') {
            // Intracavitary
            if (stripos($row["RadiationId"],'vault') !== FALSE
                || stripos($row["RadiationId"],'cervi') !== FALSE
                || stripos($row["RadiationId"],'vagin') !== FALSE
            ) {
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_CAV"]);
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_HDR"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_CAV"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_HDR"]);
            }
            // Intraluminal
            elseif (stripos($row["RadiationId"],'esophag') !== FALSE
                || stripos($row["RadiationId"],'bronch') !== FALSE
            ) {
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_LUM"]);
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_HDR"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_LUM"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_HDR"]);
            }
            // Surface
            elseif (stripos($row["RadiationId"],'eye') !== FALSE) {
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_SUR"]);
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_LDR"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_SUR"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_LDR"]);
            }
            // Interstitial
            elseif (stripos($row["RadiationId"],'prostate') !== FALSE
                || stripos($row["RadiationId"],'tongue') !== FALSE
                || stripos($row["RadiationId"],'lung') !== FALSE
                || stripos($row["RadiationId"],'lip') !== FALSE
                || stripos($row["RadiationId"],'ent') !== FALSE
                || stripos($row["RadiationId"],'cheek') !== FALSE
            ) {
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_INT"]);
                array_push($row_mods, $mods_vlabel["MOD_BRACHY_HDR"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_INT"]);
                array_push($row_mods_pk, $mods_pk["MOD_BRACHY_HDR"]);
            }
            // Unknown Other
            else {
                array_push($row_mods, $mods_vlabel["MOD_OTHER"]);
                array_push($row_mods_pk, $mods_pk["MOD_OTHER"]);
            }
        }
        // Electrons
        elseif ($row["RadiationType"] == 'E') {
            // Total Skin Electron Irradiation
            if ($row["TechniqueId"] == 'HDTSE') {
                array_push($row_mods, $mods_vlabel["MOD_E_TSEI"]);
                array_push($row_mods_pk, $mods_pk["MOD_E_TSEI"]);
            }
            // EBRT Electrons
            else {
                array_push($row_mods, $mods_vlabel["MOD_E_EBRT"]);
                array_push($row_mods_pk, $mods_pk["MOD_E_EBRT"]);
            }
        }
        // Photons
        elseif ($row["RadiationType"] == 'X') {
            // TBI
            if (stripos($row["PlanSetupId"],'TBI_ARC') !== FALSE
                || stripos($row["PlanSetupId"],'TBI ARC') !== FALSE
            ) {
                array_push($row_mods, $mods_vlabel["MOD_X_TBI"]);
                array_push($row_mods_pk, $mods_pk["MOD_X_TBI"]);
            }
            // No MLC involvement
            elseif (is_null($row["MLCPlanType"])) {
                // Cones
                // if (stripos($row["AddOnName"],'cc') !== FALSE) {
                if ($row["TechniqueId"] == 'SRS ARC') {
                    // array_push($row_mods, $mods_vlabel[MOD_X_CONF_CONE]);
                    if ($row["NoFractions"] == 1) {
                        array_push($row_mods, $mods_vlabel["MOD_X_SRS"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_SRS"]);
                    }
                    else {
                        array_push($row_mods, $mods_vlabel["MOD_X_SBRT"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_SBRT"]);
                    }
                }
                // Simple
                else {
                    array_push($row_mods, $mods_vlabel["MOD_X_SIMPLE"]);
                    array_push($row_mods_pk, $mods_pk["MOD_X_SIMPLE"]);
                }
            }
            // Stationary MLC: 3D CRT
            elseif ($row["MLCPlanType"] == 'StdMLCPlan') {
                array_push($row_mods, $mods_vlabel["MOD_X_CONF"]);
                array_push($row_mods_pk, $mods_pk["MOD_X_CONF"]);
            }
            // Dynamic MLCs
            elseif ($row["MLCPlanType"] == 'DynMLCPlan') {
                // Arc Dyanmic: Moving MLC but not intensity modulation
                if ($row["IndexParameterType"] == 'Gantry') {
                    // array_push($row_mods, $mods_vlabel[MOD_X_CONF_ARC]);
                    if ($row["NoFractions"] == 1) {
                        array_push($row_mods, $mods_vlabel["MOD_X_SRS"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_SR"]);
                    }
                    else {
                        array_push($row_mods, $mods_vlabel["MOD_X_SBRT"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_SBRT"]);
                    }
                }
                // Other plans involving MLC
                if ($row["IndexParameterType"] == 'MU') {
                    // Series of MLC patterns (stationary while beam on) - Step and Shoot "IMRT"
                    if ($row["NumControlPoints"] < MAX_CP_STEP_SHOOT) {
                        array_push($row_mods, $mods_vlabel["MOD_X_STEP_SHOOT"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_STEP_SHOOT"]);
                    }
                    // Moving MLCs, stationary gantry (inversely planned IMRT)
                    else {
                        array_push($row_mods, $mods_vlabel["MOD_X_IMRT"]);
                        array_push($row_mods_pk, $mods_pk["MOD_X_IMRT"]);
                    }
                }
                // Arc: Moving MLCs, moving gantry
                if ($row["IndexParameterType"] == 'IMRTGantry') {
                    array_push($row_mods, $mods_vlabel["MOD_X_ARC"]);
                    array_push($row_mods_pk, $mods_pk["MOD_X_ARC"]);
                }
            }
            else {
                array_push($row_mods, $mods_vlabel["MOD_OTHER"]);
                array_push($row_mods_pk, $mods_pk["MOD_OTHER"]);
            }
        }
        else {
            array_push($row_mods, $mods_vlabel["MOD_OTHER"]);
            array_push($row_mods_pk, $mods_pk["MOD_OTHER"]);
        }

        return array($row_mods,$row_mods_pk);
    }

    function determineStereo($plan_date, $dpf, $nofracts, $sbrt_json, $sbrt_numrows, $mods_vlabel, $mods_pk) {
        /**
         *Determine if the treatment plan is either SBRT or SRS
         *
         *@param string $plan_date -String representing date plan was created [Y-m-d]
         *@param string $dpf -Dose per fraction
         *@param string $nofracts -Number of fractions
         *@param array $sbrt_json -Query results of activities for the patient
         *@param int $sbrt_numrows -Number of activites for the patient
         *@param array $mods_vlabel -Verbose names of treatment modalities (dictionary)
         *@param array $mods_pk -Primary keys (SaILS) of treatment modalities (dictionary)
         *
         *@return 2D array -1st dimension contains verbose names of the modalities, 2nd
         * dimesion contains pks of the modalities
        */
        $row_mods = array();
        $row_mods_pk = array();
        if ($sbrt_numrows >0) {
            $ind = 0;
            $plan_date = DateTime::createFromFormat("Y-m-d",$plan_date);
            while($ind < $sbrt_numrows){
                $diff = date_diff($plan_date,$sbrt_json[$ind]["TaskDate"]);
                $diff_days = $diff->days;

                // Only proceed if the task date is within date range of a treatment plan
                if ($diff_days <= DAYS_CUTOFF_STEREO) {
                    // SBRT
                    if (stripos($sbrt_json[$ind]["ActivityCode"],'TX_FSRT') !== FALSE) {
                        if (floatval($dpf) >= MIN_SBRT_DPF) {
                            array_push($row_mods, $mods_vlabel["MOD_X_SBRT"]);
                            array_push($row_mods_pk, $mods_pk["MOD_X_SBRT"]);
                        }
                    }
                    // SRS
                    elseif (stripos($sbrt_json[$ind]["ActivityCode"],'TX_SRS') !== FALSE) {
                        if (floatval($dpf) >= MIN_SRS_DPF) {
                            array_push($row_mods, $mods_vlabel["MOD_X_SRS"]);
                            array_push($row_mods_pk, $mods_pk["MOD_X_SRS"]);
                        }
                    }
                }

                $ind = $ind + 1;
            }
        }
        $ii = 0;
        $mylen = sizeof($row_mods);
        while ($ii < $mylen) {
            $ii = $ii + 1;
        }
        return array($row_mods,$row_mods_pk);
    }
?>