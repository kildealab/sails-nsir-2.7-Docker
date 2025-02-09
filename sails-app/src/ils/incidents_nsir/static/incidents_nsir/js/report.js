"use strict";

var all_popovers = $(".ils-popover");

//----------------------------------------------------------------------------------------
// Function called upon page load
//----------------------------------------------------------------------------------------
$(document).ready(function(){
    $('select').chosen({search_contains:true, width:'80%'});
    //------------------------------------------------------------------------------------
    // Function called upon attempted submission of the report form. Make an ajax post
    // which applies any errors, or apply sucess highlighting/messages.
    //------------------------------------------------------------------------------------
    $("#report-form").submit(function(){
        
        disableButtons('.submit-report','Please Wait');

        $.ajax({
            url: "/nsir/report/",
            method:"POST",
            data: $("#report-form").serialize(),
            success: function(mydata){
                applyErrors(mydata.errors);
                applySuccess(mydata.changed,mydata.incident_id);
                enableButtons('.submit-report','Submit');
            },
            // The following will trigger if uncaught error (Not form field errors)
            error: function(msg){
                $("#ajax-text").html("error!");
                enableButtons('.submit-report','Submit');
            }
        });
        return false;
    });

    $("#report-form").submit(function(){
        $(window).unbind("beforeunload");
    });

    //------------------------------------------------------------------------------------
    // Disable buttons (e.g. to prevent mulitple form submits)
    //
    // @param {string} element_string - A string representing a class or id that
    // corresponds to the button elements to be disabled. (e.g. '#my_button').
    // @param {string} button_text - The text to be displayed on the button while
    // disabled. (e.g. 'Please wait').
    //------------------------------------------------------------------------------------
    function disableButtons(element_string,button_text) {
        $(element_string).attr('disabled','disabled');
        $(element_string).text(button_text);
    }

    //------------------------------------------------------------------------------------
    // Enable buttons
    //
    // @param {string} element_string - A string representing a class or id that
    // corresponds to the button elements to be enabled. (e.g. '#my_button').
    // @param {string} button_text - The text to be displayed on the button while
    // disabled. (e.g. Please wait).
    //------------------------------------------------------------------------------------
    function enableButtons(element_string,button_text) {
        $(element_string).removeAttr('disabled');
        $(element_string).text(button_text);
    }

    //------------------------------------------------------------------------------------
    // Apply error highlighting and messages to applicable fields.
    //
    // @param {dictionary} errors - dictionary of arrays, with keys corresponding to the
    // form field names. The arrays contain the errors associated with that field, and
    // typically contain only one single element. This element is a string which describes
    // the error to be displayed to the user.
    //------------------------------------------------------------------------------------
    function applyErrors(errors) {
        $(".error-msg").addClass("remove-msg"); // Add class to remove error message to existing error messages
        $("#ajax_messages").html("");

        if (errors) {
            $(".success").removeClass("success");

            // Loop through errors and apply them to appropriate field Add error class to
            // some parent div of the field (typically that div is named like 'hide-
            // id_field_name'). That div contains both the label and the field itself, so
            // error (red) highlighting is applied to both. Also handle application of
            // error messages below the appropriate fields.
            $.each(errors, function (field, message) {
                var $errorMsg = $("#error-field-" + field);
                // If there was previously no error message do the following:
                // (Note that $newDiv holds the error message. Insert below that field)
                if ($errorMsg.length == 0) {
                    var $newDiv;
                    var $control = $("#id_" + field);
                    if ($control.selector == "#id_auth_password"){
                        $($control).parent().addClass("error");
                        $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                        $newDiv.insertAfter(".submit-report").slideDown('fast');
                    } 
                    // Group error for username & password together, so no message here
                    else if ($control.selector == "#id_submitted_by") {
                    }
                    else {
                        $($control).parent().parent().addClass("error");
                        $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                        if (($control).next().hasClass("chosen-container")) {
                            $control.next().addClass("chosen-error");
                            $newDiv.insertAfter($control.next()).slideDown('fast');
                        }
                        else {
                            $newDiv.insertAfter($control).slideDown('fast');
                        }
                    }
                }
                // If there was previously an error message, and there still is an error,
                // the message should persist; so remove the 'remove-msg' class 
                else {
                    $($errorMsg).text(message).removeClass("remove-msg");
                }
            });
            removeMessages();
        }

        // Remove errors from previously errored fields, which have now been ameliorated.
        // I.e. remove the message, and remove error highlighting.
        $.each($(".remove-msg"), function() {
            $(this).slideUp('fast', function() {
                $(this).parent().removeClass("error");
                $(this).parent().parent().removeClass("error");
                $(this).prev().removeClass("chosen-error");
                $(this).remove();
            });
        });
    }

    //------------------------------------------------------------------------------------
    // Apply success highlighting and messages to applicable fields.
    //
    // @param {array} changed - Array of form fields (e.g event_type) whose inputted
    // values differ from the initial values which were specified. Thus, those fields
    // whose values were specified in form initialization, are not included.
    // @param {number} incident_id - ID number of the incident.
    //------------------------------------------------------------------------------------
    function applySuccess(changed,incident_id) {
        // remove previous success fields
        $(".success").removeClass("success");

        // Apply successes (i holds 0, m holds changed field name, e.g incident_description)
        // Adds success class to the hide-id_field_name div, for highlighting in green
        if (changed) {
            $.each(changed, function (i, m) {
                if (m == "submitted_by" || m == "auth_password") {
                    $("#id_" + m).parent().addClass("success");
                }
                else if (m != "complete") {
                    $("#id_" + m).parent().parent().addClass("success");
                }
            });

            // Need to explicitly add success class to those fields which were specified
            // upon the initial loading of the page (the 'changed' variable will not
            // include these fields)
            $("#hide-id_report_type").addClass("success");
            $("#hide-id_date_incident_detected").addClass("success");
            $("#hide-id_investigator").addClass("success");

            $("#id_auth_password").val(null); // prevent repeat online incident submissions
            updateMessages(incident_id);
        }
    }

    //------------------------------------------------------------------------------------
    // Update AJAX message divs at top and bottom of the page.
    //
    // @param {number} incident_id - ID number of the incident.
    //------------------------------------------------------------------------------------
    function updateMessages(incident_id) {
        $(".ajax_messages").html("");
        if (incident_id) {
            $(".ajax_messages").append("<div class='message-div alert alert-success style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + "Incident " + incident_id + " Successfully Submitted! Please note this ID number in order to follow-up during the investigation." + "</strong></div>");
            $(".alert").slideDown();
        }
    }

    //------------------------------------------------------------------------------------
    // Remove AJAX messages at top and bottom of the page.
    //------------------------------------------------------------------------------------
    function removeMessages() {
        $(".ajax_messages").html("");
    }

    //====================================================================================
    // Various settings, etc
    //====================================================================================
    // To enable page navigation confirmations, uncomment the following:
    // $('form').areYouSure(
    //     {'message':'You have not yet submitted your incident!'}
    // );

    $('.ils-popover').popover({
           trigger:'manual',
           animation:false,
           delay:0,
           html:true
    });

    // Show tooltips when clicking on fields
    $("input, select, textarea").on('focus',function(){
        $(".ils-popover").popover('hide');
        $(this).parents(".ils-popover").popover("show");
    });

    // Hide tooltips when click elsewhere on the page
    $("input, select, textarea").on('blur', function(){
        $(".ils-popover").popover('hide');
    });

    $(".datepicker").datepicker({
        format: 'yyyy-mm-dd',
    });

    $("label.checkbox").click(function(){
       $(this).find("input").focus();
    });

    //====================================================================================
    // Listeners to adapt which form fields are visible, and what values they hold based
    // on what is entered in other form fields. 
    //====================================================================================
    // For online reports, hide the Reported To field:
    if($("#id_reported_to").attr('type') == 'hidden'){
        $("#hide-id_reported_to").slideUp();
    }

    // Don't allow entering of ID if online-only report (is assigned automatically)
    $("#id_report_type").change(function(){
        var report_type_key = $("#id_report_type").find("option:selected").val();
        if (report_type_key == 1){
            $("#hide-id_reported_to").slideDown();
            $("#hide-id_incident_id").slideDown(); 
            // $("#id_incident_id").val(null); 
        }
        else if (report_type_key == 2){
            $("#hide-id_reported_to").slideUp();
            $("#id_reported_to").val(null);
            $("#hide-id_incident_id").slideUp(); 
            $("#id_incident_id").val(null);
        }
    }).trigger('change');

    // Hide/Show set of fields for reportable circumstance vs. near-miss/actual incident
    $("#id_event_type").change(function(){
        var event_type = $("#id_event_type").find("option:selected").val();

        if (event_type == 2 || event_type == 3){
            $("#hide-id_number_patients_involved").slideDown();
            $("#id_number_patients_involved").val(1)
            $("#hide-id_oncologist").slideDown();
            $("#hide-id_diagnosis").slideDown();
            $("#hide-id_patient_id").slideDown();
            // $("#hide-id_treatment_site").slideDown();
            $("#hide-id_body_region_treated").slideDown();
            $("#hide-id_patient_support_required").slideDown();
        }
        else {
            $("#hide-id_number_patients_involved").slideUp();
            $("#id_number_patients_involved").val(null);

            $("#hide-id_oncologist").slideUp();
            $("#hide-id_diagnosis").slideUp();
            $("#hide-id_patient_id").slideUp();
            // $("#hide-id_treatment_site").slideUp();
            $("#hide-id_body_region_treated").slideUp();
            $("#id_oncologist").val(null);
            $("#id_diagnosis").val(null);
            $("#id_patient_id").val(null);
            // $("#id_treatment_site").val(null);
            $("#id_body_region_treated").val(null);
            $("#hide-id_patient_support_required").slideUp();
            $("#id_patient_support_required").val(null);
        }
        $('select').trigger("chosen:updated");
    }).trigger('change');

    $("#id_number_patients_involved").change(function(){
        var number_patients_involved = $("#id_number_patients_involved").val();

        if (number_patients_involved == 1) {
            $("#hide-id_oncologist").slideDown();
            $("#hide-id_diagnosis").slideDown();
            $("#hide-id_patient_id").slideDown();
            // $("#hide-id_treatment_site").slideDown();
            $("#hide-id_body_region_treated").slideDown();
        }
        else {
            $("#hide-id_oncologist").slideUp();
            $("#hide-id_diagnosis").slideUp();
            $("#hide-id_patient_id").slideUp();
            // $("#hide-id_treatment_site").slideUp();
            $("#hide-id_body_region_treated").slideUp();
            $("#id_oncologist").val(null);
            $("#id_diagnosis").val(null);
            $("#id_patient_id").val(null);
            // $("#id_treatment_site").val(null);
            $("#id_body_region_treated").val(null);
        }
        $('select').trigger("chosen:updated");
    }).trigger('change');

    // Show/hide additional staff/patient support fields if support is required/given
    $("#id_support_required").change(function(){
        var support_required_key = $("#id_support_required").find("option:selected").val();
        if (support_required_key == 1){
            $("#hide-id_support_given").slideDown();
            $("#hide-id_support_description").slideDown();
        }
        else {
            $("#hide-id_support_given").slideUp();
            $("#hide-id_support_description").slideUp();
            $("#id_support_given").val(null);
            $("#id_support_description").val(null);
        }
        $('select').trigger("chosen:updated");
    }).trigger('change');

    // $("#id_support_given").change(function(){
    //     var support_required_key = $("#id_support_given").find("option:selected").val();
    //     if (support_required_key == 1){
    //         $("#hide-id_support_description").slideDown();
    //     }
    //     else {
    //         $("#hide-id_support_description").slideUp();
    //         $("#id_support_description").val(null);
    //     }
    //     $('select').trigger("chosen:updated");
    // }).trigger('change');

    $("#id_patient_support_required").change(function(){
        var patient_support_required_key = $("#id_patient_support_required").find("option:selected").val();
        if (patient_support_required_key == 1){
            $("#hide-id_patient_support_given").slideDown();
            $("#hide-id_patient_support_description").slideDown();
        }
        else {
            $("#hide-id_patient_support_given").slideUp();
            $("#hide-id_patient_support_description").slideUp();
            $("#id_patient_support_given").val(null);
            $("#id_patient_support_description").val(null);
        }
        $('select').trigger("chosen:updated");
    }).trigger('change');

    // $("#id_patient_support_given").change(function(){
    //     var patient_support_required_key = $("#id_patient_support_given").find("option:selected").val();
    //     if (patient_support_required_key == 1){
    //         $("#hide-id_patient_support_description").slideDown();
    //     }
    //     else {
    //         $("#hide-id_patient_support_description").slideUp();
    //         $("#id_patient_support_description").val(null);
    //     }
    //     $('select').trigger("chosen:updated");
    // }).trigger('change');

    //Toggle for making investigator field readonly
    // $("#id_investigator").mousedown(function(event){
    //     $("#id_investigator").children().hide();
    // });

    // $(window).bind("beforeunload", function (e) {
    //     var form_inputs = $("#report-form").find("input, select, textarea").not("[type=hidden]").not(".select2-focusser, #id_incident_occurred_date, #id_email, #id_submitted_by, #id_auth_password");

    //     // if (_.any(_.pluck(form_inputs,"value"))){
    //     //     var e = e || window.event;

    //     //     if (e) {
    //     //         e.returnValue = '';
    //     //     }

    //     //     return 'Are you sure you want to leave this page without submitting your incident?';
    //     // }
    // });
});
