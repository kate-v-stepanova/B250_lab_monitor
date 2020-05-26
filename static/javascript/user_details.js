$(document).ready(function() {
    $('.delete-user').on('click', function() {
        var username = $(this).closest('tr').find('td.username').text();
        console.log(username);

    });
});