$(document).ready(function () {
    $(".tm-input").each(function (index) {
        var field_name = $(this).data("field-name");
        var ajax_url = $(this).data("ajax-url");
        var current_tags = $(this).data("current-value").split("|");

        var tagApi = $(this).tagsManager({
            hiddenTagListName: field_name,
            tagsContainer: "#" + field_name + "_tag_container",
        });

        $.each(current_tags, function (index, value) {
           console.log(index, value);
           tagApi.tagsManager("pushTag", value);
        });

        $(this).typeahead({
            name: 'tags',
            limit: 20,
            remote: ajax_url + "?q=%QUERY"
        }).on('typeahead:selected', function (e, d) {
                tagApi.tagsManager("pushTag", d.value);
            });
    });

    $(".tm-existing-item").click(function (e) {
        $($(this).data("target")).tagsManager("pushTag", $(this).text());
        e.preventDefault();
        return false;
    })

});