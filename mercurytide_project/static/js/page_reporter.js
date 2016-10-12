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
                if(report_item == "Links" || report_item == "Keywords_not_appearing_in_the_content" || report_item == 'Metatags' || report_item == 'Most_common_5_words'){
                    var items_list = report_data['' + report_item];
                    alert(items_list[0]);
                    $("#report").append("<li>" + report_item + "<br/><div id='" + report_item + "' class='list_container'></div></li>");
                        for (var i=0; i < items_list.length - 1; i++){
                            var item = items_list[i];
                            $("#" + report_item).append("<p><label>" + item + "</label></p>");
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
                    $("#report").append("<li><label>" + report_item + ": " + report_data['' + report_item] + "</label></li>");
                }
            }
        }
    })
});
