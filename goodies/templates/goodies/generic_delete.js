function after_generic_delete_{{ prefix }}(data) {
	if (data.error_msg.length) {
		$("#message_container").append("<div id = \"message_alert_" + data.obj_id + "\" class=\"alert alert-error\">Obiectul nu a putut fi șters! <br /><span style = 'font-size:10px;'>"+ data.error_msg + "</span></div>");
		setTimeout('$("#message_alert_' + data.obj_id + '").fadeOut("fast")', 3000);
	} else {
		$("a[id^='{{ prefix }}_" + data.obj_id + "']").closest("tr").hide("fast");
		$("#message_container").append("<div id = \"message_alert_" + data.obj_id + "\" class=\"alert alert-success\">Obiectul a fost șters cu success</div>");
		setTimeout('$("#message_alert_' + data.obj_id + '").fadeOut("fast")', 3000);
	}	
}

function generic_delete_{{ prefix }}(event) {
	console.log("Entering generic_delete, prefix {{ prefix }}");
	var id_html = $(this).attr("id").match(/{{ prefix }}_(\d+)/);
	var ctype_id = null;
	if ($(this).data("ctypeid")) {
		ctype_id = $(this).data("ctypeid");
		console.log("Using hand specified ctype", ctype_id);
	} else {
		ctype_id = "{{ ctype.id }}";
		console.log("Using js set ctype", ctype_id);
	}
	
	if (confirm("Sunteți sigur că vreți să ștergeți această înregistrare?")) {
        $.post("{% url "goodies:js_ajax_delete" %}",
            {"obj_id" : id_html[1], "obj_ctype_id" : ctype_id, "prefix" : "{{ prefix }}"},
            after_generic_delete_{{ prefix }})
	};
	
	event.preventDefault();
}

{% if not using_tabs %}
	jQuery("document").ready(function () {
		$("a[id^='{{ prefix }}_']").click(generic_delete_{{ prefix }});
	});
{% endif %}