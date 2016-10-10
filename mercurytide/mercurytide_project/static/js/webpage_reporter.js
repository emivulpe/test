$('#report_button').click(function(){
    alert('button clicked');
    URL = $('#url').val();
    var request = $.post("/mercurytide_app/report/", {
        'url': URL,
    });
    request.done(function(outcome) { // Extract a list of the relevant groups
        if ("error" in outcome) {
            BootstrapDialog.alert(outcome['error']);
        }
        else{
            alert("no error");
        }
    })
});