/**
 * 	Javascript for handling bootstrap tabs and ajax calls to their urls 
 * 	Andrei AVRAM, FITX
 * 
 */

function click_handler(event) {
	event.preventDefault();

	var tab_id = jQuery(this).attr("href");
	var target = jQuery(this).attr("tab-link");
	
	jQuery(".loader").remove();
	jQuery(".error").remove();

	jQuery(this).html("<img src = '{{ STATIC_URL }}images/loading-indicator.gif' class = 'loader' /> " + jQuery(this).html());
	jQuery(this).unbind('click');
	
	window.location.hash = tab_id;
	
	jQuery.ajax(target, {success: function(data) {
		jQuery(tab_id).html(data);
		
		//	also make delete elements possible
		if (typeof generic_delete == 'function') {
			$("a[id^='delete_']").click(generic_delete);
		}
		
		jQuery(".loader").remove();
		
		jQuery("#nav-menu li a[href='" + tab_id +"']").click(click_handler);
	},
	error: function (jqXHR, textStatus, errorThrown) {
		jQuery(".loader").remove();
		jQuery("a[href='" + tab_id + "']").html("<i class = 'icon-warning-sign error'></i> " + jQuery("a[href='" + tab_id + "']").html());
				
		jQuery(tab_id).html("<div class = 'alert alert-error'>A apărut o eroare la încărcarea acestui tab. Vă rugăm să încercați mai târziu sau să contactați un administrator.<br /><br /><span style = 'font-size: 10px;'><strong>Informații pentru depanare / urmărire</strong><br />" + textStatus + ", " + errorThrown + "</span></div>");
		jQuery("#nav-menu li a[href='" + tab_id +"']").click(click_handler);
		
	}
	
	});
	
	jQuery(this).tab('show');
}


jQuery("document").ready(function () {

	//	Change active tab based on anchor
	if ((window.location.hash != "") && jQuery("#nav-menu li a[href='" + window.location.hash + "']").length > 0) {
		console.log("Have tab overwrite ", window.location.hash);
		jQuery("#nav-menu li.active a").parent().removeClass("active");
		
		console.log(jQuery("div.tab-content div.active").attr("id"));
		jQuery("div.tab-content div.active").removeClass("active");
		
		jQuery("#nav-menu li a[href='" + window.location.hash + "']").parent().addClass("active");
		jQuery(window.location.hash).addClass("active");
		
	}
	
	//	First tab - active on page show, triggering manually
	jQuery("#nav-menu li a").click(click_handler);
	
	var tab_id = jQuery("#nav-menu li.active a").attr("href");
	var target = jQuery("#nav-menu li.active a").attr("tab-link");
	
	jQuery("#nav-menu li.active a[href='" + tab_id + "']").html("<img src = '{{ STATIC_URL }}images/loading_indicator.gif' class = 'loader' /> " + jQuery("#nav-menu li a[href='" + tab_id + "']").html());
	jQuery("#nav-menu li a[href='" + tab_id + "']").unbind('click');
	
	jQuery.ajax(target, {success: function(data) {
		jQuery(tab_id).html(data);
		
		//	also make delete elements possible
		if (typeof generic_delete == 'function') {
			$("a[id^='delete_']").click(generic_delete);
		}
		
		jQuery(".loader").remove();
		jQuery("#nav-menu li a[href='" + tab_id +"']").click(click_handler);
	},
	error: function (jqXHR, textStatus, errorThrown) {
		jQuery(".loader").remove();
		jQuery("a[href='" + tab_id + "']").html("<i class = 'icon-warning-sign error'></i> " + jQuery("a[href='" + tab_id + "']").html());
				
		jQuery(tab_id).html("<div class = 'alert alert-error'>A apărut o eroare la încărcarea acestui tab. Vă rugăm să încercați mai târziu sau să contactați un administrator.<br /><br /><span style = 'font-size: 10px;'><strong>Informații pentru depanare / urmărire</strong><br />" + textStatus + ", " + errorThrown + "</span></div>");
		jQuery("#nav-menu li a[href='" + tab_id +"']").click(click_handler);
		
	}
	
	});	
	
	jQuery("#nav-menu li.active a").tab('show');
	
});
