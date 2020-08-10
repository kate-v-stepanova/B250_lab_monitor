$(document).ready(function() {
    // search projects
    function search_project() {
        var to_search = $('#search').val();
        if (to_search != '') {
            var url = window.location.href + "/search";
            $.ajax({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: url,
                dataType: 'json',
                //json object to sent to the authentication url
                data: to_search,
                contentType: 'text/html',
            }).done(function(response) {
                $('.project').addClass('d-none');
                var found = response['matching_projects'];
                for (i=0; i<found.length; i++) {
                    $('#' + found[i]).removeClass('d-none');
                }
                $('#clear_search').removeClass('d-none');
            }).fail(function(response) {
                console.log(response);
                alert('Failed');
            });
        }
    };
    // search on button click
    $('#search_btn').on('click', function() {
        search_project();
    });

    // disable form submission when pressing Enter
    $(window).keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            if (event.target.id == 'search') {
                search_project();
            }
            return false;
        }
    });

    // clear results
    $('#clear_search').on('click', function() {
        $('.project').removeClass('d-none');
        $('#clear_search').addClass('d-none');
    });
});
