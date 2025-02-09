"use strict";

// Seems to be unused:
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.indexOf(str) === 0;
  };
}

var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

//----------------------------------------------------------------------------------------
// Function called upon page load
//----------------------------------------------------------------------------------------
$(document).ready(function(){

    // Arrays that will store the various parameters associated with locally
    // required fields
    var local_depend_ids = []; // fields upon which locally required fields are dependent (e.g. local_severity_level)
    var local_thresholds = []; // Threshold values as PKs above which locally required field is mandatory
    var local_req_ids = []; // fields that are locally mandatory when above threshold value is exceeded (e.g. hospital_form_id)
    var local_messages = []; // message to be displayed to user if threshold is exceeded.
    for (var i=0;i<local_mandatory_dicts.length;i++) {
        local_depend_ids.push("#id_"+local_mandatory_dicts[i].dependent_field);
        local_thresholds.push(local_mandatory_dicts[i].threshold);
        local_req_ids.push("#id_"+local_mandatory_dicts[i].field);
        local_messages.push(local_mandatory_dicts[i].message);
    }

    $('select:not(.blocked-field, .reported-field)').chosen({search_contains:true, width:'100%'});

    //====================================================================================
    // Initialization behaviours
    //====================================================================================
    // Anonymize reported by and reported to fields if anonymous
    if (ANONYMOUS_DISPLAY) {
        $("#id_reported_by").slideUp();
        $("#id_reported_to").slideUp();
    }

    // Toggle whether or not id_discussion is displayed upon initial page load,
    // depending on whether or not the investigation is flagged for discussion.
    if ($("#id_discussion").prop('checked')) {
        $("#hide-id_discussion").slideDown();
    }
    else if ($("#id_flag").prop('checked')) {
        $("#hide-id_discussion").slideDown();
    }
    else {
        $("#hide-id_discussion").slideUp();
    }  

    // If using checkboxes to save template fields:
    // $(".test-btn").click(function(){
    //     $(".editable-field").each(function(){
    //         console.log($(this).attr('id'));
    //         var checkbox = document.createElement('input');
    //         checkbox.type = "checkbox";
    //         // checkbox.name = "name";
    //         checkbox.value = "value";
    //         checkbox.id = $(this).attr('id') + "_checkbox";
    //         $("label[for='"+$(this).attr('id')+"']").prepend(checkbox);
    //         $("#"+checkbox.id).addClass('template_checkbox');
    //     });
    // });

    //------------------------------------------------------------------------------------
    // Clicking the "Apply Template" button will scroll the user to the fieldset where
    // templates may be applied. The field used to apply templates will be highlighted
    // for a few seconds to notify the user.
    //------------------------------------------------------------------------------------
    $('.apply-template').click(function() {
        $('html, body').animate({
            scrollTop: $("#investigator-head").offset().top
        }, 200);
        var elem = $( "#hide-id_predefined_type" );
        // var elem_single = elem.find(".chosen-single");
        elem.animate({
                  color: "#00a3cc",
                }, 1000 );
        // elem_single.animate({
        //           border: "1px solid #00a3cc",
        //         }, 1000 );
        setTimeout(function(){elem.animate({ color: "#333"}, 1000)},5000);
        // setTimeout(function(){elem_single.animate({ border: "1px solid #aaa"}, 1000)},5000);
    });

    //------------------------------------------------------------------------------------
    // When changing the type of template for the current investigation, this function
    // is called, which then calls an AJAX POST method
    //------------------------------------------------------------------------------------
    $(document).on('change','#id_predefined_type', function() {
        var event_type = $("#id_event_type").find("option:selected").text();
        var selected_type = $(this).find("option:selected").text();
        get_field_values(selected_type, event_type);
    });

    //------------------------------------------------------------------------------------
    // Function used to retrieve predefined incident field-value pairs which should be
    // populated based on the currently selected template, and handle communicating the
    // success/failure of this retrieval to the user. All fields in the list of template
    // fields have their values removed, then the new values (including newly blank values)
    // are inserted.
    //
    // @param {string} selected_type - String representing the verbose name of the selected
    //      choice for predefined (template) type
    // @param {string} event_type - String representing the verbose name of the event type
    //      of the current incident
    //------------------------------------------------------------------------------------
    function get_field_values(selected_type, event_type) {
        $.ajax({
            type: 'POST',
            url: $("#get_field_values_view").text(),
            dataType: 'json',
            data: { selected_type: selected_type, event_type: event_type },
            success: function(json_data){
                // If no field-value pairs were obtained:
                if (json_data.empty) {
                    if (json_data.error_message) {
                        var message = json_data.error_message;
                        var alertType = "alert-error";
                        ariaMessage(alertType, message);
                    }
                }
                else {
                    // Remove existing field messages & highlighting
                    $(".template-msg").remove();
                    $(".control-group").removeClass("success"); // Remove success highlighting from hide-id divs
                    $(".fill-fill").removeClass("fill-fill");
                    $(".unfill-fill").removeClass("unfill-fill");
                    $(".fill-unfill").removeClass("fill-unfill");

                    unfill_fields(json_data.template_fields, json_data.required_fields);
                    fill_fields(json_data.fields);
                    apply_field_messages();
                    var alertType = "alert-success";
                    var message = "Template successfully applied. Review the highlighted changes, then click an 'Update' button to save.";
                    ariaMessage(alertType, message, 10000);

                    // var filled = fill_fields(json_data.fields);
                    // if (filled.length > 0) {
                    //     var alertType = "";
                    //     var message = "";
                    //     if (filled.length == 1)
                    //         message += "Fields that were successfully populated are highlighted in blue. Please review changes then click 'Update' to save. Note the following field was overridden: ";
                    //     else
                    //         message += "Fields that were successfully populated are highlighted in blue. Please review changes then click 'Update' to save. Note the following fields were overridden: ";
                    //     for (var i=0; i<filled.length; i++) {
                    //         message += filled[i] + ", ";
                    //     }
                    //     ariaMessage(alertType, message.slice(0, -2));
                    // }
                    // else {
                        // var alertType = "alert-success";
                        // var message = "Fields that were successfully populated are highlighted in blue. Please review changes then click 'Update' to save.";
                        // ariaMessage(alertType, message);
                    // }
                }
            },
            error: function(e){
                var alertType = "error";
                var ERROR_MESSAGE = "Problem retrieving the template. Please contact the system administrator.";
                ariaMessage(alertType, ERROR_MESSAGE);
            }
        });
    }

    //------------------------------------------------------------------------------------
    // Deselect all previously selected options from all fields included in templates.
    // Apply appropriate class for highlighting
    //
    // @param {array} template_fields - Array of field ids that are affected by choice of
    //      template (common to all templates).
    // @param {array} required_fields - Array of field names that are required in order
    //      to complete the investigation.
    //------------------------------------------------------------------------------------
    function unfill_fields(template_fields, required_fields) {
        for (var i=0;i<template_fields.length;i++) {
            var field_id = template_fields[i]; //e.g. "#id_acute_medical_harm"
            var $field_el = $(field_id);
            var field_val = $field_el.val();

            // Do the following if the field has a value:
            // Two empty checks required for FK (null) and M2M ("")
            if (field_val != null && field_val != "") {
                $(field_id+" option:selected").removeAttr("selected");
                // If the field is required, highlight label in orange
                if (required_fields.indexOf(field_id) > -1) {
                    $("label[for='"+$field_el.attr('id')+"']").addClass("missing");
                }
                $("label[for='"+$field_el.attr('id')+"']").addClass("fill-unfill");
                $field_el.addClass("fill-unfill");
                $field_el.next().addClass("fill-unfill");
            }
            $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
        }
    }

    //------------------------------------------------------------------------------------
    // Select all field options indicated in a provided list of form-value pairs. Apply
    // appropriate classes for highlighting.
    //
    // @param {array} fields - Array of dictionaries, each containing a single field-value
    //      pair.
    //------------------------------------------------------------------------------------
    function fill_fields(fields) {
        for (var i=0;i<fields.length;i++) {
            var field_id = fields[i].field; //e.g. "#id_acute_medical_harm"
            var $field_el = $(field_id);
            var field_val = $field_el.val();

            // Select new value
            $(field_id+ " option").filter(function() {
                //may want to use $.trim in here
                // Need to get rid of leading -'s because of tree type fields
                // return $(this).text().replace(/^-+/,"") == fields[i].field_value;
                return $(this).val() == fields[i].field_value 
            }).prop('selected', true);

            // Apply filled highlighting
            $(field_id.replace("#","#hide-")).removeClass("success");
            if ($field_el.hasClass("fill-unfill")){
                $("label[for='"+$field_el.attr('id')+"']").removeClass("fill-unfill");
                $field_el.removeClass("fill-unfill");
                $field_el.next().removeClass("fill-unfill");
                $("label[for='"+$field_el.attr('id')+"']").addClass("fill-fill");
                $field_el.addClass("fill-fill");
                $field_el.next().addClass("fill-fill");
            }
            else if(!$field_el.hasClass("fill-fill")){
                $("label[for='"+$field_el.attr('id')+"']").addClass("unfill-fill");
                $field_el.addClass("unfill-fill");
                $field_el.next().addClass("unfill-fill");
            }
        }
        $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
    }

    //------------------------------------------------------------------------------------
    // Provide appropriate message for each field affected by the change in template type,
    // according to the "fill" class applied to the field. These messages are displayed
    // under each corresponding field.
    //------------------------------------------------------------------------------------
    function apply_field_messages() {
        var FILL_UNFILL_MSG = "Previous field value erased by template";
        var FILL_FILL_MSG = "Previous field value replaced with template value";
        var UNFILL_FILL_MSG = "Field successfully filled with template value";

        $( "select.fill-fill" ).each(function( index ) {
            var $newMsg = $("<div id='template-msg-"+$(this).attr('id')+"' class='fill-fill help-block template-msg'>" + FILL_FILL_MSG + "</div>");   
            $newMsg.insertAfter($(this).next()).slideDown('fast');
        });
        $( "select.fill-unfill" ).each(function( index ) {
            var $newMsg = $("<div id='template-msg-"+$(this).attr('id')+"' class='fill-unfill help-block template-msg'>" + FILL_UNFILL_MSG + "</div>");   
            $newMsg.insertAfter($(this).next()).slideDown('fast');
        });
        $( "select.unfill-fill" ).each(function( index ) {
            var $newMsg = $("<div id='template-msg-"+$(this).attr('id')+"' class='unfill-fill help-block template-msg'>" + UNFILL_FILL_MSG + "</div>");   
            $newMsg.insertAfter($(this).next()).slideDown('fast');
        });
    }

    // Old approach to filling form fields:
    // function fill_fields(fields) {
    //     var filled = []
    //     var prev_field_id = "" // Used for multi-select elements
    //     for (var i=0;i<fields.length;i++) {
    //         var field_id = fields[i].field;
    //         var $field_el = $(field_id);
    //         var field_val = $field_el.val();

    //         // If the field was previously filled, empty and add field to list (to be
    //         // displayed to user)
    //         if (field_val != null && field_val != "" && field_id != prev_field_id) {
    //             filled.push($.trim($("label[for='"+$field_el.attr('id')+"']").text()));                
    //             $(field_id+" option:selected").removeAttr("selected");
    //         }

    //         // Select new value
    //         $(field_id+ " option").filter(function() {
    //             //may want to use $.trim in here
    //             // Need to get rid of leading -'s because of tree type fields
    //             return $(this).text().replace(/^-+/,"") == fields[i].field_value; 
    //         }).prop('selected', true);

    //         // Apply filled highlighting
    //         $(field_id.replace("#","#hide-")).removeClass("success");
    //         $("label[for='"+$field_el.attr('id')+"']").addClass("filled");
    //         $field_el.addClass("filled");


    //         prev_field_id = field_id;
    //     }
    //     return filled
    // }

    
    //------------------------------------------------------------------------------------
    // The following function is performed when the user clicks the button to initiate
    // upload of a new image. Display the incidentimage creation form to the user.
    //------------------------------------------------------------------------------------
    $(".add-image").click(function(){
        $("#upload-image-div").toggle();
        $(".save-template").toggle();
        $(".mark-invalid").toggle();

        if ($("#upload-image-div").is(':visible')) {
            // $(".update-investigation").hide();
            $(this).html("Cancel Image Upload");
            $(".update-investigation").hide();

        }
        else {
            // $(".update-investigation").show();
            $(this).html("Add New Image");
            $(".update-investigation").show();

        }
    });        

    //------------------------------------------------------------------------------------
    // Function called when an image being uploaded to the incident is changed (or removed)
    // Used to toggle display of a thumbmail of the image.
    //------------------------------------------------------------------------------------
    $("#id_image").change(function(){
        readURL(this);
        if (this.files.length > 0) {
        }
        else {
            $('#upload-thumbnail').attr('src', '');
        }
    });

    // subfunction called by previous to read the URL of the image to be uploaded so that
    // a thumbnail may be displayed
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#upload-thumbnail').attr('src', e.target.result);
            }

            reader.readAsDataURL(input.files[0]);
        }
    }

    //------------------------------------------------------------------------------------
    // This function is called when the user clicks the button to confirm saving a new
    // template. POST the "templatable" field-value pairs to the backend for processing
    // and (error checking and saving of the new template type). Receive the new errors
    // or successful data. Display message to the user accordingly. If successful, add
    // the newly created template to the Investigation template type field.
    //------------------------------------------------------------------------------------
    $(".confirm-image").click(function(){
        var data = new FormData($('#incidentimage-form')[0]);
        disableButtons('.confirm-image','Please Wait');

        $.ajax({
            type: 'POST',
            url: $("#save_new_image_view").text(),
            dataType: 'json',
            // Pass the serialized template form & field-value pairs to the backend. Passing
            // in stringified URL notation: best way to parse the two types of data on the
            // backend:
            data: data,
            processData: false,
            contentType: false,
            // data: { post_data: JSON.stringify(field_array), form_data: JSON.stringify($('#template-form').serializeArray()) },
            success: function(json_data){
                if (json_data.errors) {
                    applyErrors(json_data.errors);
                }
                else {
                    applyErrors(json_data.errors);
                    $(".add-image").trigger("click");
                    $('#incidentimage-form').trigger("reset");
                    $("#id_image").trigger("change");
                    displayNewImage(json_data);
                    $("#no-images-div").hide();
                    var SUCCESS_MESSAGE = "New image successfully uploaded";
                    validMessage(SUCCESS_MESSAGE);
                }
                enableButtons('.confirm-image','Upload Image');
            },
            // If there is an unforseen problem posting the data:
            error: function(e) {
                var alertType = "error";
                var ERROR_MESSAGE = "There was a problem uploading the image. Please contact the system administrator.";
                ariaMessage(alertType, ERROR_MESSAGE);
                enableButtons('.confirm-image','Upload Image');
            }
        });
        return false;
    });

    //------------------------------------------------------------------------------------
    // Create a new div to display an image that was just added by a user, including
    // caption information.
    //
    // @param {dictionary} json_data - Dictionary passed by the view
    // Relevant keys:
    //  image_location - Relative path (and URL) of the image file location
    //  image_name - verbose name of the image (as specified by the uploader)
    //  image_uploaded_by - string name of the user who uploaded the image
    //  image_date - string representing datetime the image was uploaded
    //------------------------------------------------------------------------------------
    function displayNewImage(json_data) {
        if ($(".uploaded-images").last().children().length % 3 == 0) {
            $("#uploaded-images-panel").append("</div><div class='row-fluid uploaded-images'>");
        }
        var new_image_html = "<div class='span4 image-block'>";
        new_image_html += "<a href='"+json_data.image_location+"' target='_blank'>";
        new_image_html += "<center><div class='image-icon new-image'>";
        new_image_html += "<img src='"+json_data.image_location+"'>";
        new_image_html += "</div></center></a>";
        new_image_html += "<p><b>Name:</b> "+json_data.image_name+"</p>";
        new_image_html += "<p><b>Uploaded by:</b> "+json_data.image_uploaded_by+"</p>";
        new_image_html += "<p><b>Date Uploaded:</b> "+json_data.image_date+"</p>";
        new_image_html += "</div>";
        $(".uploaded-images").last().append(new_image_html);
    }

    //------------------------------------------------------------------------------------
    // If any field value, upon which locally-mandatory fields are dependent, is changed:
    // Need to apply highlighting and display a message to the user accordingly. The arrays
    // storing the necessary information (local_depend_ids, etc) are defined at the top of 
    // the script.
    //------------------------------------------------------------------------------------
    $.each(local_depend_ids, function(index, element) { 
        $(element).change(function(){
            // If becomes true, means the dependent field has not been provided. Only display message
            // and highlighting if is_missing is True
            var is_missing = false; 

            var field_label = "";
            var field_id = local_req_ids[index];
            var field_type = $(field_id).prop('type');

            // If the independent field is above the threshold
            if ($(this).val() >= local_thresholds[index] ) {
                field_label = $("label[for='"+$(field_id).attr('id')+"']").text();
                // How to check whether or not the field is "filled" depends on the type
                // of field. Handle these two cases for now:
                if (field_type == "checkbox"){
                    if (!$(field_id).prop('checked')) {
                        $("label[for='"+$(field_id).attr('id')+"']").addClass("local-mandatory-field");
                        $(field_id).addClass("local-mandatory-field");
                        $(field_id).next().addClass("local-mandatory-field");
                        is_missing = true;
                    }
                }
                else if (field_type == "text"){
                    if (!$(field_id).val()) {
                        $("label[for='"+$(field_id).attr('id')+"']").addClass("local-mandatory-field");
                        $(field_id).addClass("local-mandatory-field");
                        $(field_id).next().addClass("local-mandatory-field"); 
                        is_missing = true
                    }
                }

                if (is_missing) {
                    // Display message to user notifying them that the change has made fields now mandatory
                    var alertType = "alert-error";
                    ariaMessage(alertType, local_messages[index], 20000);
                }
            }
            else {
                $("label[for='"+$(field_id).attr('id')+"']").removeClass("local-mandatory-field");
            }
        });
    });

    //------------------------------------------------------------------------------------
    // Select Patient Disclosure for the Ameliorating Actions field if the Patient Disclosure
    // checkbox is checked; and vice-versa.
    //------------------------------------------------------------------------------------
    $("#id_patient_disclosure").change(function(){
        var disclosure_checked = $("#id_patient_disclosure").prop('checked');
        if (disclosure_checked) {
            $("#id_ameliorating_actions option[value="+6+"]").prop('selected',true);
            $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
        }
        else {
            $("#id_ameliorating_actions option[value="+6+"]").prop('selected',false);
            $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
        }
    });

    $("#id_ameliorating_actions").change(function(){
        if ($("#id_ameliorating_actions option[value="+6+"]").prop('selected')) {
            $("#id_patient_disclosure").prop('checked',true);
        }
        else {
            $("#id_patient_disclosure").prop('checked',false);
        }
    });

    //------------------------------------------------------------------------------------
    // The following function is performed when the user clicks the button to initiate the
    // template creation process. Display instructions & template-creation form to the
    // user. Also apply highlighting to all "templatable" fields so they may review the
    // fields they are saving.
    //------------------------------------------------------------------------------------
    $(".save-template").click(function(){
        // Remove existing highlighting on investigation form
        $(".control-group").removeClass("success"); // Remove success highlighting from hide-id divs
        $(".fill-fill").removeClass("fill-fill");
        $(".unfill-fill").removeClass("unfill-fill");
        $(".fill-unfill").removeClass("fill-unfill");

        //hide invalid stuff
        $(".mark-invalid").toggle();
        //hide image stuff
        $(".add-image").toggle();

        // show/hide instructions & form div
        $("#template-div").toggle();        

        if ($("#template-div").is(':visible')) {
            $(".update-investigation").hide();
            $("#hide-id_predefined_type").slideUp();
            $(this).html("Close Template Creation");
            // Apply highlighting
            for (var i=0; i<template_fields.length; i++) {
                var field_id = "#id_"+template_fields[i];
                $("label[for='"+$(field_id).attr('id')+"']").addClass("template-field");
                $(field_id).addClass("template-field");
                $(field_id).next().addClass("template-field");
            }
        }
        else {
            $(".update-investigation").show();
            $("#hide-id_predefined_type").slideDown();
            $(this).html("Create Incident Template");
            // Remove highlighting
            for (var i=0; i<template_fields.length; i++) {
                var field_id = "#id_"+template_fields[i];
                $("label[for='"+$(field_id).attr('id')+"']").removeClass("template-field");
                $(field_id).removeClass("template-field");
                $(field_id).next().removeClass("template-field");
            }
        }
    });

    //------------------------------------------------------------------------------------
    // This function is called when the user clicks the button to confirm saving a new
    // template. POST the "templatable" field-value pairs to the backend for processing
    // and (error checking and saving of the new template type). Receive the new errors
    // or successful data. Display message to the user accordingly. If successful, add
    // the newly created template to the Investigation template type field.
    //------------------------------------------------------------------------------------
    $(".confirm-template").click(function(){
        disableButtons('.confirm-template','Please Wait');

        var field_array = [];
        // Create array of form field-value pairs which should be saved for the template:
        for (var i=0; i<template_fields.length; i++) {
            var field_value_pair = {}
            var nam = "#id_"+template_fields[i];
            var val = $("#id_"+template_fields[i]).val();
            // var val = $("#id_"+template_fields[i]+" option:selected").text();
            field_value_pair["field_name"] =nam;
            field_value_pair["field_val"] =val;
            field_array.push(field_value_pair);
        }
        // AJAX POST & data reception:
        $.ajax({
            type: 'POST',
            url: $("#save_new_template_view").text(),
            dataType: 'json',
            // Pass the serialized template form & field-value pairs to the backend. Passing
            // in stringified URL notation: best way to parse the two types of data on the
            // backend:
            data: $('#template-form').serialize()+'&'+$.param({ 'fields': JSON.stringify(field_array)}),
            // data: { post_data: JSON.stringify(field_array), form_data: JSON.stringify($('#template-form').serializeArray()) },
            success: function(json_data){
                if (json_data.errors) {
                    applyErrors(json_data.errors);
                }
                else {
                    applyErrors(json_data.errors);
                    $(".save-template").trigger("click");
                    $('#template-form').trigger("reset");
                    var SUCCESS_MESSAGE = "New Template: " + json_data.template_name + " successfully saved!";
                    validMessage(SUCCESS_MESSAGE);
                    // Add new option:
                    $('#id_predefined_type').append('<option value="'+json_data.template_pk+'">'+json_data.template_name+'</option>');
                    $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
                }
                enableButtons('.confirm-template','Confirm Template Creation');
            },
            // If there is an unforseen problem posting the data:
            error: function(e) {
                var alertType = "error";
                var ERROR_MESSAGE = "There was a problem saving the template. Please contact the system administrator.";
                ariaMessage(alertType, ERROR_MESSAGE);
                enableButtons('.confirm-template','Confirm Template Creation');
            }
        });
        return false;
    });


    // Toggle dispay of form field to mark an incident as invalid
    $(".mark-invalid").click(function(){
        $("#invalid-div").toggle();
        $(".save-template").toggle();
        $(".add-image").toggle();
    });

    // Toggle stuff for adding new taskable action
    $(".display-action, .cancel-action").click(function(){
        $(".display-action").toggle();
        $(".add-action").toggle();
        $(".cancel-action").toggle();
        $("#new-action-span").toggle();
        $('select:not(.blocked-field, .reported-field)').chosen({search_contains:true, width:'100%'});
    });


    //------------------------------------------------------------------------------------
    // When clicking the "Update Actions" button on action forms which have just been
    // added on the current page load, need to manually trigger the AJAX post actions
    // method.
    //------------------------------------------------------------------------------------
    $("#set_of_forms").on('click', '.new-update-actions' , function() {
        postActions();
    });

    //------------------------------------------------------------------------------------
    // Called when the existing "Update Actions" buttons are clicked (i.e. not new forms)
    //------------------------------------------------------------------------------------
    $(".update-actions").click(function() {
        postActions();
    });

    //------------------------------------------------------------------------------------
    // Post data in the Actions formset to the view/DB
    //------------------------------------------------------------------------------------
    function postActions(){
        $.ajax({
            url: "/nsir/incident/" + thisInc + "/",
            method:"POST",
            data: $("#action-update-formset").serialize(),
            success: function(json_data){
                // If there are errors in the form fields:
                if (json_data.errors) {
                    // loop through all forms
                    for (var i = 0; i < json_data.errors.length; i++) {
                        var error_dict = json_data.errors[i];
                        var is_empty = jQuery.isEmptyObject(error_dict);
                        // If there are errors in the current form
                        if (!is_empty){
                            applyActionErrors(i, error_dict);
                            removeMessages();
                        }
                        // If there are no errors in the current form, remove errors which
                        // may previously have been in place on the current form
                        else {
                            removeActionErrors(i);
                        }
                    }
                }
                // No errors, POST was successful
                else {
                    // Remove previous errors
                    // 
                    for (var i = 0; i < parseInt(json_data.num_forms); i++) {
                        removeActionErrors(i);
                    }
                    // Apply success highlighting on successfully changed fields
                    applyActionSuccess(json_data.changed);
                    // Toggle display of completion info on the formsets
                    toggleActionCompleteInfo(json_data);

                    // Before this, just_completed and incompleted are arrays holding the
                    // relevant info for each action. This info has been used already (above)
                    // so safe to assign to the incident completion status and toggle its
                    // display accordingly
                    json_data.just_completed = json_data.inc_just_completed
                    json_data.just_incompleted = json_data.inc_just_incompleted
                    toggleCompleteInfo(json_data);

                    // header message:
                    var SUCCESS_MESSAGE = ""
                    if (json_data.just_completed) {
                        SUCCESS_MESSAGE = "Investigation completed! Actions successfully updated.";
                    }
                    else {
                        SUCCESS_MESSAGE = "Actions successfully updated";
                    }
                    var alertType = "alert-success";
                    ariaMessage(alertType, SUCCESS_MESSAGE);
                }
            },
            // Problems outside of the data
            error: function(e){
                var ERROR_MESSAGE = "There was a problem updating the actions. Please contact the system administrator";
                var alertType = "alert-error";
                ariaMessage(alertType, ERROR_MESSAGE);
            }
        });
        return false;
    }

    //------------------------------------------------------------------------------------
    // Function to determine whether or not an action has been completed or incompleted
    // and toggle display of complete info accordingly.
    //
    // @param {dictionary} json_data - Contains information passed from the view.
    // Relevant keys:
    //  {number} num_forms - number of forms in the formset
    //  {just_completed} - array of Booleans indicating whether each form was just completed
    //  {just_incompleted} - array of Booleans indicating whether each form was just incompleted
    //  {completed_date} - array of strings representing the date each form was completed
    //  {completed_by} - array of strings representing who completed each form
    //------------------------------------------------------------------------------------
    function toggleActionCompleteInfo(json_data){
        var num_forms = parseInt(json_data.num_forms);
        // var changed = json_data.changed;
        var just_completed = json_data.just_completed;
        var just_incompleted = json_data.just_incompleted;
        var completed_date = json_data.completed_date;
        var completed_by = json_data.completed_by;

        for (var i = 0; i < num_forms; i++) {
            if (just_completed[i]) {
                $("#hide-complete-action-"+i).html("<br><b>Date Completed:</b> "+completed_date[i]+"<br><b>Completed By:</b> "+completed_by[i]);
                $("#hide-complete-action-"+i).toggle();

                // $(".act_status-"+i).toggleClass('label_info label_success');
                $(".act_status-"+i).text("Complete");
                $(".act_status-"+i).removeClass("inv_color_incomplete");
                $(".act_status-"+i).addClass("inv_color_complete");

                UpdateActionEditable(i)
            }
            if (just_incompleted[i]) {
                $("#hide-complete-action-"+i).html("<br><b>Date Completed:</b> <br><b>Completed By:</b> ");
                $("#hide-complete-action-"+i).toggle();

                $(".act_status-"+i).text("Incomplete");
                $(".act_status-"+i).removeClass("inv_color_complete");
                $(".act_status-"+i).addClass("inv_color_incomplete");
            }
        }
    }

    //------------------------------------------------------------------------------------
    // Update readonly status of fields a particular action update form.
    //
    // @param {number} form_id - the ID associated with a form for a particular Incident
    // Action, within a formset tied to a particular Incident/Investigation
    //------------------------------------------------------------------------------------
    function UpdateActionEditable(form_id) {
        $("#id_form-"+form_id+"-complete").attr('readonly',true);
        $("#id_form-"+form_id+"-complete").addClass('blocked-action-field');
        $("#id_form-"+form_id+"-complete").removeClass('editable-action-field');
        $("#id_form-"+form_id+"-description_performed").attr('readonly',true);
        $("#id_form-"+form_id+"-description_performed").addClass('blocked-action-field');
        $("#id_form-"+form_id+"-description_performed").removeClass('editable-action-field');
    }

    //------------------------------------------------------------------------------------
    // Apply success highlighting to succesfully updated actions in the actions formset.
    //
    // @param {array} formset_changed - Array of arrays. Each element in the outer array
    // corresponds to a form in the action formset. Each inner array contains the form 
    // fields which have changed since the previous POST. Forms which did not change are
    // indicated by empty arrays
    //------------------------------------------------------------------------------------
    function applyActionSuccess(formset_changed) {
        // remove previous success fields
        $(".success").removeClass("success");
        if (formset_changed) {
            // loop through all forms
            for (var form_id = 0; form_id < formset_changed.length; form_id++) {
                // Fields which have changed in the current form
                var form_changed = formset_changed[form_id];

                // Apply successes
                $.each(form_changed, function (changed_index, field) {
                    var parent_div = "#hide-id_form-" + form_id + "-" + field;
                    $(parent_div).addClass("success");
                });
            }
        }  
    }

    //------------------------------------------------------------------------------------
    // Remove action error messages and highlighting
    //
    // @param {number} form_id - the ID associated with a form for a particular Incident
    // Action, within a formset tied to a particular Incident/Investigation
    //------------------------------------------------------------------------------------
    function removeActionErrors(form_id) {
        $.each($(".error-msg-" + form_id), function() {
            $(this).slideUp('fast', function() {
                $(this).parent().parent().removeClass("error"); // remove red error class
                $(this).remove(); // remove the error message
            });
        });
    }

    //------------------------------------------------------------------------------------
    // Apply error highlighting and messages to applicable fields for an Incident Action
    //
    // @param {number} form_id - the ID associated with a form for a particular Incident
    // Action, within a formset tied to a particular Incident/Investigation
    //
    // @param {dictionary} errors - dictionary of arrays, with keys corresponding to the
    // form field names. The arrays contain the errors associated with that field, and
    // typically contain only one single element. This element is a string which describes
    // the error to be displayed to the user.
    //------------------------------------------------------------------------------------
    function applyActionErrors(form_id, errors) {
        $(".error-msg-" + form_id).addClass("remove-msg"); // Add class to remove error message to existing error messages

        $(".success").removeClass("success"); // Remove success highlighting

        // Loop through errors and apply them to appropriate field Add error class to
        // some parent div of the field (typically that div is named like 'hide-
        // id_field_name'). That div contains both the label and the field itself, so
        // error (red) highlighting is applied to both. Also handle application of
        // error messages below the appropriate fields.
        $.each(errors, function (field, message) {
            var $errorMsg = $("#error-field-form-" + form_id + "-" + field);
            // If there was previously no error message do the following:
            // (Note that $newDiv holds the error message. Insert below that field)
            if ($errorMsg.length == 0) {
                var $newDiv;
                var $control = $("#id_form-" + form_id + "-" + field);
                var $parent_div = $("#hide-id_form-" + form_id + "-" + field);
                
                $parent_div.addClass("error");
                $newDiv = $("<div id='error-field-form-"+ form_id + "-" + field + "' class='error-msg error-msg-" + form_id + " help-block' style='display: none;'>" + message + "</div>");   
                $newDiv.insertAfter($control).slideDown('fast');
            }
            // If there was previously an error message, and there still is an error,
            // the message should persist; so remove the 'remove-msg' class 
            else {
                $($errorMsg).text(message).removeClass("remove-msg");
            }
        });

        // Remove errors from previously errored fields, which have now been ameliorated.
        // I.e. remove the message, and remove error highlighting.
        $.each($(".remove-msg"), function() {
            $(this).slideUp('fast', function() {
                $(this).parent().removeClass("error");
                $(this).parent().parent().removeClass("error");
                $(this).remove();
            });
        });
    }

    //------------------------------------------------------------------------------------
    // Called when the "Add Action" button is clicked. If valid, POST the inputted data
    // to create a new IncidentAction in the formset and display it. If invalid, display
    // errors to the user.
    //------------------------------------------------------------------------------------
    $(".add-action").click(function(){
        disableButtons('.add-action','Please Wait');

        $.ajax({
            url: "/nsir/incident/" + thisInc + "/",
            method:"POST",
            data: $("#action-create-form").serialize(),
            success: function(json_data){
                // Standard error application
                applyErrors(json_data.errors);

                // If there were no errors
                if (!json_data.errors){

                    // toggle display of creation form & buttons
                    $("#action-create-form").trigger('reset');
                    $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
                    $(".display-action").toggle();
                    $(".add-action").toggle();
                    $(".cancel-action").toggle();
                    $("#new-action-span").toggle();

                    // Display the new action form as an UpdateActionForm alongside the
                    // others
                    DisplayNewActionForm(json_data);

                    // Toggle the displayed completion info of the incident (make incomplete if was complete)
                    toggleCompleteInfo(json_data);

                    // header message:
                    var SUCCESS_MESSAGE = ""
                    if (json_data.just_incompleted) {
                        SUCCESS_MESSAGE = "Investigation no longer complete: Action successfully tasked to " + json_data.responsible_first + " " + json_data.responsible_last;
                    }
                    else {
                        SUCCESS_MESSAGE = "Action successfully tasked to " + json_data.responsible_first + " " + json_data.responsible_last;
                    }
                    var alertType = "alert-success";
                    ariaMessage(alertType, SUCCESS_MESSAGE);

                    $('select:not(.blocked-field, .reported-field)').chosen({search_contains:true, width:'100%'});
                }

                enableButtons('.add-action','Submit');
            },
            error: function(e){
                var ERROR_MESSAGE = "There was a problem submitting the action. Please contact the system administrator";
                var alertType = "alert-error";
                ariaMessage(alertType, ERROR_MESSAGE);
                enableButtons('.add-action','Submit');
            }
        });
        return false;
    });


    //------------------------------------------------------------------------------------
    // Display a new UpdateActionFormset 
    //
    // @param {dictionary} json_data - Contains information passed from the view.
    //
    // Relevant keys:
    //  {string} incident_id - ID number of the incident to which the action is tied
    //  {string} action_id - ID number of the action
    //  {string} date_assigned - date the action was assigned (created)
    //  {string} id_pk - The primary key of the action object
    //  {string} description_proposed - description of the proposed action
    //  {string} responsible - string representing the name of the individual who is
    //  responsibe for the action
    //------------------------------------------------------------------------------------ß
    function DisplayNewActionForm(json_data) {
        // gives 0 if there are none
        // new_form_id is also the number of forms in the formset prior to the addition
        var new_form_id = $("#id_form-TOTAL_FORMS").val();
        $('#set_of_forms').prepend($('#empty_form').html().replace(/__prefix__/g, new_form_id))
        $('#id_form-TOTAL_FORMS').val(parseInt(new_form_id) + 1);

        // Header
        $("#action-header-" + new_form_id).html("Incident #"+json_data.incident_id+" - Action #"+json_data.action_id);

        // Assigned Info
        $("#hide-initial-action-" + new_form_id).html("<b>Date Assigned:</b> "+json_data.date_assigned+"<br><b>Assigned By:</b> "+json_data.assigned_by);

        // Filling Form Values
        $("#id_form-" + new_form_id + "-instance_id").val(parseInt(json_data.id_pk));
        $("#id_form-" + new_form_id + "-description_proposed").val(json_data.description_proposed);
        $("select#id_form-"+new_form_id+"-responsible option").filter(function() {
            //may want to use $.trim in here
            return $(this).text() == json_data.responsible; 
        }).prop('selected', true);
        $("#id_form-"+new_form_id+"-responsible").addClass('blocked-field');

        // $("#hide-id_form-"+new_form_id+"-description_performed").slideUp();
    }

    //------------------------------------------------------------------------------------
    // Called when the "Mark Invalid" button is clicked
    //------------------------------------------------------------------------------------
    $(".confirm-invalid").click(function(){
        disableButtons('.confirm-invalid','Please Wait');

        $.ajax({
            url: "/nsir/incident/" + thisInc + "/",
            method:"POST",
            data: $("#invalid-form").serialize(),
            success: function(json_data){
                applyErrors(json_data.errors);
                if (!json_data.errors){
                    toggleCompleteInfo(json_data);
                    $(".mark-invalid").toggle();
                    $(".mark-valid").toggle();
                    $("#invalid-div").toggle();
                    var SUCCESS_MESSAGE = "Investigation Successfully Closed as Invalid";
                    validMessage(SUCCESS_MESSAGE);
                }

                enableButtons('.confirm-invalid','Confirm Invalid');
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
        $("#floating-status-message").remove();
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
                    $($control).parent().parent().addClass("error");
                    if (($control).next().hasClass("chosen-container")) {
                        $control.next().addClass("chosen-error");
                        $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                        $newDiv.insertAfter($control.next()).slideDown('fast');
                    }
                    else {
                        $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                        $newDiv.insertAfter($control).slideDown('fast');
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

    function removeMessages() {
        // $(".ajax_messages").html("");
        $("#floating-status-message").remove();
    }

    //------------------------------------------------------------------------------------
    // Called when the "Re-Open Investigation" button is clicked
    //------------------------------------------------------------------------------------
    $(".mark-valid").click(function(){
        disableButtons('.mark-valid','Please Wait')
        $.ajax({
            url: "/nsir/incident/" + thisInc + "/",
            method:"POST",
            data: $("#valid-form").serialize(),
            success: function(json_data){
                toggleCompleteInfo(json_data);
                var SUCCESS_MESSAGE = "Investigation Successfully Re-Opened";
                $("#id_invalid_reason").val(null);
                $(".mark-valid").toggle();
                $(".mark-invalid").toggle();
                $(".save-template").toggle();
                $(".add-image").toggle();
                validMessage(SUCCESS_MESSAGE);
                enableButtons('.mark-valid','Re-Open Investigation')
            }
        });
        return false;
    });

    //------------------------------------------------------------------------------------
    // Display an ajax message to the user which indicates whether or not setting the
    // incident as valid or invalid was successful.
    //
    // @param {string} messageText - a string containing the message to be displayed.
    //------------------------------------------------------------------------------------
    function validMessage(messageText) {
        // $(".ajax_messages").html("");
        // $("#floating-status-message").remove();
        // $(".ajax_messages").append("<div class='message-div alert alert-success style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        // $(".alert").slideDown();

        var $message = $("<div class='floating-message-div alert alert-success style='width:100%'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        $('.navbar').append($message);
         setTimeout(function() {
             $message.remove();
         }, 10000)
    }

    //------------------------------------------------------------------------------------
    // Called when any of the "Update" buttons on the investigation page are pressed.
    // Make several sub-function calls to handle highlighting success/error fields,
    // displaying messages, and highlighting missing fields.
    //------------------------------------------------------------------------------------
    $(".update-investigation").click(function(){
        //$(".update-investigation").off();
        //$("#investigation-form").submit();
        //updateNewForms();
        $.ajax({
            url: "/nsir/incident/" + thisInc + "/",
            method:"POST",
            data: $("#investigation-form").serialize(),
            success: function(json_data){
                // If a POST somehow was attempted for an unauthorized user:
                if (json_data.blocked_post) {
                    var blocked_message = [{"extra_tags":"error", "message":"Changes not saved. You do not have write privileges for this investigation!"}];
                    updateMessages(blocked_message);
                }
                else if (json_data.empty_post) {
                    var empty_message = [{"extra_tags":"", "message":"No changes made"}];
                    updateMessages(empty_message);
                }
                else {
                    // $(".filled").removeClass("filled");
                    $(".template-msg").remove();
                    $(".fill-fill").removeClass("fill-fill");
                    $(".unfill-fill").removeClass("unfill-fill");
                    $(".fill-unfill").removeClass("fill-unfill");
                    toggleCompleteInfo(json_data);
                    //applyErrors(json_data.errors);
                    applySuccess(json_data.changed);
                    updateMessages(json_data.messages);
                    updateEditable(json_data.can_edit,json_data.valid);   
                }
            }
        });
        return false;
    });

    //------------------------------------------------------------------------------------
    // Function to determine whether or not the investigation is completed, and call
    // functions to handle displaying of missing fields or completed information
    // accordingly.
    //
    // @param {dictionary} json - Contains information passed from the view.
    // Relevant keys:
    //  {Boolean} inv_complete - indicates whether or not investigation is complete
    //------------------------------------------------------------------------------------
    function toggleCompleteInfo(json){
        if(!json.valid) {
            handleInvalid(json);
        }
        else if(json.inv_complete) {
            handleComplete(json);
        }
        else {
            handleIncomplete(json);
        }
    }

    //------------------------------------------------------------------------------------
    // Function to handle updating the investigation page if the investigation is
    // invalid. Remove missing highlights, display date completed, toggle complete icon.
    //
    // @param {dictionary} json - Contains information passed from the view.
    // Relevant keys:
    //  {text} invalid_reason - Why incident marked as invalid.
    //------------------------------------------------------------------------------------
    function handleInvalid(json) {
        $(".complete_status").text("Investigation Completed (Invalid): "+json.valid_status_date);
        $(".complete_date_missing_fields").text(json.invalid_reason);
        $("#complete_status_signature").text("--"+json.valid_status_by);
        $(".complete_date_missing_fields").removeClass("missing");
        $(".complete_date_missing_fields").removeClass("complete-text");
        // $(".complete_date_missing_fields").addClass("invalid");

        $(".status_text").text("Invalid for Trending");
        $(".status_text").removeClass("inv_color_incomplete");
        $(".status_text").removeClass("inv_color_complete");
        $(".status_text").addClass("inv_color_invalid");
    }

    //------------------------------------------------------------------------------------
    // Function to handle updating the investigation page if the investigation is
    // complete. Remove missing highlights, display date completed, toggle complete icon.
    //
    // @param {dictionary} json - Contains information passed from the view.
    // Relevant keys:
    //  {Array} field_labels - All non many-to-many form field names (strings)
    //  {Array} m2m_field_labels - All many-to-many form field names (strings)
    //  {number} inv_day, inv_month, inv_year - numbers representing the date the
    //      investigation was completed.
    //  {Boolean} just_completed - Indicates whether or not the investigation completion
    //      status changed to 'complete' on the most recent form POST
    //------------------------------------------------------------------------------------
    function handleComplete(json) {
        $(".complete_status").text("Completed:");

        // Remove missing class from field labels
        for (var i=0; i<json.field_labels.length; i++) {
            //$("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").css('color','#333');
            $("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").removeClass("missing");
        }
        //Remove highlighting from local mandatory fields (must be filled if complete)
        $(".local-mandatory-field").removeClass("local-mandatory-field");

        // // Remove missing class from m2m field labels
        // for (var i=0; i<json.m2m_field_labels.length; i++) {
        //     //$("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").css('color','#333');
        //     $("label[for='"+$("#id_"+json.m2m_field_labels[i]).attr('id')+"']").removeClass("missing");
        // }

        $(".complete_status").text("Investigation Completed: "+json.inv_complete_date);
        $(".complete_date_missing_fields").text(json.inv_narrative);
        $("#complete_status_signature").text("--"+json.inv_narrative_by);
        $(".complete_date_missing_fields").removeClass("missing");
        $(".complete_date_missing_fields").removeClass("invalid");
        //$(".complete_date_missing_fields").addClass("complete-text");

        // toggle the icon representing the investigation completion status at top of page
        if (json.just_completed) {
            $(".status_text").toggleClass('label_info label_success');
        }
        $(".status_text").text("Complete");
        $(".status_text").removeClass("inv_color_incomplete");
        $(".status_text").removeClass("inv_color_invalid");
        $(".status_text").addClass("inv_color_complete");
    }

    //------------------------------------------------------------------------------------
    // Function to handle updating the investigation page if the investigation is
    // incomplete. Add missing highlights, display list of missing fields, toggle complete
    // icon.
    //
    // @param {dictionary} json - Contains information passed from the view.
    // Relevant keys:
    //  {Array} field_labels - All non many-to-many form field names (strings)
    //  {Array} m2m_field_labels - All many-to-many form field names (strings)
    //  {Array} missing_field_labels - Names of missing form fields which are mandatory
    //  {Array} missing_fields - Verbose names of missing form fields which are mandatory
    //  {Boolean} just_incompleted - Indicates whether or not the investigation completion
    //      status changed to 'incomplete' on the most recent form POST
    //------------------------------------------------------------------------------------
    function handleIncomplete(json) {
        $(".complete_status").text("Missing fields which are required to complete the investigation:");
        
        // Remove missing class from field labels
        for (var i=0; i<json.field_labels.length; i++) {
            //$("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").css('color','#333');
            $("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").removeClass("missing");
        }
        // Remove local-mandatory-field class
        $(".local-mandatory-field").removeClass("local-mandatory-field");

        // // Remove missing class from m2m field labels
        // for (var i=0; i<json.m2m_field_labels.length; i++) {
        //     //$("label[for='"+$("#id_"+json.field_labels[i]).attr('id')+"']").css('color','#333');
        //     $("label[for='"+$("#id_"+json.m2m_field_labels[i]).attr('id')+"']").removeClass("missing");
        // }

        // Add missing class to any missing field labels (for coloring in orange), and 
        // add the verbose field name to list of missing fields
        // Also account for particular missing fields that may be required locally, not
        // according to the NSIR taxonomy
        var missing_string = "";
        for (var i=0; i<json.missing_fields.length; i++) {
            //console.log("id_" + json.missing_field_labels[i]);
            if (jQuery.inArray("#id_"+json.missing_field_labels[i],local_mandatory_fields_html) >= 0){
                $("label[for='"+$("#id_"+json.missing_field_labels[i]).attr('id')+"']").addClass("local-mandatory-field");
                missing_string += "<span class='local-mandatory-field'>"+json.missing_fields[i]+"</span>";
                if (i<json.missing_fields.length-1) {
                    missing_string += ", ";
                }
            }
            else {
                $("label[for='"+$("#id_"+json.missing_field_labels[i]).attr('id')+"']").addClass("missing");
                missing_string += json.missing_fields[i];
                if (i<json.missing_fields.length-1) {
                    missing_string += ", ";
                }
            }
        }

        $(".complete_status").text("Missing information required to complete the investigation:");
        $(".complete_date_missing_fields").html(missing_string);
        $("#complete_status_signature").text("");
        $(".complete_date_missing_fields").removeClass("complete-text");
        $(".complete_date_missing_fields").removeClass("invalid");
        $(".complete_date_missing_fields").addClass("missing");

        // toggle the icon representing the investigation completion status at top of page
        if (json.just_incompleted) {
            $(".status_text").toggleClass('label_info label_success');
        }
        $(".status_text").text("Incomplete");
        //$(".status_text").css('background-color', 'red');
        $(".status_text").removeClass("inv_color_complete");
        $(".status_text").removeClass("inv_color_invalid");
        $(".status_text").addClass("inv_color_incomplete");
    }

    //------------------------------------------------------------------------------------
    // Apply success highlighting and messages to applicable fields.
    //
    // @param {array} changed - Array of form fields (e.g event_type) whose inputted
    // values differ from the initial values which were specified. Thus, those fields
    // whose values were specified in form initialization, are not included.
    //------------------------------------------------------------------------------------
    function applySuccess(changed) {
        // remove previous success fields
        $(".success").removeClass("success");

        // Apply successes (i holds 0, m holds changed field name, e.g incident_description)
        // Adds success class to the hide-id_field_name div, for highlighting in green
        if (changed) {
            $.each(changed, function (i, m) {
                if (m != "complete") {
                    if (m == "date_incident_occurred") {
                        $("#hide-id_date_incident_occurred").addClass("success");
                    }
                    else {
                        $("#hide-id_" + m).addClass("success");
                    }
                }
            });
        }      
    }

    //------------------------------------------------------------------------------------
    // Update AJAX message divs at top and bottom of the page.
    //
    // @param {array} messages - single element array containing a dictionary.
    // Relevant keys of the dictionary:
    //  {string} extra_tags - contains additional classes which should be added to the 
    //      message text
    //  {string} message - Actual message to be displayed
    //------------------------------------------------------------------------------------
    function updateMessages(messages) {
        // $(".ajax_messages").html("");
        $("#floating-status-message").remove();

        // Show message (i holds 0, m is a dictionary containing relevant material)
        if (messages) {
            $.each(messages, function (i, m) {
                // $(".ajax_messages").append("<div class='message-div alert alert-" + m.extra_tags + "' style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + m.message + "</strong></div>");
                
                var $message = $("<div id='floating-status-message' class='floating-message-div alert alert-" + m.extra_tags + " style='width:96%'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + m.message + "</strong></div>");
                $('.navbar').append($message);
                 setTimeout(function() {
                     $message.remove();
                 }, 10000)
            });
            // $(".alert").slideDown();
        }
    }

    //------------------------------------------------------------------------------------
    // Update readonly status of fields in the investigation form based on whether or
    // not the current user has editing privileges.
    //
    // @param {Boolean} can_edit - indicates whether or not the user can make changes to
    // the investigation or not.
    //------------------------------------------------------------------------------------
    function updateEditable(can_edit,valid) {
        if (can_edit) {
            $(".blocked-field").addClass("editable-field");
            $(".blocked-field").removeClass("blocked-field");
            $(".editable-field").attr('readonly',false);
            $(".update-investigation").show();
            if (valid) {
                $(".mark-invalid").show();
                $(".mark-valid").hide();
            }
            else if (!valid){
                $(".mark-valid").show();
                $(".mark-invalid").hide();
            }
            $(".get-pat").show();
            $("#id_date_incident_occurred").parent().addClass("datepicker");
            $("#instructions-blocked").hide();
            $("#instructions-editable").show();
        }
        else {
            $(".editable-field").addClass("blocked-field");
            $(".editable-field").removeClass("editable-field");
            $(".blocked-field").attr('readonly',true);
            $(".update-investigation:not(.clickable)").hide();
            $(".mark-invalid").hide();
            $(".mark-valid").hide();
            $(".get-pat").hide();
            $("#id_date_incident_occurred").parent().removeClass("datepicker");
            $("#instructions-editable").hide();
            $("#instructions-blocked").show();
        }
    }

    //------------------------------------------------------------------------------------
    // Called when the user requests treatment information from the EMR (ARIA at MUHC).
    // Display a series of tables containing the treatment information associated with
    // patient ID associated with the current investigation. Display message to the user
    // indicating whether or not the query was successful.
    //------------------------------------------------------------------------------------
    $(".get-tmnt").click(function(){

        var SUCCESS_MESSAGE = "Treatment information successfully retrieved from the EMR";
        var FAILURE_MESSAGE = "No radiotherapy treatment information could be found for the provided patient ID";
        var ERROR_MESSAGE = "There was a problem with the query, please contact the system administrator";
        var current_patient_id = $("#id_patient_id").val();

        // Only call php/query ARIA single time per page load (non-ajax)
        if ($.trim($("#tmnt-info").text()) === "" ) {
            $.ajax({
                type: 'POST',
                dataType: "json",
                data: { patientID: current_patient_id },
                url: PHP_DIR.concat("queryTreatment.php"),
                // url: "/nsir/ajax/", // Relative paths are allowed if defined in URLCONF & view is provided
                success: function(mydata) {
                    // Successful access of PHP script, but no query result
                    if (typeof mydata == "undefined" || mydata.length === 0) {
                        var alertType = "";
                        ariaMessage(alertType, FAILURE_MESSAGE);
                    }
                    // Successful query
                    else {
                        // Determine # of plans and courses, autofill/display tables accordingly
                        var num_c=0; // number of courses
                        var num_p=0; // number of plans
                        var i_p;
                        while (mydata[num_c.toString()]) {
                            i_p = 0;
                            while (mydata[num_c][i_p.toString()]) {
                                i_p = i_p + 1;
                            }
                            num_p = num_p + i_p;
                            num_c = num_c + 1;
                        }
                        // If only single plan retrieved, autopopulate treatment fields with that plan
                        if (num_p == 1) {
                            var total_dose = mydata["0"]["0"]["nofractions"]*mydata["0"]["0"]["dose"];
                            var num_fractions = mydata["0"]["0"]["nofractions"];
                            var modalities = mydata["0"]["0"]["mods_pk"];

                            $("#id_radiation_treatment_techniques option:selected").prop('selected',false);
                            for (var i=0; i<modalities.length; i++) {
                                $("#id_radiation_treatment_techniques option[value="+modalities[i]+"]").prop('selected',true);
                            }
                            $("#id_total_dose_prescribed").val(Math.round(total_dose*100.0)/100.0);
                            $("#id_number_fractions_prescribed").val(num_fractions)

                            $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
                            SUCCESS_MESSAGE = "Treatment information (single plan) successfully retrieved and autopopulated!";
                        }

                        // Prepare treatment information tables
                        prepareText(mydata, current_patient_id);
                        toggleButtonText();
                        var alertType = "alert-success";
                        ariaMessage(alertType, SUCCESS_MESSAGE);
                    }
                },
                // Error in accessing PHP script
                error: function(e) {
                    var alertType = "alert-error";
                    ariaMessage(alertType, ERROR_MESSAGE);
                }
            });
        }
        // If already queried on this page load, just toggle display of the table
        else {
            $("#tmnt-info").toggle();
            toggleButtonText();
        }
    });

    function check_and_anonymize(name_string) {
        if (ANONYMOUS_DISPLAY) {
            var anon_str = "";
            for (var index=0;index<name_string.length;index++) {
                anon_str +="*";
            }
            return anon_str;
        }
        else {
            return name_string;
        }
    }

    //------------------------------------------------------------------------------------
    // Handles clicking buttons to populate treatment information (buttons fount in
    // treatment information tables)
    //------------------------------------------------------------------------------------
    $(document).on('click', '.fill-tmnt', function(){
        fill_treatment_info(this);
    });
    function fill_treatment_info(pressed) {
        var prev_filled = false;
        var FILL_MESSAGE;
        var alertType;

        //Index the Table (determine the row (plan) the user has selected)
        var table = $(pressed).parents(".dataTable");
        table = table.DataTable();
        var cur_row = table.row($(pressed).parent());
        var row_data = cur_row.data();

        // Values to populate - modalities requires conversion from str to array of ints
        var total_dose = row_data[6];
        var num_fractions = row_data[7];
        var modalities = $.trim(row_data[8]);
        modalities = modalities.split(",");
        modalities.pop();

        // Fill fields. For each, determine if there was an existing value selected; if so,
        // display different message to the user notifying them that previous values were replaced
        if ($("#id_radiation_treatment_techniques option:selected").prop('selected',true).length > 0) {
            prev_filled = true;
        }
        $("#id_radiation_treatment_techniques option:selected").prop('selected',false);
        for (var i=0; i<modalities.length; i++) {
            $("#id_radiation_treatment_techniques option[value="+modalities[i]+"]").prop('selected',true);
        }

        if ($("#id_total_dose_prescribed").val()) {
            prev_filled = true;
        }
        $("#id_total_dose_prescribed").val(Math.round(total_dose*100.0)/100.0);

        if ($("#id_number_fractions_prescribed").val()) {
            prev_filled = true;
        }
        $("#id_number_fractions_prescribed").val(num_fractions)

        $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
        
        // Display message to the user
        if (!prev_filled) {
            alertType= "alert-success";
            FILL_MESSAGE = "Treatment information successfully populated";
        }
        else {
            alertType= "alert";
            FILL_MESSAGE = "Treatment information successfully populated, previous input replaced";
        }
        ariaMessage(alertType, FILL_MESSAGE);
    }

    //------------------------------------------------------------------------------------
    // Prepare the text (tables) containing treatment information to be displayed to the 
    // user. 
    // 
    // @param {dictionary} mydata - A dictionary which behaves like an array and a
    // dictionary. Indexing the dictionary like an array (using stringified numbers "0",
    // "1", etc) will return another dictionary which represents a single treatment
    // course. However the mydata dictionary also has additional keys for FirstName,
    // LastName, and DoseUnits.
    //
    //      Course Dictionary: contains a key for the 'name' of the course. May also be
    //      indexed similarly to above, to access each treatment plan within that course.
    //      Each plan object is also represented with a dictionary.
    //
    //          Plan Dictionary: contains keys for creation date 'date', plan id 'name',
    //          plan status 'status', user who set the status 'status_user', prescribed
    //          dose per fraction 'dose', and number fractions 'nofractions'. Can also be
    //          indexed similarly to above to access each field within that plan. Each
    //          field object is also represented with a dictionary.
    //
    //              Field Dictionary: contains key for the name of the field 'name'
    //
    // @param {string} current_patient_id - ID of the patient assoc. with investigation
    //------------------------------------------------------------------------------------
    function prepareText(mydata, current_patient_id) {
        mydata["FirstName"] = check_and_anonymize(mydata["FirstName"]);
        mydata["LastName"] = check_and_anonymize(mydata["LastName"]);
        // tmnttext holds the tables to be displayed containing treatment information
        var tmnttext = "<h4><center>Treatment Plan Information for " + mydata["FirstName"] + " " + mydata["LastName"] + " (ID:" + current_patient_id + ")</center></h4>";
        // i is used to index courses, j is used to index plans, and k is used to index
        // fields
        var i = 0;
        var j = 0;
        var k = 0;
        // Convert each index integer to a string, to index the dictionary (nomenclature of
        // a k after the index implies key)
        var ik = i.toString();
        var jk = j.toString();
        var kk = k.toString();

        while (mydata[ik] !== undefined){
            tmnttext += "<table class ='table table-striped mytable tmnt-table'>";
            tmnttext += "<thead>";
            tmnttext += "<tr><th colspan='9'>Treatment Course: " + mydata[ik]["name"] + "</th></tr>";
            tmnttext += "<tr>";
            tmnttext += "<th>Click to Populate</th>";
            tmnttext += "<th>Date Created</th>";
            tmnttext += "<th>Plan ID</th>";
            tmnttext += "<th>Modality</th>";
            //tmnttext += "<th>Intent</th>";
            //tmnttext += "<th>Clinical Status</th>";
            tmnttext += "<th>Plan Status</th>";
            tmnttext += "<th>Plan Status Set By</th>";
            tmnttext += "<th>Prescribed Dose (" + mydata["DoseUnits"] +")</th>";
            tmnttext += "<th># of Fractions</th>";
            // tmnttext += "<th>Fields</th>";
            tmnttext += "<th style='display:none'>Modality Key(s)</th>";
            tmnttext += "</tr>";
            tmnttext += "</thead>";
            tmnttext += "<tbody>";

            while (mydata[ik][jk] !== undefined){
                var totaldose = mydata[ik][jk]["dose"] * mydata[ik][jk]["nofractions"];
                mydata[ik][jk]["status_user"] = check_and_anonymize($.trim(mydata[ik][jk]["status_user"]));
                tmnttext += "<tr>";
                tmnttext += "<td>" + "<button type='button' style='margin-right:5px;' class='btn btn-primary emr-shader fill-tmnt'>Populate Treatment Info</button>" + "</td>";                
                tmnttext += "<td>" + $.trim(mydata[ik][jk]["date"]) + "</td>";
                tmnttext += "<td>" + $.trim(mydata[ik][jk]["name"]) + "</td>";
                tmnttext += "<td>" + mydata[ik][jk]["mods"] + "</td>";
                //tmnttext += "<td>" + $.trim(mydata[ik][jk]["intent"]) + "</td>";
                //tmnttext += "<td>" + $.trim(mydata[ik][jk]["cstatus"]) + "</td>";
                tmnttext += "<td>" + $.trim(mydata[ik][jk]["status"]) + "</td>";
                tmnttext += "<td>" + $.trim(mydata[ik][jk]["status_user"]) + "</td>";
                tmnttext += "<td>" + totaldose + "</td>";
                tmnttext += "<td>" + $.trim(mydata[ik][jk]["nofractions"]) + "</td>";
                // tmnttext += "<td>";
                // while (mydata[ik][jk][kk] !== undefined){
                //     tmnttext += mydata[ik][jk][kk]["name"] + ",";
                //     k += 1;
                //     var kk = k.toString();
                // }
                // tmnttext += "</td></tr>";
                tmnttext += "<td style='display:none'>";
                for (var ind=0;ind<mydata[ik][jk]["mods_pk"].length;ind++) {
                    tmnttext += mydata[ik][jk]["mods_pk"][ind] + ",";
                }
                tmnttext += "</td>";
                tmnttext += "</tr>";
                k = 0;
                var kk = k.toString();
                j += 1;
                var jk = j.toString();
            }
            tmnttext += "</tbody>";
            tmnttext += "</table><hr>";
            k = 0;
            var kk = k.toString();
            j = 0;
            var jk = j.toString();
            i += 1;
            var ik = i.toString();
        }

        $("#tmnt-info").html(tmnttext);
        // Convert the table into a jQuery dataTable
        $(".tmnt-table").DataTable({
            sDom:'<<ir>><<rt>><<p>>',
            iDisplayLength: -1, // Display all rows
            "aoColumns": [
            { "sWidth": "20%" },
            { "sWidth": "10%" },
            //{ "sWidth": "10%" },
            //{ "sWidth": "10%" },
            { "sWidth": "10%" },
            { "sWidth": "20%" },
            { "sWidth": "10%" },
            { "sWidth": "10%" },
            { "sWidth": "10%" },
            { "sWidth": "10%" },
            // { "sWidth": "40%" },
            { "sWidth": "0%" },
            ],
            "bInfo": false, // Disable: "Showing x to y of z entries"
            "bAutoWidth": false,
            "bPaginate": false, // Disable: Next and Previous page buttons
            // "bSortClasses": false, // Disable: Sort column Highlighting
            //"aaSorting": [[7, "desc"]] // Sort by creation date by default
            "aaSorting": [[1, "desc"]] // Sort by creation date by default
        });
        $("#tmnt-info").toggle();     
    }

    //------------------------------------------------------------------------------------
    // Toggle the text displayed on the button which hides/shows treatment information.
    //------------------------------------------------------------------------------------
    function toggleButtonText() {
        var curText = $('.get-tmnt').text();
        var showText = "Retrieve treatment info from EMR";
        var hideText = "Hide treatment info";
        $('.get-tmnt').text(curText == hideText ? showText : hideText);
    }

    //------------------------------------------------------------------------------------
    // Called when the user requests patient information from the EMR (ARIA at MUHC).
    // Populate NSIR-RT patient demographic fields, using EMR data for the patient ID
    // associated with the current investigation. Display message to the user indicating
    // whether or not the query was successful.
    //------------------------------------------------------------------------------------
    $(".get-pat").click(function(){

        var SUCCESS_MESSAGE = "Patient information successfully retrieved from the EMR. Click the Update button to save changes";
        var FAILURE_MESSAGE = "No patient was found in the EMR with matching patient ID";
        var ERROR_MESSAGE = "There was a problem with the query, please contact the system administrator";
        var current_patient_id = $("#id_patient_id").val();

        $.ajax({
            type: 'POST',
            dataType: "json",
            data: { patientID: current_patient_id },
            url: PHP_DIR.concat("queryPatient.php"),
            success: function(mydata) {
                var jsonDict = mydata[0];
                // Successful access of PHP script, but no query result
                if (typeof jsonDict == "undefined") {
                    var alertType = "";
                    ariaMessage(alertType, FAILURE_MESSAGE);
                }
                // Successful query
                else {
                    fillPatFields(jsonDict);
                    var alertType = "alert-success";
                    ariaMessage(alertType, SUCCESS_MESSAGE);
                }
            },
            // Error in accessing PHP script
            error: function(e) {
                var alertType = "alert-error";
                ariaMessage(alertType, ERROR_MESSAGE);
            }
        });
    });

    //------------------------------------------------------------------------------------
    // Fill relevant patient demographic fields using data from EMR.
    //
    // @param {dictionary} fields - Contains key-value pairs for the patient demographic
    // fields. e.g. Date of birth fields and patient gender.
    //------------------------------------------------------------------------------------
    function fillPatFields(fields) {
        $("#id_patient_year_birth").val(fields.DateOfBirth_yyyy);
        $("#id_patient_month_birth").val(fields.DateOfBirth_mm);
        $("#id_patient_gender option").filter(function() {
            return this.text == $.trim(fields.Sex);
        }).attr('selected', true);
        $('select:not(.blocked-field, .reported-field)').trigger("chosen:updated");
    }

    //------------------------------------------------------------------------------------
    // Called when the user requests patient documents from the EMR (ARIA at MUHC).
    // Display a table which lists the documents from the EMR for the patient whose ID is
    // associated with the investigation. Show fields which are presented in the patient
    // manager, and provide a button which links to the document. If the document is not
    // already a PDF, it is converted to one (without affecting the original file) before
    // being served to the user. The PDF document will open in a new browser tab. Display
    // message to the user indicating whether or not the query was successful.
    //------------------------------------------------------------------------------------
    $(".get-docs").click(function(){

        var SUCCESS_MESSAGE = "Documents successfully retrieved from the EMR.";
        var FAILURE_MESSAGE = "No documents were found in the EMR with matching patient ID";
        var ERROR_MESSAGE = "There was a problem with the query, please contact the system administrator";
        var current_patient_id = $("#id_patient_id").val();

        // only call php/query ARIA single time per page load (non-ajax)
        if ($.trim($("#pt-docs").text()) === "" ) {
            $.ajax({
                type: 'POST',
                dataType: "json",
                data: { patientID: current_patient_id },
                url: PHP_DIR.concat("queryDocuments.php"),
                success: function(mydata) {
                    // Successful access of PHP script, but no query result
                    if (mydata.length == 0) {
                        var alertType = "";
                        ariaMessage(alertType, FAILURE_MESSAGE);
                    }
                    // Successful query
                    else {
                        displayDocs(mydata, current_patient_id);
                        toggleDocsButtonText();
                        var alertType = "alert-success";
                        ariaMessage(alertType, SUCCESS_MESSAGE);
                    }
                },
                // Error in accessing PHP script
                error: function(e) {
                    var alertType = "alert-error";
                    ariaMessage(alertType, ERROR_MESSAGE);
                }
            });
        }
        // if already queried on this page load, just toggle display of the table
        else {
            $("#pt-docs").toggle();
            toggleDocsButtonText();
        }
    });

    //------------------------------------------------------------------------------------
    // Prepare the table to display patient/treatment documents. Provide link to that
    // document and display relevant parameters (dates, authors, etc).
    // 
    // @param {array} mydata - An array of dictionaries. Each element is a dictionary
    // representing a particular document. The document dictionary contains relevant
    // parameters such as names and dates, as well as the URL of the document within
    // the EMR database. 
    //
    // @param {string} current_patient_id - ID of the patient assoc. with investigation
    //------------------------------------------------------------------------------------
    function displayDocs(mydata, current_patient_id){
        mydata[0]["FirstName"] = check_and_anonymize(mydata[0]["FirstName"]);
        mydata[0]["LastName"] = check_and_anonymize(mydata[0]["LastName"]);
        // doctext holds the table to display patient documents.
        var doctext = "<h4><center>Documents for " + mydata[0]["FirstName"] + " " + mydata[0]["LastName"] + " (ID:" + current_patient_id + ")</center></h4>";
        doctext += "<table class ='table table-striped docs-table'>";
        doctext += "<thead>";
        doctext += "<tr>";
        doctext += "<th>Document Name</th>";
        doctext += "<th>Author</th>";
        doctext += "<th>Created By</th>";
        doctext += "<th>Signed By</th>";
        doctext += "<th>Date of Service</th>";
        doctext += "<th>Approval Status</th>";
        doctext += "<th>Approved By</th>";
        doctext += "<th>Document Link</th>";
        doctext += "</tr>";
        doctext += "</thead>";
        doctext += "<tbody>";

        // my $documentDirectoryWWW = "/mount/VarianFILEDATA"; # relative to /var/www
        // my $documentDirectory = "/mnt/VarianFILEDATA/Documents/Files";
        // <a href=\"$documentDirectoryWWW/$doc_file_loc\">$doc_file_loc</a>
        for (var i = 0; i < mydata.length; i++) {
            var phpURL = PHP_DIR.concat("downloadPDF.php");
            mydata[i]["Author"] = check_and_anonymize($.trim(mydata[i]["Author"]));
            mydata[i]["CreatedBy"] = check_and_anonymize($.trim(mydata[i]["CreatedBy"]));
            mydata[i]["SignedBy"] = check_and_anonymize($.trim(mydata[i]["SignedBy"]));
            mydata[i]["ApprovedBy"] = check_and_anonymize($.trim(mydata[i]["ApprovedBy"]));
            doctext += "<tr>";
            doctext += "<td>" + mydata[i]["DocName"] + "</td>";
            doctext += "<td>" + mydata[i]["Author"] + "</td>";
            doctext += "<td>" + mydata[i]["CreatedBy"] + "</td>";
            doctext += "<td>" + mydata[i]["SignedBy"] + "</td>";
            doctext += "<td>" + mydata[i]["ServiceDate"] + "</td>";
            doctext += "<td>" + mydata[i]["ApprovalStatus"] + "</td>";
            doctext += "<td>" + mydata[i]["ApprovedBy"] + "</td>";
            // Straight URL: doc only
            // doctext += "<td><a href='" + myURL + "'>" + "Click here to download" + "</a></td>";
            // ajax button: text
            // doctext += "<td><button class='btn btn-primary btn-small doc-link doc-shader'>Click here to download</button></td>";
            // ajax button: explicit
            // doctext += "<td><button class='btn btn-primary btn-small doc-link doc-shader'>" + mydata[i]["URL"] + "</button></td>";
            // form - download file
            //doctext += "<td><form class='form-buttons' method='POST' ACTION='" + phpURL + "'><input type='hidden' name='filename' value='" + mydata[i]["URL"] + "'/><input type='submit' class='btn btn-primary btn-small doc-shader' value='download'></form></td>";
            // form - open in new tab
            doctext += "<td><form target='_blank' class='form-buttons' method='POST' ACTION='" + phpURL + "'><input type='hidden' name='filename' value='" + mydata[i]["URL"] + "'/><input type='submit' class='btn btn-primary btn-small doc-shader' value='view document'></form></td>";
            doctext += "</tr>";
        }

        doctext += "</tbody>";
        doctext += "</table><hr>";

        $("#pt-docs").html(doctext);
        $("#pt-docs").toggle();
        // Convert the table into a jQuery DataTable
        $(".docs-table").DataTable({
            sDom:'<<ir>><<rt>><<p>>',
            iDisplayLength: -1, // Display all rows
            "bInfo": false, // Disable: "Showing x to y of z entries"
            "bPaginate": false, // Disable: Next and Previous page buttons
            //"bSortClasses": false, // Disable: Sort column Highlighting
            "aaSorting": [[4, "desc"]] // Sort by creation date by default
        });
    }

    //------------------------------------------------------------------------------------
    // Toggle the text displayed on the button which hides/shows patient documents table.
    //------------------------------------------------------------------------------------
    function toggleDocsButtonText() {
        var curText = $('.get-docs').text();
        var showText = "Retrieve patient documents from EMR";
        var hideText = "Hide patient documents";
        $('.get-docs').text(curText == hideText ? showText : hideText);
    }

    //------------------------------------------------------------------------------------
    // Called when the user requests journal entries from the EMR (ARIA at MUHC). Display
    // a table which lists the journal entries from the EMR for the patient whose ID is
    // associated with the investigation. Show fields which are presented in the patient
    // manager. Display message to the user indicating whether or not the query was
    // successful.
    //------------------------------------------------------------------------------------
    $(".get-journal").click(function(){

        var SUCCESS_MESSAGE = "Journal entries successfully retrieved from the EMR.";
        var FAILURE_MESSAGE = "No journal entries were found in the EMR with matching patient ID";
        var ERROR_MESSAGE = "There was a problem with the query, please contact the system administrator";
        var current_patient_id = $("#id_patient_id").val();

        // only call php/query ARIA single time per page load (non-ajax)
        if ($.trim($("#pt-journal").text()) === "" ) {
            $.ajax({
                type: 'POST',
                dataType: "json",
                data: { patientID: current_patient_id },
                url: PHP_DIR.concat("queryJournal.php"),
                success: function(mydata) {
                    // Successful access of PHP script, but no query result
                    if (mydata.length == 0) {
                        var alertType = "";
                        ariaMessage(alertType, FAILURE_MESSAGE);
                    }
                    // Successful query
                    else {
                        displayJournal(mydata, current_patient_id);
                        toggleJournalButtonText();
                        var alertType = "alert-success";
                        ariaMessage(alertType, SUCCESS_MESSAGE);
                    }
                },
                // Error in accessing PHP script
                error: function(e) {
                    var alertType = "alert-error";
                    ariaMessage(alertType, ERROR_MESSAGE);
                }
            });
        }
        // if already queried on this page load, just toggle display of the table
        else {
            $("#pt-journal").toggle();
            toggleJournalButtonText();
        }
    });

    //------------------------------------------------------------------------------------
    // Prepare the table to display journal entries for a patient.
    // 
    // @param {array} mydata - An array of dictionaries. Each element is a dictionary
    // representing a particular journal entry. The document dictionary contains relevant
    // parameters such as names and dates, as well as the journal entry itself.
    //
    // @param {string} current_patient_id - ID of the patient assoc. with investigation
    //------------------------------------------------------------------------------------
    function displayJournal(mydata, current_patient_id){
        mydata[0]["PatFirstName"] = check_and_anonymize(mydata[0]["PatFirstName"]);
        mydata[0]["PatLastName"] = check_and_anonymize(mydata[0]["PatLastName"]);
        // jourtext holds the table to display journal entries
        var jourtext = "<h4><center>Journal Entries for " + mydata[0]["PatFirstName"] + " " + mydata[0]["PatLastName"] + " (ID:" + current_patient_id + ")</center></h4>";
        jourtext += "<table class ='table table-striped journal-table'>";
        jourtext += "<thead>";
        jourtext += "<tr>";
        jourtext += "<th>Date/Time</th>";
        jourtext += "<th>Authored By</th>";
        jourtext += "<th>Status</th>";
        jourtext += "<th>Journal Entry</th>";
        jourtext += "</tr>";
        jourtext += "</thead>";
        jourtext += "<tbody>";

        for (var i = 0; i < mydata.length; i++) {
            mydata[i]["AuthFirstName"] = check_and_anonymize($.trim(mydata[i]["AuthFirstName"]));
            mydata[i]["AuthLastName"] = check_and_anonymize($.trim(mydata[i]["AuthLastName"]));
            // Need to remove extra spaces in date format for proper sorting
            mydata[i]["CreationDate"] = mydata[i]["CreationDate"].replace(/\s\s+/g, ' ');
            jourtext += "<tr>";
            jourtext += "<td>" + mydata[i]["CreationDate"] + "</td>";
            jourtext += "<td>" + mydata[i]["AuthFirstName"] + " " + mydata[i]["AuthLastName"] + "</td>";
            jourtext += "<td>" + mydata[i]["ApprovalStatus"] + "</td>";
            jourtext += "<td>" + mydata[i]["NoteText"] + "</td>";
            jourtext += "</tr>";
        }

        jourtext += "</tbody>";
        jourtext += "</table><hr>";

        $("#pt-journal").html(jourtext);
        $("#pt-journal").toggle();
        // Convert the table into a jQuery DataTable
        // Required for date sorting:
        $.fn.dataTable.moment( 'MMM D YYYY h:mmA' );
        $(".journal-table").DataTable({
            sDom:'<<ir>><<rt>><<p>>',
            iDisplayLength: -1, // Display all rows
            "aoColumns": [
            { "sWidth": "18%" },
            { "sWidth": "15%" },
            { "sWidth": "13%" },
            { "sWidth": "54%" },
            ],
            "bInfo": false, // Disable: "Showing x to y of z entries"
            "bPaginate": false, // Disable: Next and Previous page buttons
            // "bSortClasses": true, // Disable: Sort column Highlighting
            "aaSorting": [[0, "desc"]] // Sort by creation date by default
        });
    }

    //------------------------------------------------------------------------------------
    // Toggle the text displayed on the button which hides/shows journal entries table.
    //------------------------------------------------------------------------------------
    function toggleJournalButtonText() {
        var curText = $('.get-journal').text();
        var showText = "Retrieve journal entries from EMR";
        var hideText = "Hide journal entries";
        $('.get-journal').text(curText == hideText ? showText : hideText);
    }

    //------------------------------------------------------------------------------------
    // Called when the user requests patient alerts from the EMR (ARIA at MUHC). Display a
    // table which lists the alerts from the EMR for the patient whose ID is associated
    // with the investigation. Show fields which are presented in the patient manager.
    // Display message to the user indicating whether or not the query was successful.
    //------------------------------------------------------------------------------------
    $(".get-alerts").click(function(){

        var SUCCESS_MESSAGE = "Patient alerts successfully retrieved from the EMR.";
        var FAILURE_MESSAGE = "No patient alerts were found in the EMR with matching patient ID";
        var ERROR_MESSAGE = "There was a problem with the query, please contact the system administrator";
        var current_patient_id = $("#id_patient_id").val();

        // only call php/query ARIA single time per page load (non-ajax)
        if ($.trim($("#pt-alerts").text()) === "" ) {
            $.ajax({
                type: 'POST',
                dataType: "json",
                data: { patientID: current_patient_id },
                url: PHP_DIR.concat("queryAlerts.php"),
                success: function(mydata) {
                    // Successful access of PHP script, but no query result
                    if (mydata.length == 0) {
                        var alertType = "";
                        ariaMessage(alertType, FAILURE_MESSAGE);
                    }
                    // Successful query
                    else {
                        displayAlerts(mydata, current_patient_id);
                        toggleAlertButtonText();
                        var alertType = "alert-success";
                        ariaMessage(alertType, SUCCESS_MESSAGE);
                    }
                },
                // Error in accessing PHP script
                error: function(e) {
                    var alertType = "alert-error";
                    ariaMessage(alertType, ERROR_MESSAGE);
                }
            });
        }
        // if already queried on this page load, just toggle display of the table
        else {
            $("#pt-alerts").toggle();
            toggleAlertButtonText();
        }
    });

    //------------------------------------------------------------------------------------
    // Prepare the table to display patient alerts for a particular patient.
    // 
    // @param {array} mydata - An array of dictionaries. Each element is a dictionary
    // representing a particular patient alert. The document dictionary contains relevant
    // parameters such as names and dates, as well as the alert text.
    //
    // @param {string} current_patient_id - ID of the patient assoc. with investigation
    //------------------------------------------------------------------------------------
    function displayAlerts(mydata, current_patient_id){
        mydata[0]["PatFirstName"] = check_and_anonymize(mydata[0]["PatFirstName"]);
        mydata[0]["PatLastName"] = check_and_anonymize(mydata[0]["PatLastName"]);
        // alerttext holds the table to display journal entries
        var alerttext = "<h4><center>Patient Alerts for " + mydata[0]["PatFirstName"] + " " + mydata[0]["PatLastName"] + " (ID:" + current_patient_id + ")</center></h4>";
        alerttext += "<table class ='table table-striped alert-table'>";
        alerttext += "<thead>";
        alerttext += "<tr>";
        alerttext += "<th>Hidden</th>";
        alerttext += "<th>Signed Off</th>";
        alerttext += "<th>Display Date</th>";
        alerttext += "<th>Patient Alert</th>";
        alerttext += "<th>Created By</th>";
        alerttext += "<th>Signed Off By</th>";
        alerttext += "<th>Signed Off Date</th>";
        alerttext += "</tr>";
        alerttext += "</thead>";
        alerttext += "<tbody>";

        //Fill the table
        for (var i = 0; i < mydata.length; i++) {
            mydata[i]["AuthUsername"] = check_and_anonymize($.trim(mydata[i]["AuthUsername"]));
            mydata[i]["SignedOffBy"] = check_and_anonymize($.trim(mydata[i]["SignedOffBy"]));

            mydata[i]["DisplayDate"] = mydata[i]["DisplayDate"].replace(/\s\s+/g, ' ');
            mydata[i]["SignedOffDate"] = mydata[i]["SignedOffDate"].replace(/\s\s+/g, ' ');
            alerttext += "<tr>";
            // Hidden column to govern sorting of the next column:
            alerttext += "<td>" + mydata[i]["SignedOffStatus"] + "</td>";
            // Column which displays icon indicative of sign off status
            if (mydata[i]["SignedOffStatus"] == "Signed"){
                alerttext += "<td style='text-align:center'><i class='icon-check-sign green_check'></i></td>";
            }
            else {
                alerttext += "<td></td>";
            }
            alerttext += "<td>" + mydata[i]["DisplayDate"] + "</td>";
            alerttext += "<td>" + mydata[i]["AlertText"] + "</td>";
            alerttext += "<td>" + mydata[i]["AuthUsername"] + "</td>";
            alerttext += "<td>" + mydata[i]["SignedOffBy"] + "</td>";
            alerttext += "<td>" + mydata[i]["SignedOffDate"] + "</td>";
            alerttext += "</tr>";
        }

        alerttext += "</tbody>";
        alerttext += "</table><hr>";

        $("#pt-alerts").html(alerttext);
        $("#pt-alerts").toggle();
        // Convert the table into a jQuery DataTable:
        // Required for date sorting plugin:
        $.fn.dataTable.moment( 'MMM D YYYY h:mmA' );
        $(".alert-table").DataTable({
            sDom:'<<ir>><<rt>><<p>>',
            iDisplayLength: -1, // Display all rows
            "aoColumns": [
            { "bVisible": false }, // don't display
            { "sWidth": "11%", "iDataSort": 0 }, // sort based on prev column
            { "sWidth": "16%" },
            { "sWidth": "33%" },
            { "sWidth": "11%" },
            { "sWidth": "13%" },
            { "sWidth": "16%" },
            ],
            "bInfo": false, // Disable: "Showing x to y of z entries"
            "bPaginate": false, // Disable: Next and Previous page buttons
            //"bSortClasses": false, // Disable: Sort column Highlighting
            "aaSorting": [[2, "desc"]] // Sort by creation date by default
        });
    }

    //------------------------------------------------------------------------------------
    // Toggle the text displayed on the button which hides/shows patient alerts table.
    //------------------------------------------------------------------------------------
    function toggleAlertButtonText() {
        var curText = $('.get-alerts').text();
        var showText = "Retrieve patient alerts from EMR";
        var hideText = "Hide patient alerts";
        $('.get-alerts').text(curText == hideText ? showText : hideText);
    }

    //------------------------------------------------------------------------------------
    // Display an ajax message to the user which indicates whether or not a query to
    // the EMR (ARIA at MUCH) was successful.
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
        // $("#floating-status-message").remove();
        // $(".ajax_messages").append("<div class='message-div alert " + alertType + " style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        // $(".alert").slideDown();

        var $message = $("<div class='floating-message-div alert " + alertType + " style='width:96%'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        $('.navbar').append($message);
         setTimeout(function() {
             $message.remove();
         }, duration)
    }

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

    //====================================================================================
    // The following all involve toggling hidden/displayed sections of the page (i.e.
    // can choose to hide/show the fields assoicated with a particular section of the
    // investigation form. 
    //====================================================================================
    // $("#-head").click(function(){
    //     $("#-form-wrapper").slideToggle('fast');
    //     $("#-plus").toggle();
    //     $("#-minus").toggle();
    // });

    $("#comments-head").click(function(){
        $("#comments-form-wrapper").slideToggle('fast');
        $("#comments-plus").toggle();
        $("#comments-minus").toggle();
    });

    $("#local-head").click(function(){
        $("#local-form-wrapper").slideToggle('fast');
        $("#local-plus").toggle();
        $("#local-minus").toggle();
    });

    $("#investigator-head").click(function(){
        $("#investigator-form-wrapper").slideToggle('fast');
        $("#investigator-plus").toggle();
        $("#investigator-minus").toggle();
    });

    $("#support-head").click(function(){
        $("#support-form-wrapper").slideToggle('fast');
        $("#support-plus").toggle();
        $("#support-minus").toggle();
        $('select:not(.blocked-field, .reported-field)').chosen({search_contains:true, width:'100%'});
    });

    $("#impact-head").click(function(){
        $("#impact-form-wrapper").slideToggle('fast');
        $("#impact-plus").toggle();
        $("#impact-minus").toggle();
    });

    $("#discovery-head").click(function(){
        $("#discovery-form-wrapper").slideToggle('fast');
        $("#discovery-plus").toggle();
        $("#discovery-minus").toggle();
    });

    $("#patient-head").click(function(){
        $("#patient-form-wrapper").slideToggle('fast');
        $("#patient-plus").toggle();
        $("#patient-minus").toggle();
    });

    $("#details-head").click(function(){
        $("#details-form-wrapper").slideToggle('fast');
        $("#details-plus").toggle();
        $("#details-minus").toggle();
    });

    $("#treatment-head").click(function(){
        $("#treatment-form-wrapper").slideToggle('fast');
        $("#treatment-plus").toggle();
        $("#treatment-minus").toggle();
    });

    $("#investigation-head").click(function(){
        $("#investigation-form-wrapper").slideToggle('fast');
        $("#investigation-plus").toggle();
        $("#investigation-minus").toggle();
    });

    $("#actions-head").click(function(){
        $("#actions-form-wrapper").slideToggle('fast');
        $("#actions-plus").toggle();
        $("#actions-minus").toggle();
    });

    //====================================================================================
    // Various settings, etc
    //====================================================================================
    // To enable page navigation confirmations, uncomment the following:
    // $('form').areYouSure(
    //     {'message':'Ensure that you have saved any desired changes before navigating away from this page!'}
    // );

    $(document).on('focus', 'input, select, textarea', function(){
        $('.ils-popover').popover({
               trigger:'manual',
               animation:false,
               delay:0,
               html:true,
        });
        $(".ils-popover").popover('hide');
        $(this).parents(".ils-popover").popover("show");
    });
    $(document).on('blur', 'input, select, textarea', function(){
        $(".ils-popover").popover('hide');
    });

    // On fields that are blocked from updates, prevent showing options and do not allow
    // field change; but trigger focus so display tooltip
    $("#investigation-form").on('mousedown keypress', '.blocked-field, .reported-field', function(event){
        event.preventDefault();
        $(this).focus();
    });
    $("#investigation-form").on('click', 'input:checkbox.blocked-field', function(event){
        event.preventDefault();
        $(this).focus();
    });
    $("#investigation-form").on('click', '.chosen-container', function(event){
        if ($(this).prev().hasClass('reported-field')) {
            event.preventDefault();
            event.stopPropagation();
            // $(this).children().slice(1).hide();
        }
    });

    $("#set_of_forms").on('mousedown keypress', '.action-responsible', function(event){
        event.preventDefault();
        $(this).focus();
    });
    $("#set_of_forms").on('click', 'input:checkbox.blocked-action-field', function(event){
        event.preventDefault();
        $(this).focus();
    });

    $(".datepicker").datepicker({
        format: 'yyyy-mm-dd',
    });

    $(".red_flags").on('click', function(event){
        var message = "";
        var alertType = "alert-success";
        if ($("#id_flag").is(':checked')) {
            $("#id_flag").prop('checked',false);
            message = "Please save changes: Incident no longer flagged for discussion.";
        }
        else {
            $("#id_flag").prop('checked',true);
            message = "Please save changes: Incident flagged for discussion.";
        }
        $("#id_flag").trigger('change');
        ariaMessage(alertType, message);
    });

    //------------------------------------------------------------------------------------
    // Handle sticky-ing the confirm template creation button as user scrolls down page to
    // review the fields which should be saved in the template.
    //------------------------------------------------------------------------------------
    $(window).scroll(function(e){ 
      var $el = $('#confirm-template-button'); 
      var isPositionFixed = ($el.css('position') == 'fixed');
      if ($(this).scrollTop() > 400 && !isPositionFixed){ 
        $('#confirm-template-button').css({'position': 'fixed', 'top': '50px'}); 
      }
      if ($(this).scrollTop() < 400 && isPositionFixed)
      {
        $('#confirm-template-button').css({'position': 'static', 'top': '50px'}); 
      } 
    });

    //====================================================================================
    // Listeners to adapt which form fields are visible, and what values they hold based
    // on what is entered in other form fields. 
    //====================================================================================
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
    // }).trigger('change');

    $("#id_flag").change(function(){
        $("i",".incident-flag").toggleClass("icon-flag icon-flag-alt");
        var flag_key = $("#id_flag").prop('checked');
        var discussion_key = $("#id_discussion").prop('checked');
        if (flag_key == true){
            $("#hide-id_discussion").slideDown();
        }
        else {
            $("#hide-id_discussion").slideUp();
            if (discussion_key == true) {
                $("#id_discussion").prop('checked',false);
                $("i",".incident-discussion").toggleClass("icon-comment fa-fw");
            }
        }
    });

    $("#id_discussion").change(function(){
        $("i",".incident-discussion").toggleClass("icon-comment fa-fw");
        var discussion_key = $("#id_discussion").prop('checked');
        var flag_key = $("#id_flag").prop('checked');
        if (discussion_key == true && flag_key == true){
            $("#id_flag").prop('checked',false);
            $("i",".incident-flag").toggleClass("icon-flag icon-flag-alt");
        }
    });

    // Slide up description performed field on incomplete actions
    // need to use 'on' behaviour to handle dynamically-added elements
    //$(".action-complete").change(function(){
    // $("#set_of_forms").on('change', '.action-complete', function(){
    //     var complete_id = $(this).attr('id');
    //     // Need condidtional to prevent attempting this on the blank form
    //     if (!(complete_id.indexOf("__prefix__") >= 0)) {
    //         var form_id = complete_id.match(/\d/g)[0];
    //         if ($(this).prop('checked')){
    //             $("#hide-id_form-"+form_id+"-description_performed").slideDown();
    //         }
    //         else {
    //             $("#hide-id_form-"+form_id+"-description_performed").slideUp();
    //             $("#id_form-"+form_id+"-description_performed").val(null);
    //         }
    //     }

    // }).trigger('change');
    // $(".action-complete").trigger('change'); 
});
