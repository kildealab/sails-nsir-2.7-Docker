"use strict";

$(document).ready(function(){
    $('select').chosen({search_contains:true, width:'45%'});
    var num_plots = 0;
    //------------------------------------------------------------------------------------
    // Function which is called upon attempting to generate a new plot. POSTs statistics
    // form data to the view, and receives relevant JSON data from the view. Handle the
    // cases where there are form errors, erroneous data, or successful POSTing. Calls
    // relevant functions to add a new chart container and plot the desired chart.
    //------------------------------------------------------------------------------------
    $(".generate-plot").click(function(){
        $.ajax({
            url: "/nsir/statistics/",
            method:"POST",
            data: $("#statistics-form").serialize(),
            success: function(json_data){
                // Form errors
                if (json_data.errors) {
                    applyErrors(json_data.errors);
                }
                // Selection errors
                else if (json_data.error_message) {
                    var alertType = "alert-error";
                    displayMessage(alertType, json_data.error_message);
                }
                else {
                    removeMessages();
                    removeErrors();
                    addChartContainer();
                    if (json_data.plot_type == "column") {
                        setColumnChartOptions(json_data);
                    }
                    else if (json_data.plot_type == "unstacked") {
                        setUnstackedChartOptions(json_data);
                    }
                    else if (json_data.plot_type == "pie") {
                        setPieChartOptions(json_data);
                    }
                }
            },
            error: function(e){
            }
        });
        return false;
    });

    //------------------------------------------------------------------------------------
    // Function which creates a new plot container, using an existing hidden/blank
    // container. Uses a global variable 'num_plots' to determine the id of the next
    // container to be generated. The new container is inserted after the form.
    //------------------------------------------------------------------------------------
    function addChartContainer() {
        num_plots += 1;
        var $newdiv = $('#row-__id__').clone();
        $newdiv.html($newdiv.html().replace(/__id__/g, num_plots));
        var new_id = $newdiv.attr('id').replace(/__id__/g, num_plots);
        $newdiv.attr("id",new_id);
        $newdiv.insertAfter('#row-form');
        $newdiv.show();
    }

    //------------------------------------------------------------------------------------
    // Function used to create the desired column chart. Uses an existing highcharts
    // settings variable for column charts, and modifies appropriate settings based on
    // JSON data passed to the function.
    // @param {dictionary} json_data - Contains information passed from the view.
    // Relevant keys:
    //  {string} plot_type - Type of plot to be generated ('column')
    //  {string} single_choice - If a single choice was to be plotted, rather than 'All',
    //      this will hold the string representing that choice
    //  {string} complete_label - e.g. 'All Valid Incidents' or 'Complete Incidents'
    //  {string} query_model_title - The model to be plotted e.g. 'Event Type'
    //  {string} date_label - The date type used in binning e.g. 'Date Incident Submitted'
    //  {array} date_range - Array of strings representing the date bins
    //  {array} series - actual binned/filtered incident data formatted for highcharts
    //------------------------------------------------------------------------------------
    function setColumnChartOptions(json_data) {
        var chart_type_jq = json_data.plot_type;
        var y_label_jq = 'Number of Incidents';

        var chart_title;
        var new_chart_options = chart_options;
        if (json_data.single_choice != null) {
            chart_title = json_data.complete_label + " (" + json_data.query_model_title + ": " + json_data.single_choice +") [N=" + json_data.num_incidents + "]";
            new_chart_options.legend.enabled = true;
            new_chart_options.legend.draggable = true;
        }
        else {
            chart_title = json_data.complete_label + " by " + json_data.query_model_title + " [N=" + json_data.num_incidents + "]";
            new_chart_options.legend.enabled = true;
            new_chart_options.legend.draggable = true;
        }

        new_chart_options.chart.type = chart_type_jq;
        new_chart_options.chart.renderTo = 'plot-container-' + num_plots;
        new_chart_options.title.text = chart_title;
        new_chart_options.xAxis.title.text = json_data.date_label;
        new_chart_options.xAxis.categories = json_data.date_range;
        new_chart_options.yAxis.title.text = y_label_jq;
        new_chart_options.series = json_data.series_array;

        var chartnew = new Highcharts.Chart(new_chart_options);

        $("#single-color-"+num_plots).hide();
    }

    //------------------------------------------------------------------------------------
    // Function used to create the desired unstacked column chart. Uses an existing 
    // highcharts settings variable for column charts, and modifies appropriate settings 
    // based on JSON data passed to the function.
    // @param {dictionary} json_data - Contains information passed from the view.
    // Relevant keys:
    //  {string} plot_type - Type of plot to be generated ('column')
    //  {string} single_choice - If a single choice was to be plotted, rather than 'All',
    //      this will hold the string representing that choice
    //  {string} complete_label - e.g. 'All Valid Incidents' or 'Complete Incidents'
    //  {string} query_model_title - The model to be plotted e.g. 'Event Type'
    //  {string} date_label - The date type used in binning e.g. 'Date Incident Submitted'
    //  {array} date_range - Array of strings representing the type bins (NOT ACTUALLY
    //      DATES!)
    //  {array} series - actual binned/filtered incident data formatted for highcharts
    //------------------------------------------------------------------------------------
    function setUnstackedChartOptions(json_data) {
        var chart_type_jq = 'column';
        var y_label_jq = 'Number of Incidents';

        var chart_title;
        var new_chart_options = unstacked_options;
        if (json_data.single_choice != null) {
            chart_title = json_data.complete_label + " (" + json_data.query_model_title + ": " + json_data.single_choice +") [N=" + json_data.num_incidents + "]";
        }
        else {
            chart_title = json_data.complete_label + " by " + json_data.query_model_title + " [N=" + json_data.num_incidents + "]";
        }

        new_chart_options.chart.type = chart_type_jq;
        new_chart_options.chart.renderTo = 'plot-container-' + num_plots;
        new_chart_options.title.text = chart_title;
        new_chart_options.xAxis.title.text = json_data.query_model_title;
        new_chart_options.xAxis.categories = json_data.date_range;
        new_chart_options.yAxis.title.text = y_label_jq;
        new_chart_options.series = json_data.series_array;

        var chartnew = new Highcharts.Chart(new_chart_options);

        $("#float-legend-"+num_plots).hide();
        $("#display-legend-"+num_plots).hide();
    }

    //------------------------------------------------------------------------------------
    // Function used to create the desired pie chart. Uses an existing highcharts
    // settings variable for pie charts, and modifies appropriate settings based on
    // JSON data passed to the function.
    // @param {dictionary} json_data - Contains information passed from the view.
    // Relevant keys:
    //  {string} plot_type - Type of plot to be generated ('pie')
    //  {string} single_choice - If a single choice was to be plotted, rather than 'All',
    //      this will hold the string representing that choice
    //  {string} complete_label - e.g. 'All Valid Incidents' or 'Complete Incidents'
    //  {string} query_model_title - The model to be plotted e.g. 'Event Type'
    //  {array} series - actual binned/filtered incident data formatted for highcharts
    //------------------------------------------------------------------------------------
    function setPieChartOptions(json_data) {
        var chart_type_jq = json_data.plot_type;
        var y_label_jq = 'Number of Incidents';

        var chart_title;
        var new_chart_options = pie_chart_options;
        if (json_data.single_choice != null) {
            chart_title = json_data.complete_label + " (" + json_data.query_model_title + ": " + json_data.single_choice +") [N=" + json_data.num_incidents + "]";
        }
        else {
            chart_title = json_data.complete_label + " by " + json_data.query_model_title + " [N=" + json_data.num_incidents + "]";
        }

        new_chart_options.chart.type = chart_type_jq;
        new_chart_options.chart.renderTo = 'plot-container-' + num_plots;
        new_chart_options.title.text = chart_title;
        new_chart_options.yAxis.title.text = "Y AXIS";
        new_chart_options.series = json_data.series_array;

        var chartnew = new Highcharts.Chart(new_chart_options);

        //Hide/display relevant buttons
        $("#remove-date-"+num_plots).show();
        $("#display-labels-"+num_plots).show();
        $("#float-legend-"+num_plots).hide();
        $("#single-color-"+num_plots).hide();
    }

    var chart_type = 'column';

    //====================================================================================
    // Default options (template) used for generating stacked/date-binned column charts.
    //====================================================================================
    var chart_options = {
        // Taken from:
        // http://tools.medialab.sciences-po.fr/iwanthue/
        // 20 color palette, hard(Force Vector)
        // Old colors:
        // colors: ['#27AED5','#8FD31E','#CF6FFC','#6BE04B','#DE52D1',
        //     '#16B661','#D0338A','#1CBC8A','#F65262','#6073E0',
        //     '#D3C247','#3E62A8','#F7983F','#B8A2F0','#73880B',
        //     '#B0B6EC','#776721','#9D96C5','#B14046','#217C8D'],
        colors: [
        '#77C4E8','#2FC826','#AA38C9','#EB696D','#386EA6',
        '#8BC726','#3ADCC6','#FE4CA6','#EDE478','#C8A67A',
        '#7FB279','#5280E9','#D58CD5','#4F8F8F','#FFD3AC',
        '#FE8E67'
        ],
        chart: {
            renderTo: 'plot-container',
            type: chart_type,
            // Use the following if want to display only those options which have counts
            events: {
                load: function () {
                    var chart = this;
                    $.each(chart.series,function(i,serie) {
                        function getSum(total, num) {
                            return total + num;
                        }
                        var current_data = serie.yData;
                        if(current_data.reduce(getSum) == 0) {
                            serie.update({
                                showInLegend:false
                            });
                        }
                    });
                }
            }
        },
        title: {
            text: "",
            style: {
                fontSize:'25px',
                fontWeight: 'bold'
            },
            name: "",
        },
        xAxis: {
            title: {
                text: "",
                style: {
                    fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            labels: {
                style: {
                    fontSize:'18px'
                }
            }
        },
        yAxis: {
            title: {
                text: "",
                style: {
                    fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontSize:'15px',
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            },
            labels: {
                style: {
                    fontSize:'18px'
                }
            },
            minTickInterval: 1,
            allowDecimals: false,
        },
        legend: {
            //Truncate the legend text
            //May change to setting max width, and wrap the text?
            labelFormatter: function() {
                // do truncation here and return string
                // this.name holds the whole label
                // for example:
                if (this.name.length > 60) {
                    return this.name.slice(0, 60)+'...'
                }
                else {
                    return this.name
                }

                // if (this.x == 0) return '<h3><u>'+this.series.name+'</u></h3>' + this.name + ' (' + this.fraction + ')';
                // else return this.name + ' (' + this.fraction + ')';

            },
            layout: 'vertical',
            align: 'right',
            // verticalAlign: 'middle',
            // x: 130,
            verticalAlign: 'top',
            // y: 90,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false,
            draggable: true,
            itemStyle: {
                fontSize:'18px'
            }
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Monthly Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    // Remove data labels for 0 counts
                    formatter:function() {
                        if(this.y != 0) {
                            return this.y;
                        }
                    },
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            },
            series: {
                point: {
                    events: {
                        click: function () {
                            produceIncidentTable(this, "column");
                        }
                    }
                }
            },
        },
        series: [],
        // Remove watermark from bottom
        credits: {
            enabled: false
        }
    };

    //====================================================================================
    // Default options (template) used for generating unstacked column charts.
    //====================================================================================
    var unstacked_options = {
        chart: {
            renderTo: 'plot-container',
            type: chart_type,
            // Use the following if want to display only those options which have counts
            events: {
                load: function () {
                    var chart = this;
                    $.each(chart.series,function(i,serie) {
                        function getSum(total, num) {
                            return total + num;
                        }
                        var current_data = serie.yData;

                        if(current_data.length > 0 && current_data.reduce(getSum) == 0) {
                            serie.update({
                                showInLegend:false
                            });
                        }
                    });
                }
            }
        },
        title: {
            text: "",
            style: {
                fontSize:'25px',
                fontWeight: 'bold'
            }
        },
        xAxis: {
            title: {
                text: "",
                style: {
                    fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            labels: {
                // rotation: -45,
                style: {
                    fontSize:'14px'
                }
            }
        },
        yAxis: {
            title: {
                text: "",
                style: {
                    fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontSize:'15px',
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            },
            labels: {
                style: {
                    fontSize:'18px'
                }
            },
            minTickInterval: 1,
            allowDecimals: false,
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: 'Count: {point.y}/{point.series.options.num_incidents} ({point.fraction})'
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true,
                    // Remove data labels for 0 counts
                    formatter:function() {
                        if(this.y != 0) {
                            return this.y;
                        }
                    },
                    color: "#333",
                    style: {"fontSize": "18px"},
                }
            },
            series: {
                point: {
                    events: {
                        click: function () {
                            produceIncidentTable(this, "unstacked");
                        }
                    }
                }
            }
        },
        series: [],
        // Remove watermark from bottom
        credits: {
            enabled: false
        }
    };

    //====================================================================================
    // Default options (template) used for generating pie charts.
    //====================================================================================
    var pie_chart_options = {
        // Taken from:
        // http://tools.medialab.sciences-po.fr/iwanthue/
        // 20 color palette, hard(Force Vector)
        // colors: ['#27AED5','#8FD31E','#CF6FFC','#6BE04B','#DE52D1',
        //     '#16B661','#D0338A','#1CBC8A','#F65262','#6073E0',
        //     '#D3C247','#3E62A8','#F7983F','#B8A2F0','#73880B',
        //     '#B0B6EC','#776721','#9D96C5','#B14046','#217C8D'],
        chart: {
            renderTo: 'plot-container',
            type: 'pie',
        },
        title: {
            text: "",
            style: {
                fontSize:'25px',
                fontWeight: 'bold'
            }
        },
        yAxis: {
            title: {
                text: "",
                style: {
                    fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            labels: {
                style: {
                    fontSize:'18px'
                }
            },
        },
        tooltip: {
            headerFormat: '',
            pointFormat: '<b>{point.name}:</b><br> {point.y}/{point.series.options.num_incidents} ({point.fraction})',
        },
        plotOptions: {
            pie: {
                dataLabels: {
                    enabled: true,
                    // Remove data labels for 0 counts
                    formatter:function() {
                        if(this.y != 0 && this.series.name != "Date Bins") {
                            // Or this.point.y or this.point.fraction
                            // return this.point.name;
                            return this.point.y;
                        }
                    },
                    distance: -100,
                    color: "#ffffff",
                    style: {
                        fontSize: "19px"
                    }
                },
                showInLegend: true,
                events: {
                    legendItemClick: function () {
                        return false; 
                    }
                },
            },
            series: {
                point: {
                    events: {
                        // If the dates have been removed, allow clicking legend elements
                        legendItemClick: function () {
                            if (this.series.chart.series.length == 1) {
                                return true;
                            }
                            // If only plotting one paramter, allow clicking too
                            else if (this.series.chart.series[0].yData.length == 1) {
                                return true;
                            }
                            else {
                                return false;
                            }
                        },
                        click: function () {
                            produceIncidentTable(this, "pie");
                        }
                    }
                }
            },
        },
        legend: {
            align: 'right',
            layout: 'vertical',
            verticalAlign: 'top',
            x: -30,
            y: 130,
            labelFormatter: function () {
                if (this.series.name != "Date Bins") {
                    // if (this.x == 0) return '<h3><u>'+this.series.name+'</u></h3>' + this.name + ' (' + this.fraction + ')';
                    // else return this.name + ' (' + this.fraction + ')';
                    if (this.x == 0) return '<h3><u>'+this.series.name+'</u></h3>' + this.name;
                    else return this.name;
                }
                else {
                    if (this.x == 0) return '<h3>'+this.series.name+'</h3>' + this.name;
                    else return this.name;
                }
            },
            useHTML: true,
            itemStyle: {
                fontSize:'19px'
            }
            // itemMarginTop: 5,
            // itemMarginBottom: 5
        },
        series: [],
        // Remove watermark from bottom
        credits: {
            enabled: false
        },
        // exporting: {
        //     sourceWidth: 1000,
        //     sourceHeight: 400,
        // },
    }

    //------------------------------------------------------------------------------------
    // Produce a table of incidents based on the section of a highcharts plot that was
    // clicked. 
    //
    // @param {dictionary} point - A dictionary representing a data point on a highcharts
    //      plot. 
    // @param {string} chart_type - Indicates what type of chart is being generated;
    //      required for proper table title formatting.
    //------------------------------------------------------------------------------------
    function produceIncidentTable (point, chart_type) {
        var arr = point.series.chart.renderTo.id.split('-');
        var chart_id = arr[arr.length-1]; //This is the ID number of the chart
        var table_id = "#table-div-" + chart_id;

        // Generate a title for the table based on the point which was selected
        var table_title = ""
        if (chart_type == "column") {
            var type = point.series.name;
            var xbin = point.series.xAxis.categories[point.x];
            var title = point.series.chart.title.textStr;
            if (point.year == null) {
                table_title = title + ": " + type + " [" + xbin + "]";
            }
            else {
                table_title = title + ": " + type + " [" + xbin + ", " + point.year + "]";
            }
        }
        else if (chart_type == "unstacked") {
            var xbin = point.series.xAxis.categories[point.x];
            var title = point.series.chart.title.textStr;
            table_title = title + ": " + xbin;
        }
        else if (chart_type == "pie") {
            var title = point.series.chart.title.textStr;
            if (point.year == null) {
                var type = point.name;
                table_title = title + ": " + type;
            }
            else {
                var type = point.series_name;
                var xbin = point.name;
                table_title = title + ": " + type + " [" + xbin + ", " + point.year + "]";
            }
        }

        // Create an HTML table and column headers.
        var mytable = "<div class='table-title' style='color:"+point.color+"'>" + table_title + "</div>";
        mytable += "<br>";
        mytable += "<table id='inc-table-"+chart_id+"' class='table table-striped inc-table'>";
        mytable += "<thead>";
        mytable += "<tr>";
        mytable += "<th>Incident ID</th>";
        mytable += "<th>Description</th>";
        mytable += "<th>Investigator</th>";
        mytable += "<th>Oncologist</th>";
        mytable += "<th>Date Incident Detected</th>";
        mytable += "<th>Event Type</th>";
        mytable += "<th>Completion Status</th>";
        mytable += "</tr>";
        mytable += "</thead>";
        mytable += "<tbody>";

        // Fill the table with incident data contained in the data point that was passed
        // to this function
        for (var i=0;i<point.ids.length;i++) {
            // Create a URL to link to the incident investigation
            var temp = url_path.split('/');
            temp[temp.length-2] = point.ids[i];
            temp = temp.join('/');
            // var inc_url = url_host+temp;
            var inc_url = temp;

            mytable += "<tr>";
            mytable += "<td><a href='"+inc_url+"' target='_blank'>" + point.ids[i] + "</a></td>";
            mytable += "<td>" + point.descs[i] + "</td>";
            mytable += "<td>" + point.invs[i] + "</td>";
            mytable += "<td>" + point.oncs[i] + "</td>";
            mytable += "<td>" + point.datedec[i] + "</td>";
            mytable += "<td>" + point.etypes[i] + "</td>";

            // Completion status icons
            if (point.compstatus[i]) {
                mytable += "<td>" + "<span class='status_text pull-left label inv_color_complete' style='margin-left: 10px;'>Complete</span>" + "</td>";
            }
            else {
                mytable += "<td>" + "<span class='status_text pull-left label inv_color_incomplete' style='margin-left: 10px;'>Incomplete</span>" + "</td>";
            }
            mytable += "</tr>";
        }
        mytable += "</tbody>";
        mytable += "</table>";

        $(table_id).html(mytable);
        if($(table_id+':visible').length == 0) {
            $(table_id).toggle();
        }

        // Convert into a DataTable, sort by date
        $("#inc-table-"+chart_id).DataTable({
            sDom:'<"top">rt<"bottom"ifp><"clear">',
            iDisplayLength: 10, // Display all rows
            "bInfo": true, // Disable: "Showing x to y of z entries"
            "bPaginate": true, // Disable: Next and Previous page buttons
            "bFilter": false,
            //"bSortClasses": false, // Disable: Sort column Highlighting
            "aaSorting": [[4, "asc"]], // Sort by creation date by default
            "pagingType": "full_numbers",
            "oLanguage": {
                "sInfo": "Displaying _START_ to _END_ of _TOTAL_ incidents matching selected criteria"
            },
        });
    }


    //------------------------------------------------------------------------------------
    // Reload the available options on "Choice to Filter Events By" field, based on the
    // input to the "Paremeter to Plot Events By" field, for key-based Parameters
    //------------------------------------------------------------------------------------
    $(document).on('change','#id_fk_model_type', function() {
    // $("#id_fk_model_type").change(function() {
        reload_fk_choices($(this).find("option:selected").text());
        if ($(this).find("option:selected").val() == "") {
            $("#hide-id_fk_single_choice").slideUp();
        }
        else {
            $("#hide-id_fk_single_choice").slideDown();
        }
    });
    $("#id_fk_model_type").trigger('change');

    function reload_fk_choices(cur_model) {
        $.ajax({
            type: 'POST',
            url: $("#reload_fk_choices_view").text(),
            dataType: 'json',
            data: 'cur_model='+cur_model,
            success: function(json_data){
                if (json_data.empty) {
                    $("#id_fk_single_choice").empty();
                    $('#id_fk_single_choice').append('<option value>---------</option>');
                    $('#id_fk_single_choice').append('<option value="All" selected="selected">All</option>');
                    if (json_data.error_message) {
                        var alertType = "alert-error";
                        displayMessage(alertType, json_data.error_message);
                    }
                }
                else {
                    $("#id_fk_single_choice").empty();
                    $('#id_fk_single_choice').append('<option value>---------</option>');
                    $('#id_fk_single_choice').append('<option value="All" selected="selected">All</option>');
                    $.each(json_data.choices, function(index, value) {
                        var value_ticker = index+1;
                        $('#id_fk_single_choice').append('<option value="'+value+'">'+value+'</option>');
                    });
                }
                $('select').trigger("chosen:updated");
            }
        });
    }

    //------------------------------------------------------------------------------------
    // Reload the available options on "Choice to Filter Events By" field, based on the
    // input to the "Paremeter to Plot Events By" field, for user-based Parameters
    //------------------------------------------------------------------------------------
    $(document).on('change','#id_user_type', function() {
        reload_user_choices($(this).find("option:selected").text());
        if ($(this).find("option:selected").val() == "") {
            $("#hide-id_user_single_choice").slideUp();
        }
        else {
            $("#hide-id_user_single_choice").slideDown();
        }
    });
    $("#id_user_type").trigger('change');

    function reload_user_choices(cur_model) {
        $.ajax({
            type: 'POST',
            url: $("#reload_user_choices_view").text(),
            dataType: 'json',
            data: 'cur_model='+cur_model,
            success: function(json_data){
                if (json_data.empty) {
                    $("#id_user_single_choice").empty();
                    $('#id_user_single_choice').append('<option value>---------</option>');
                    $('#id_user_single_choice').append('<option value="All" selected="selected">All</option>');
                    if (json_data.error_message) {
                        var alertType = "alert-error";
                        displayMessage(alertType, json_data.error_message);
                    }
                }
                else {
                    var user_ids = json_data.user_ids;
                    var user_names = json_data.user_names;
                    $("#id_user_single_choice").empty();
                    $('#id_user_single_choice').append('<option value>---------</option>');
                    $('#id_user_single_choice').append('<option value="All" selected="selected">All</option>');
                    for (var i=0; i<user_ids.length; i++) {
                        $('#id_user_single_choice').append('<option value="'+user_ids[i]+'">'+user_names[i]+'</option>');
                    }
                }
                $('select').trigger("chosen:updated");
            }
        });
    }

    $(".clear-form").click(function(){
        $('#statistics-form').trigger("reset");
        $('select').trigger("chosen:updated");
        removeErrors();
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
        removeMessages();
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
                    // $($control).addClass("error");
                    $newDiv = $("<div id='error-field-" + field + "' class='error-msg help-block' style='display: none;'>" + message + "</div>");   
                    if (($control).next().hasClass("chosen-container")) {
                        $control.next().addClass("chosen-error");
                        $newDiv.insertAfter($control.next()).slideDown('fast');
                    }
                    else {
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
    // Remove action error messages and highlighting
    //------------------------------------------------------------------------------------
    function removeErrors() {
        $.each($(".error-msg"), function() {
            $(this).slideUp('fast', function() {
                $(this).parent().parent().removeClass("error"); // remove red error class
                $(this).prev().removeClass("chosen-error");
                $(this).remove(); // remove the error message
            });
        });
    }

    //------------------------------------------------------------------------------------
    // Display an ajax message to the user which indicates an error/success status
    //
    // @param {string} alertType - a string representing additional classes which should
    // be added to the ajax message (effectively to color the message differently if
    // displaying success vs. warning vs. error)
    //
    // @param {string} messageText - a string containing the message to be displayed.
    //------------------------------------------------------------------------------------
    function displayMessage(alertType, messageText) {
        // $(".ajax_messages").html("");
        $("#floating-status-message").remove();
        // $(".ajax_messages").append("<div class='message-div alert " + alertType + " style='display: none;'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        // $(".alert").slideDown();

        var $message = $("<div id='floating-status-message' class='floating-message-div alert " + alertType + " style='width:100%'><a class='close' href='#' data-dismiss='alert'>&times;</a><strong>" + messageText + "</strong></div>");
        $('.navbar').append($message);
         setTimeout(function() {
             $message.remove();
         }, 10000)
    }

    //------------------------------------------------------------------------------------
    // Handle popovers on the form inputs
    //------------------------------------------------------------------------------------
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


    //------------------------------------------------------------------------------------
    // Hide the corresponding plot if a close button is clicked
    //------------------------------------------------------------------------------------
    $(document).on("click", ".close-button", function() {
        $(this).parent().parent().parent().slideUp();
        // setTimeout(function() {
        //     $(this).parent().parent().parent().remove();
        // }, 5000)
    });

    //------------------------------------------------------------------------------------
    // Handle rewriting the title of a highcharts plot. 
    //------------------------------------------------------------------------------------
    $(document).on("keyup", ".inputTitle", function(e) {
    // $(document).keyup(function (e) {

        if (e.keyCode == 13) {
            var cur_id = $(this).attr("id");
            var plot_id = cur_id.replace( /^\D+/g, '');
            var $title_div = $("#plot-container-"+plot_id).find('.highcharts-title tspan')

            $title_div.html($('#inputTitle-'+plot_id).val());
            Highcharts.charts[parseInt(plot_id)-1].options.title.text = $('#inputTitle-'+plot_id).val();
            $('#inputTitle-'+plot_id).css("visibility", "hidden");
        }
    });

    $(document).on("click", ".title-button", function() {
        var cur_id = $(this).attr("id");
        // var plot_id = cur_id.substring(cur_id.indexOf("__")+1,cur_id.lastIndexOf("__"));
        var plot_id = cur_id.replace( /^\D+/g, '');

        var $title_div = $("#plot-container-"+plot_id).find('.highcharts-title tspan')

        $('#inputTitle-'+plot_id).val($title_div.html());
        $title_div.html("");
        $('#inputTitle-'+plot_id).css("visibility", "visible");
        $('#inputTitle-'+plot_id).focus();
    });

    $('.highcharts-title').css('cursor', 'pointer');

    //------------------------------------------------------------------------------------
    // Remove individual coloration of points (bars) on a column chart
    //------------------------------------------------------------------------------------
    $(document).on("click", ".color-button", function() {
        var cur_id = $(this).attr("id");
        var plot_id = cur_id.replace( /^\D+/g, '');
        var mychart = Highcharts.charts[parseInt(plot_id)-1]

        console.log(mychart);

        for (var i=0; i<mychart.series[0].data.length; i++) {
            // mychart.series[0].data[i].color = "#333333";
            mychart.series[0].data[i].update({
                options:{
                    color: "#2B558B"
                }
            });
        }
        $(this).hide();
    });

    //------------------------------------------------------------------------------------
    // Toggle draggability of a plot legend
    //------------------------------------------------------------------------------------
    $(document).on("click", ".legend-button", function() {
        var cur_id = $(this).attr("id");
        var plot_id = cur_id.replace( /^\D+/g, '');

        var is_floating = Highcharts.charts[parseInt(plot_id)-1].options.legend.floating;
        var new_floating = !is_floating;
        Highcharts.charts[parseInt(plot_id)-1].options.legend.floating = new_floating;
        Highcharts.charts[parseInt(plot_id)-1].redraw();
    });

    //------------------------------------------------------------------------------------
    // Toggle appearance of a plot legend
    //------------------------------------------------------------------------------------
    $(document).on("click", ".legend-display-button", function() {
        var cur_id = $(this).attr("id");
        var plot_id = cur_id.replace( /^\D+/g, '');
        var mychart = Highcharts.charts[parseInt(plot_id)-1]

        var legend = mychart.legend;

        if(legend.display) {
            legend.group.hide();
            if (mychart.options.chart.type == "column"){
                legend.box.hide();
            }
            legend.display = false;
        } else {
            legend.group.show();
            if (mychart.options.chart.type == "column"){
                legend.box.show();
            }
            legend.display = true;
        }

        var is_enabled = mychart.options.legend.enabled;
        var new_enabled = !is_enabled;
        mychart.options.legend.enabled = new_enabled

        if (mychart.options.chart.type == "column"){
            var is_draggable = mychart.options.legend.draggable;
            var new_draggable = !is_draggable;
            mychart.options.legend.draggable = new_draggable
        }
        mychart.redraw();
    });

    //------------------------------------------------------------------------------------
    // Toggle appearance of data labels on the plot itself
    //------------------------------------------------------------------------------------
    $(document).on("click", ".labels-display-button", function() {
        var cur_id = $(this).attr("id");
        var plot_id = cur_id.replace( /^\D+/g, '');
        var mychart = Highcharts.charts[parseInt(plot_id)-1]

        var cur_labels = mychart.options.plotOptions.pie.dataLabels.enabled;
        var new_labels = !cur_labels;

        mychart.options.plotOptions.pie.dataLabels.enabled = new_labels;
        mychart.series[0].update({ dataLabels: { enabled:new_labels }});

        mychart.redraw();
    });

    //------------------------------------------------------------------------------------
    // Remove the outer ring of data (dates) for pie charts
    //------------------------------------------------------------------------------------
    $(document).on("click", ".date-remove-button", function() {
        var cur_id = $(this).attr("id");
        var plot_id = cur_id.replace( /^\D+/g, '');
        var mychart = Highcharts.charts[parseInt(plot_id)-1]

        mychart.series[1].remove();

        $("#remove-date-"+plot_id).hide();
    });

    // Handle display of appropriate choice fields
    $("#id_parameter_type").change(function(){
        var parameter_type = $("#id_parameter_type").find("option:selected").text().toLowerCase();
        var nsir_text = "nsir";
        var user_text = "user";

        if (parameter_type.indexOf(nsir_text) >= 0) {
            $("#hide-id_fk_model_type").slideDown();
            $("#hide-id_fk_single_choice").slideDown();
            $("#hide-id_user_type").slideUp();
            $("#hide-id_user_single_choice").slideUp();
        }
        else if (parameter_type.indexOf(user_text) >= 0) {
            $("#hide-id_user_type").slideDown();
            $("#hide-id_user_single_choice").slideDown();
            $("#hide-id_fk_model_type").slideUp();
            $("#hide-id_fk_single_choice").slideUp();
        }
        else {
            $("#hide-id_user_type").slideUp();
            $("#hide-id_user_single_choice").slideUp();
            $("#hide-id_fk_model_type").slideUp();
            $("#hide-id_fk_single_choice").slideUp();
        }
        $('select').trigger("chosen:updated");
    }).trigger('change');

    // Handle display of fields upon binning type change
    $("#id_date_bin").change(function(){
        var date_bin_type = $("#id_date_bin").find("option:selected").text().toLowerCase();
        var monthly_text = "monthly";
        var yearly_text = "yearly";
        var monthly_choose_text = "monthly - choose range";
        var choose_text = "choose";

        // if (date_bin_type.indexOf(monthly_text) >= 0) {
        // if (date_bin_type == monthly_choose_text) {
        if (date_bin_type.indexOf(choose_text) >= 0) {
            if (date_bin_type.indexOf(yearly_text) >= 0) {
                $("#hide-id_start_month").slideUp();
                $("#hide-id_end_month").slideUp();
                $("#hide-id_start_year").slideDown();
                $("#hide-id_end_year").slideDown();
            }
            else if (date_bin_type.indexOf(monthly_text) >= 0) {
                $("#hide-id_start_year").slideDown();
                $("#hide-id_end_year").slideDown();
                $("#hide-id_start_month").slideDown();
                $("#hide-id_end_month").slideDown();
            }
        }
        else {
            $("#hide-id_start_month").slideUp();
            $("#hide-id_end_month").slideUp();
            $("#hide-id_start_year").slideUp();
            $("#hide-id_end_year").slideUp();
            $("#id_start_month").val(null);
            $("#id_end_month").val(null);
            $("#id_start_year").val(null);
            $("#id_end_year").val(null);
        }
    }).trigger('change');

    //------------------------------------------------------------------------------------
    // Function which overrides behaviour in the highcharts source code. This behaviour
    // allows a specific formatting for the legend for pie charts. Separate entries for
    // inner and outer data via blank entries in the legend. Also allow specific data
    // points in a series to be hidden from the legend via showInLegend parameter. This
    // parameter is set per data point in the view/statistics.
    //------------------------------------------------------------------------------------
    (function (H) {
        var UNDEFINED;
        /**
         * Returns true if the object is not null or undefined. Like MooTools' $.defined.
         * @param {Object} obj
         */
        function defined(obj) {
            return obj !== UNDEFINED && obj !== null;
        }
        H.wrap(H.Legend.prototype, 'getAllItems', function (p) {
            var allItems = []
            H.each(this.chart.series, function (series) {
                var seriesOptions = series.options;

                // Handle showInLegend. If the series is linked to another series, defaults to false.
                if (!H.pick(seriesOptions.showInLegend, !defined(seriesOptions.linkedTo) ? UNDEFINED : false, true)) {
                    return;
                }

                if (series.legendItems) {
                    // use points or series for the legend item depending on legendType
                    allItems = allItems.concat(series.legendItems);
                } else if (seriesOptions.legendType === 'point') {
                    var pointsForLegend = [];
                    var i_pad = 0 // padding variable
                    H.each(series.data, function (e, i) {
                        if (e.showInLegend) {
                            if (series.name == "Date Bins" && i_pad == 0){
                                e.showInLegend = false;
                                // pointsForLegend.push(e);
                                pointsForLegend.push(e);
                                pointsForLegend.push(e);
                                // pointsForLegend.push(e);
                                pointsForLegend.push(e);
                                e.showInLegend = true;
                                i_pad = 1; // no longer need to pad
                            }
                            pointsForLegend.push(e);
                        }
                    })
                    allItems = allItems.concat(pointsForLegend);
                } else {
                    allItems = allItems.concat(series);
                }
            });
            return allItems;
        });
    })(Highcharts);
});