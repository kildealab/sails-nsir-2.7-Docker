//----------------------------------------------------------------------------------------
// Required for incident list pages which use the Listable django package to create
// jQuery DataTables
//----------------------------------------------------------------------------------------

$(document).ready(function(){
    $(Listable.tableId).addClass(
    Listable.cssTableClass
).dataTable({
    aaSorting:[],
    bStateSave:Listable.stateSave,
    bPaginate: true,
    sPaginationType:Listable.paginationType,
    bProcessing: true,
    bServerSide: true,
    sAjaxSource: Listable.url,
    bAutoWidth: Listable.autoWidth,
    aoColumns:Listable.columnDefs,
    bFilter:true,
    sDom:Listable.DOM
}).columnFilter({
    sPlaceHolder: "head:after",
    aoColumns: Listable.columnFilterDefs,
    iFilteringDelay:250
}).find("input, select").addClass(
    Listable.cssInputClass
);

// Remove "null" options from lists
$('select option')
    .filter(function() {
        return $.trim(this.value) == "None";
    })
   .remove();

});