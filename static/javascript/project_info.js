$(document).ready(function() {
    $.fn.editable.defaults.mode = 'inline';
    $('#project_name').editable();
    $('#description').editable({
       type:  'textarea',
    });
    $('#prepared_by').editable();
    $('#protocol').editable({
        type: 'select',
        value: $('#protocol').text(),
        source: [
              {value: 'New', text: 'New'},
              {value: 'Old', text: 'Old'},
              {value: 'N/A', text: 'N/A'}
           ]
    });

    $('#save_project').on("click", function() {
        var data = {};
        $('.editable-unsaved').each(function() {
            var el_id = $(this).attr('id');
            data[el_id] = $('#'+el_id).text();
        });
        if ($.isEmptyObject(data)) {
            alert("Project info has not been changed")
        } else {
            var url = $(location).attr('href');
            $.post(url, data, function(data, status) {
                $('.editable-unsaved').removeClass('editable-unsaved');
                alert('Successfully updated');
            });
        }
    });

    $('#description').parent().find('div.editable-input').parent().addClass('w-100');
});