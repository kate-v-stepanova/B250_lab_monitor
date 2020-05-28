$(document).ready(function() {
    $('button.delete-user').on('click', function() {
        var email = $(this).closest('tr').find('td.username').text();
        var tr_to_delete = $(this).closest('tr');
        var url = window.location.href + "/delete_user";
        var user_data = {'email': email};
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data:  JSON.stringify(user_data),
            contentType: 'application/json',
        }).done(function(response) {
            tr_to_delete.remove();
            $('#error-2').removeClass('d-none');
            $('#error-2').removeClass('alert-danger');
            $('#error-2').addClass('alert-success');
            $('#error-text-2').append('<p>User <b>' + email + '</b> has been successfully deleted</p>');
        }).fail(function(response) {
            var error_message = response['responseJSON']['error_message'];
            $('#error-2').removeClass('d-none');
            $('#error-2').removeClass('alert-success');
            $('#error-2').addClass('alert-danger');
            $('#error-text-2').append(error_message);
        });
    });

    $('#new_pass_btn').on('click', function() {
        var new_pass = Math.random().toString(20).substr(2, 8);
        $('#new_pass').val(new_pass);
    });

    $('#modal-submit').on('click', function() {
        var email = $('#new_email').val();
        var repeat = $('#repeat_email').val();
        var pass = $('#new_pass').val();

        // validate form
        var error_message = ""
        if (email != repeat) {
            error_message += "<p>Emails don't match</p>"
        }
        var email_regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i;
        if(!email_regex.test(email)) {
            error_message += "<p><b>" + email + " </b>is not a valid email</p>";
        }
        if (!email_regex.test(repeat) && email != repeat) {
            error_message += "<p><b>" + repeat + " </b>is not a valid email</p>";
        }
        if (pass == "") {
            error_message += "<p>Password should not be empty</p>"
        }
        // show error message
        if (error_message != "") {
            $('#error-text').empty();
            $('#error-text').append(error_message);
            $('#error').removeClass('d-none');
            $('#error').removeClass('alert-success');
            $('#error').addClass('alert-danger');
        } else {
        // submit to server
            $('#error-text').empty();
            $('#error').addClass('d-none');
            var url = window.location.href + "/create_user";
            user_data = {'email': email, 'password': pass}
            $.ajax({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: url,
                dataType: 'json',
                //json object to sent to the authentication url
                data:  JSON.stringify(user_data),
                contentType: 'application/json',
            }).done(function(response) {
                $('#error').removeClass('d-none');
                $('#error').removeClass('alert-danger');
                $('#error').addClass('alert-success');
                $('#error-text').append('<p>User <b>' + email + '</b> has been successfully created</p>');
                $('#new_email').val('');
                $('#repeat_email').val('');
                $('#new_pass').val('');
                var new_row = "<tr><td class='username'>" + email +
                    "</td><td><button class='btn btn-sm btn-outline-secondary delete-user'>×</button></td></tr>"
                $("#list_of_users tbody").prepend(new_row);
            }).fail(function(response) {
                var error_message = response['responseJSON']['error_message'];
                $('#error').removeClass('d-none');
                $('#error').removeClass('alert-success');
                $('#error').addClass('alert-danger');
                $('#error-text').append(error_message);
            });
        }
    });

    $('#change_password').on('click', function() {
        var email = $('#email').val();
        var current_pass = $('#current_password').val();
        var new_pass = $('#new_password').val();
        var repeat_pass = $('#repeat_password').val();
        var error_message = ""
        if (new_pass.length < 8) {
            error_message += "<p>Password is too short</p>";
        }
        if (new_pass != repeat_pass) {
            error_message += "<p>Passwords don't match</p>";
        }
        if (error_message != "") {
            $('#error-2').removeClass('d-none');
            $('#error-2').removeClass('alert-success');
            $('#error-2').addClass('alert-danger');
            $('#error-text-2').empty();
            $('#error-text-2').append(error_message);
        } else {
            var data = {'email': email, 'current_pass': current_pass, 'new_pass': new_pass};
            var url = window.location.href.replace('login', 'user_details') + "/change_password"; // bad, but simple
            var done = false;
            $.ajax({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: url,
                dataType: 'json',
                //json object to sent to the authentication url
                data:  JSON.stringify(data),
                contentType: 'application/json',
            }).done(function(response) {
                $('#error-2').removeClass('d-none');
                $('#error-2').removeClass('alert-danger');
                $('#error-2').addClass('alert-success');
                $('#error-text-2').empty();
                $('#error-text-2').append('<p>Password has been successfully changed</p>');
                $('#current_password').val('');
                $('#new_password').val('');
                $('#repeat_password').val('');
                done = true;
            }).fail(function(response) {
                var error_message = response['responseJSON']['error_message'];
                $('#error-2').removeClass('d-none');
                $('#error-2').removeClass('alert-success');
                $('#error-2').addClass('alert-danger');
                $('#error-text-2').empty();
                $('#error-text-2').append(error_message);
            });

            if (window.location.href.includes('/login') && done) {
                // this shit doesn't work
                setTimeout(function () {
                    alert('You will be redirected now')
                    window.location.replace('/login', '/')
                }, 5000);
            }
        }

    });
});