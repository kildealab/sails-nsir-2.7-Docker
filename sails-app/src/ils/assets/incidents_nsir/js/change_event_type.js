"use strict";

var all_popovers = $(".ils-popover");

$(document).ready(function(){
    // The following is required to allow for an HTTPResponseRedirect following a successful
    // AJAX post.
    // $(document).ajaxComplete(function(e, xhr, settings) {
    //     if (xhr.status == 278) {
    //         window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
    //     }
    // });

    $('select').chosen({search_contains:true, width:'100%'});

    //------------------------------------------------------------------------------------
    // Function called upon attempted submission of the form. Make an ajax post
    // which applies any errors, or if successfuly, redirects back to the investigation page
    //------------------------------------------------------------------------------------
    $("#change-event-type-form").submit(function(){
        $.ajax({
            url: "/nsir/change-event-type/" + thisInc + "/",
            method:"POST",
            data: $("#change-event-type-form").serialize(),
            success: function(data, textStatus, jqXHR){
                if (data.errors) {
                    applyErrors(data.errors);
                }
                else {
                    window.location.href = jqXHR.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
                }
            },
            // The following will trigger if uncaught error (Not form field errors)
            error: function(msg){
                var ERROR_MESSAGE = "There was a problem submitting your change, please contact the system administrator.";
                var alertType = "alert-error";
                ariaMessage(alertType, ERROR_MESSAGE);
            }
        });
        return false;
    });

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
    // Display an ajax message to the user which indicates whether or not an action was
    // successful
    //
    // @param {string} alertType - a string representing additinal classes which should
    // be added to the ajax message (effectively to color the message differently if
    // displaying success vs. warning vs. error)
    //
    // @param {string} messageText - a string containing the message to be displayed.
    //------------------------------------------------------------------------------------
    function ariaMessage(alertType, messageText, duration) {
        var duration = typeof duration !== 'undefined' ?  duration : 10000;
        // $(".ajax_messages").html("");
        $("#floating-status-message").remove();
        // $(".ajax_messages").append("<div class='message-div alert " + alertType + " style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        // $(".alert").slideDown();

        var $message = $("<div id='floating-status-message' class='floating-message-div alert " + alertType + " style='width:100%'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        $('.navbar').append($message);
         setTimeout(function() {
             $message.remove();
         }, duration)
    }

    $("#change-event-type-form").submit(function(){
        $(window).unbind("beforeunload");
    });

    //------------------------------------------------------------------------------------
    // Handle the popover (tooltip) behaviour
    //------------------------------------------------------------------------------------

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

    //====================================================================================
    // Listeners to adapt which form fields are visible, and what values they hold based
    // on what is entered in other form fields. 
    //====================================================================================
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

});