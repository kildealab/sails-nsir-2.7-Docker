"use strict";

$(document).ready(function(){

    $("#action-complete-table").DataTable({
        sDom:'<<ir>><<rt>><<p>>',
        iDisplayLength: -1, // Display all rows
        "bInfo": false, // Disable: "Showing x to y of z entries"
        "bAutoWidth": false,
        "bPaginate": false, // Disable: Next and Previous page buttons
        // "bSortClasses": false, // Disable: Sort column Highlighting
        //"aaSorting": [[7, "desc"]] // Sort by creation date by default
        "aaSorting": [[2, "desc"]] // Sort by creation date by default
    });

    $("#action-incomplete-table").DataTable({
        sDom:'<<ir>><<rt>><<p>>',
        iDisplayLength: -1, // Display all rows
        "bInfo": false, // Disable: "Showing x to y of z entries"
        "bAutoWidth": false,
        "bPaginate": false, // Disable: Next and Previous page buttons
        // "bSortClasses": false, // Disable: Sort column Highlighting
        //"aaSorting": [[7, "desc"]] // Sort by creation date by default
        "aaSorting": [[3, "desc"]] // Sort by creation date by default
    });

    // JSPlumb draws the connectors (arrows) between flowchart elements
    jsPlumb.ready(function() {
        // Anchors are [x,y] coordinators of the start,end positions of connectors
        // When more than two elements are provided in the outer array, jsplumb will
        // cycle between them from one element to the next
        var dynamicAnchors = [ 
            [0.75,1],
            [0.25,0],
            [0.75,0],
            [0.25,1],
        ];
        var optionalAnchors = [
            [1,0.25],
            [1,0.5],
            [1,0.75],
            [0,0.25],
            [0,0.5],
            [0,0.75]
        ];
        var newAnchors = [ 
            [1,0.5],
            [0,0.5],
        ];

        var arrowHead = ["PlainArrow", {width:10, length:15, location:0.86}];
        var spreadArrowHead = ["PlainArrow", {width:10, length:15, location:0.94}];

        var straightLines = { strokeStyle:"#333", lineWidth:3/*, dashstyle:"2 2"*/ };
        var dashedLines = { strokeStyle:"#333", lineWidth:3, dashstyle:"2 2" };

        var myEndPoints = [ "Rectangle", { width:1, height:1 } ]

        // Draw connectors
        jsPlumb.connect({
            source:"item_incident",
            target:"item_report",
            endpoint: myEndPoints,
            overlays:[ arrowHead ],
            anchor: newAnchors,
            connector: "Straight",
            paintStyle: straightLines
        });
        // If report was submitted by a coordinator, there is an extra piece in the flowchart
        if ($("#item_coordinator").length) {
            jsPlumb.connect({
                source:"item_report",
                target:"item_coordinator",
                endpoint: myEndPoints,
                overlays:[ arrowHead ],
                anchor: dynamicAnchors,
                connector: "Straight",
                paintStyle: straightLines
            });
            jsPlumb.connect({
                source:"item_coordinator",
                target:"item_investigator",
                endpoint: myEndPoints,
                overlays:[ arrowHead ],
                anchor: dynamicAnchors,
                connector: "Straight",
                paintStyle: straightLines
            });
        }
        else {
            jsPlumb.connect({
                source:"item_report",
                target:"item_investigator",
                endpoint: myEndPoints,
                overlays:[ arrowHead ],
                anchor: newAnchors,
                connector: "Straight",
                paintStyle: straightLines
            });
        }
        jsPlumb.connect({
            source:"item_investigator",
            target:"item_submit",
            endpoint: myEndPoints,
            overlays:[ arrowHead ],
            anchor: newAnchors,
            connector: "Straight",
            paintStyle: straightLines
        });
        jsPlumb.connect({
            source:"item_submit",
            target:"item_investigation",
            endpoint: myEndPoints,
            overlays:[ arrowHead ],
            anchor: newAnchors,
            connector: "Straight",
            paintStyle: straightLines
        });

        jsPlumb.connect({
            source:"item_investigation",
            target:"item_share",
            endpoint: myEndPoints,
            overlays:[ spreadArrowHead ],
            anchor: optionalAnchors,
            connector: "Straight",
            paintStyle: dashedLines
        });

        jsPlumb.connect({
            source:"item_investigation",
            target:"item_discussion",
            endpoint: myEndPoints,
            overlays:[ spreadArrowHead ],
            anchor: optionalAnchors,
            connector: "Straight",
            paintStyle: dashedLines
        });

        jsPlumb.connect({
            source:"item_investigation",
            target:"item_action",
            endpoint: myEndPoints,
            overlays:[ spreadArrowHead ],
            anchor: optionalAnchors,
            connector: "Straight",
            paintStyle: dashedLines
        });

        // OLD VERSION OF FLOWCHART (WHEN USING PAPER FORMS)

        // jsPlumb.connect({
        //     source:"item_incident",
        //     target:"item_paper",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_paper",
        //     target:"item_sub_coord",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_sub_coord",
        //     target:"item_add_coord",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_add_coord",
        //     target:"item_sub_chief",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_sub_chief",
        //     target:"item_transcribe",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_transcribe",
        //     target:"item_assign",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });
        // jsPlumb.connect({
        //     source:"item_assign",
        //     target:"item_investigate",
        //     endpoint: myEndPoints,
        //     overlays:[ arrowHead ],
        //     anchor: dynamicAnchors,
        //     connector: "Straight",
        //     paintStyle: straightLines
        // });

        // jsPlumb.connect({
        //     source:"item_investigate",
        //     target:"item_share",
        //     endpoint: myEndPoints,
        //     overlays:[ spreadArrowHead ],
        //     anchor: optionalAnchors,
        //     connector: "Straight",
        //     paintStyle: dashedLines
        // });

        // jsPlumb.connect({
        //     source:"item_investigate",
        //     target:"item_discussion",
        //     endpoint: myEndPoints,
        //     overlays:[ spreadArrowHead ],
        //     anchor: optionalAnchors,
        //     connector: "Straight",
        //     paintStyle: dashedLines
        // });

        // jsPlumb.connect({
        //     source:"item_investigate",
        //     target:"item_action",
        //     endpoint: myEndPoints,
        //     overlays:[ spreadArrowHead ],
        //     anchor: optionalAnchors,
        //     connector: "Straight",
        //     paintStyle: dashedLines
        // });
        // jsPlumb.connect({
        //     source:"item_bottom",
        //     target:"item_right",
        //     endpoint:[ "Rectangle", { width:1, height:1 } ],
        //     overlays:[ ["PlainArrow", {location:1, width:15, length:20} ]],
        //     paintStyle:{ strokeStyle:"#333", lineWidth:4 }
        // });
    });

    $(window).resize(function(){
          jsPlumb.repaintEverything();
      });
});