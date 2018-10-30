function initSelectArrowOnly(){
    $('select[data-arrow-only]').each(function () {
        var t = $(this);
        if (t.closest('span.arrow-only-wrapper').length == 0) {
            t.wrap('<span class="arrow-only-wrapper">');
        }
    });
}
var $$ = $$ ? $$ : {};

$(function() {
    $("form").submit($$.formSubmit);
    $$.fieldsInit();
    // $$.elReloadInit();
    $(document).foundation();
    jQuery.ajaxSetup( {
        beforeSend : function(msg) {
            $("#ajax_status").removeClass('ERROR').html('Request ...') },
        error : function(msg) {
            $("#ajax_status").addClass('ERROR').html('Error!') },
    });
});

