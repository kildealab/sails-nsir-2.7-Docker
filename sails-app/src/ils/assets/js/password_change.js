"use strict";

//----------------------------------------------------------------------------------------
// Function called upon page load
//----------------------------------------------------------------------------------------
$(document).ready(function(){
    //------------------------------------------------------------------------------------
    // Function called upon attempted submission of the report form. Make an ajax post
    // which applies any errors, or apply sucess highlighting/messages.
    //------------------------------------------------------------------------------------
    $("#form-change-password").submit(function(){
        $.ajax({
            url: "/password_change/",
            method:"POST",
            data: $("#form-change-password").serialize(),
            success: function(errors){
                if (errors) {
                    applyErrors(errors);
                }
                else {
                    window.location='/password_change/done/';
                }
            },
            // The following will trigger if uncaught error (Not form field errors)
            error: function(msg){
                console.log("error!");
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
        // $("#ajax_messages").html("");

        if (errors) {
            // $(".success").removeClass("success");

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
                    // if ($control.selector == "#id_new_password1"){
                    //     $($control).parent().addClass("error");
                    //     $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                    //     $newDiv.insertAfter(".submit-report").slideDown('fast');
                    // } 
                    // // Group error for username & password together, so no message here
                    // else if ($control.selector == "#id_new_password2") {
                    // }
                    // else {
                    $($control).parent().parent().addClass("error");
                    $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                    if (($control).next().hasClass("chosen-container")) {
                        $control.next().addClass("chosen-error");
                        $newDiv.insertAfter($control.next()).slideDown('fast');
                    }
                    else {
                        $newDiv.insertAfter($control).slideDown('fast');
                    }
                    // }
                }
                // If there was previously an error message, and there still is an error,
                // the message should persist; so remove the 'remove-msg' class 
                else {
                    $($errorMsg).text(message).removeClass("remove-msg");
                }
            });
            // removeMessages();
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
});