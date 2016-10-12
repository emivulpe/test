function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

var csrftoken = getCookie('csrftoken');

$('#report_button').click(function(){
    alert('button clicked');
    var URL = $('#url').val();
    alert(URL);
    var request = $.post("/mercurytide/report/", {
        'url': URL,
        'csrfmiddlewaretoken': csrftoken,
    }).done(function(report_data) {
        if ("error" in report_data) {
            alert("error");
        }
        else{
            $("#contents").empty();
            alert("no error" + report_data);

            for (var report_item in report_data) {
                alert(report_item);
                alert(report_data[''+report_item]);
            }
        }
    })
});
