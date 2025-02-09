//----------------------------------------------------------------------------------------
// Function called upon page load
//----------------------------------------------------------------------------------------
$(document).ready(function(){

    // Required for sorting of incidents by ID number (numerically rather than
    // alphabetically in the corresponding jQuery DataTables)
    jQuery.fn.dataTableExt.oSort['numeric-html-asc']  = function(a,b) {
        a = parseInt($(a).text());
        b = parseInt($(b).text());
        return ((a < b) ? -1 : ((a > b) ?  1 : 0));
    };
    jQuery.fn.dataTableExt.oSort['numeric-html-desc']  = function(a,b) {
        a = parseInt($(a).text());
        b = parseInt($(b).text());
        return ((a < b) ? 1 : ((a > b) ?  -1 : 0));
    };

    // Formatting of DataTables
    $("#incident-table").dataTable({
        iDisplayLength:5,
        sDom:'<<ir>><<rt>><<p>>',
        "aoColumns": [
            { "sType": 'numeric-html' },
            { "sType": 'date' },
            null,
            { "sType": 'date' },
            null,
        ],
        "aaSorting": [[3, "desc"]]
    });

    $("#oncologist-table").dataTable({
        iDisplayLength:5,
        sDom:'<<ir>><<rt>><<p>>',
        "aoColumns": [
            { "sType": 'numeric-html' },
            null,
            { "sType": 'date' },
            null,
            null,
            null,
        ],
        "aaSorting": [[2, "desc"]]
    });

    $("#action-table").dataTable({
        iDisplayLength:5,
        sDom:'<<ir>><<rt>><<p>>',
        "aoColumns": [
            { "sType": 'numeric-html' },
            { "sType": 'numeric-html' },
            { "sType": 'date' },
            null,
            null,
        ],
        "aaSorting": [[2, "desc"]]
    });


    //====================================================================================
    // Default options (template) used for generating stacked/date-binned column charts.
    //====================================================================================
    var chart_options = {
        // Taken from:
        // http://tools.medialab.sciences-po.fr/iwanthue/
        // 20 color palette, hard(Force Vector)
        colors: ['#27AED5','#8FD31E','#CF6FFC','#6BE04B','#DE52D1',
            '#16B661','#D0338A','#1CBC8A','#F65262','#6073E0',
            '#D3C247','#3E62A8','#F7983F','#B8A2F0','#73880B',
            '#B0B6EC','#776721','#9D96C5','#B14046','#217C8D'],
        chart: {
            renderTo: 'plot-container',
            type: 'column',
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
            },
        },
        title: {
            text: "",
            style: {
                fontSize:'14px',
                fontWeight: 'bold'
            }
        },
        xAxis: [{
            title: {
                enabled:false,
                text: "",
                style: {
                    // fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            labels: {
                style: {
                    // fontSize:'18px'
                }
            },
            lineWidth: 2,
            lineColor: "#333",
            tickColor: "#333",
        },{
            linkedTo: 0,
            opposite: true,
            title: {
                enabled: false
            },
            labels: {
                enabled: false
            },
            lineWidth: 2,
            tickLength: 0,
            lineColor: "#333",
        }],
        yAxis: [{
            title: {
                enabled:false,
                text: "",
                style: {
                    // fontSize:'20px',
                    fontWeight: 'bold'
                }
            },
            stackLabels: {
                enabled: true,
                style: {
                    // fontSize:'15px',
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            },
            labels: {
                style: {
                    // fontSize:'18px'
                }
            },
            minTickInterval: 1,
            lineWidth: 2,
            lineColor: "#333",
        },{
            linkedTo: 0,
            opposite: true,
            stackLabels : {
                enabled: false
            },
            labels: {
                enabled: false
            },
            title: {
                enabled: false
            },
            lineWidth: 2,
            lineColor: "#333",
        }],
        legend: {
            //Truncate the legend text
            //May change to setting max width, and wrap the text?
            labelFormatter: function() {
                // do truncation here and return string
                // this.name holds the whole label
                // for example:
                if (this.name.length > 30) {
                    return this.name.slice(0, 30)+'...'
                }
                else {
                    return this.name
                }
            },
            layout: 'vertical',
            align: 'left',
            // verticalAlign: 'middle',
            x: 130,
            verticalAlign: 'top',
            y: 90,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false,
            draggable: true,
            // itemStyle: {
            //     fontSize:'18px'
            // }
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: false,
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
                pointWidth: 22,//width of the column bars irrespective of the chart size
                animation: false,
            }
        },
        series: [],
        // Remove watermark from bottom
        credits: {
            enabled: false
        }
    };

    //------------------------------------------------------------------------------------
    // Generate plots
    //------------------------------------------------------------------------------------
    for (var i=0; i<json_data.length;i++){
        setColumnChartOptions(json_data[i],i);
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
    function setColumnChartOptions(json_data,plot_id) {
        var chart_type_jq = json_data.plot_type;
        var y_label_jq = 'Counts';

        var chart_title;
        var new_chart_options = chart_options;
        if (json_data.single_choice != null) {
            chart_title = json_data.complete_label + " (" + json_data.query_model_title + ": " + json_data.single_choice +")";
            new_chart_options.legend.enabled = false;
            // new_chart_options.legend.draggable = true;
        }
        else {
            chart_title = json_data.complete_label + " by " + json_data.query_model_title + " for the Last Year";
            new_chart_options.legend.enabled = false;
            // new_chart_options.legend.draggable = true;
        }

        new_chart_options.chart.type = chart_type_jq;
        new_chart_options.chart.renderTo = 'plot-container-'+plot_id;
        new_chart_options.title.text = chart_title;
        new_chart_options.xAxis[0].title.text = json_data.date_label;
        new_chart_options.xAxis[0].categories = json_data.date_range;
        new_chart_options.yAxis[0].title.text = y_label_jq;
        new_chart_options.series = json_data.series_array;

        //--------------------------------------------------------------------------------
        // Inner function call here is used to create a custom legend for the chart, which
        // is displayed outside the typical plotting area. Add ability for the legend to
        // be clicked to toggle series display, and hovered for series highlighting.
        //--------------------------------------------------------------------------------
        var chartnew = new Highcharts.Chart(
            new_chart_options,
            function (chart) {
                var div_id = chart.renderTo.id;
                var plot_id = div_id.replace( /^\D+/g, '');
                var $legend = $('#customLegend-'+plot_id);

                // $legend.append('<table style="width:100%">')
                $.each(chart.series, function (j, data) {
                    $legend.append('<div class="item"><div class="symbol" style="background-color:'+data.color+'"></div><div class="serieName" id="">' + data.name + '</div></div>');
                });
                // $legend.append('</table>')
                
                $('#customLegend-'+plot_id+' .item').click(function(){
                    var inx = $(this).index(),
                        point = chart.series[inx];
                   
                    if(point.visible)
                        point.setVisible(false);
                    else
                        point.setVisible(true);
                });
                $('#customLegend-'+plot_id+' .item').hover(
                function(){
                    var inx = $(this).index();
                    var point = chart.series[inx];
                   
                    if(point.visible) {
                        for (var j=0;j<point.data.length;j++) {
                            point.data[j].setState('hover');
                        }
                    }
                }, 
                function(){
                    var inx = $(this).index();
                    var point = chart.series[inx];
                   
                    if(point.visible) {
                        for (var j=0;j<point.data.length;j++) {
                            point.data[j].setState();
                        }
                    }
                });             
            }
        );
    }


});
