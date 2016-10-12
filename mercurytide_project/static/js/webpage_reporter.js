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
    var URL = $('#url').val();
    var request = $.post("/mercurytide/report/", {
        'url': URL,
        'csrfmiddlewaretoken': csrftoken,
    }).done(function(report_data) {
        if ("error" in report_data) {
            alert(report_data["error"]);
        }
        else{
            $("#contents").append("<ul id='report'></ul>");
            for (var report_item in report_data) {
                alert(report_item);
                if(report_item == "Links"){
                    alert('here');
                    var links_list = report_data['' + report_item];
                    alert(links_list[0]);
                    $("#report").append("<li><div id='page_links'></div></li>");
                        for (var i=0; i < links_list.length - 1; i++){
                            var link = links_list[i]
                            $("#page_links").append("<label>" + link + "</label>");
                            console.log(link);
                        }
//                    var list_string = "";
//                    var item_list = report_data[''+report_item];
//                    for (var i=0; i < item_list.length - 1; i++){
//                        list_string += item_list[i] + ", "
//                        alert(item_list[i]);
//                    }
//                    list_string += item_list[item_list.length - 1];
//                    $("#report").append("<li><label>" + report_item + ": " + list_string + "</label></li>");
                }
                else{
                    alert(report_item + 'in else');
                    $("#report").append("<li><label>" + report_item + ": " + report_data['' + report_item] + "</label></li>");
                }
            }
        }
    })
});
