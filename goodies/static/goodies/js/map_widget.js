/**
 * Created with PyCharm.
 * User: andrei
 * Date: 9/22/13
 * Time: 3:40 PM
 * To change this template use File | Settings | File Templates.
 */

(function( $ ){
   $.fn.init_map = function() {
       var $map = $(this);
       var current_coordinates = $("#id_" + $(this).data("field-name")).val();
       var location_lat = 46.06668531963049;
       var location_long = 23.576405296325674;
       if (current_coordinates.length) {
           location_lat = current_coordinates.split(";")[0];
           location_long = current_coordinates.split(";")[1];
       } else {
           $("#id_" + $map.data("field-name")).val(location_lat + ";" + location_long);
       }

       var location = new google.maps.LatLng(location_lat, location_long);
       var map_options = {
           center: location,
           zoom: 7,
           mapTypeId: google.maps.MapTypeId.ROADMAP
       }

       var map = new google.maps.Map(document.getElementById("map_canvas_" + $(this).data("field-name")), map_options);
       var marker = new google.maps.Marker({
           position: location,
           map: map,
           title: "Locația curentă",
           animation: google.maps.Animation.DROP,
           draggable: true
       });



       google.maps.event.addListener(marker, 'click', toggleBounce);
       google.maps.event.addListener(marker, 'dragend', function () {
           console.log("herE", marker.getPosition().lat() + ";" + marker.getPosition().lng());
            $("#id_" + $map.data("field-name")).val(marker.getPosition().lat() + ";" + marker.getPosition().lng());
       });
   };
})( jQuery );

function toggleBounce() {
    if (marker.getAnimation() != null) {
        marker.setAnimation(null);
    } else {
        marker.setAnimation(google.maps.Animation.BOUNCE);
    }
}

jQuery("document").ready(function () {
    $("[id^='map_canvas']").init_map();
})