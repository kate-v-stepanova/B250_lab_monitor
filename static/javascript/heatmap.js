$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    // initial html of multiselect without any selected options
    const group2_html = $('li#group2').html().replace(/selected/g, '');

    const choices = new Choices('#first_group', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "All samples selected"
    });

    var group2 = new Choices('#second_group', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "All samples selected"
    });


    $('#filter1').change(function() {
        if ($(this).val() === 'list_of_genes') {
            $('#list_of_genes').removeClass('d-none');
            $('#number_of_genes').addClass('d-none');
            remove_group();
            $('#add_group').addClass('d-none');
        } else {
            if (!$('#list_of_genes').hasClass('d-none')) {
                $('#list_of_genes').addClass('d-none');
                $('#number_of_genes').removeClass('d-none');
                $('#add_group').removeClass('d-none');
            }
        }
    });
    if ($('#inchlib').length != 0) {
        var a = $('#inchlib').attr('data-series');
        a = a.replace(/'/g, '"'); //");
        a = JSON.parse(a);
        $('#inchlib').removeAttr('data-series');
        window.inchlib = new InCHlib({ //instantiate InCHlib
            target: "inchlib", //ID of a target HTML element
            metadata: true, //turn on the metadata
            draw_row_ids: true,
            //max_height: 1200, //set maximum height of visualization in pixels
            min_row_height: 15,
            width: 1000, //set width of visualization in pixels
            heatmap_colors: "BuWhRd", //set color scale for clustered data
            column_dendrogram: true,
        });
        inchlib.read_data(a);
        inchlib.draw(); //draw cluster heatmap
    }

    // export CSV data
    var csv_data = $('#inchlib').attr('data-csv')
    if (csv_data) {
        $('#export_button').on('click', function() {
            var blob = new Blob([csv_data], {type: "text/plain;charset=utf-8"});
            saveAs(blob, "heatmap.csv");
        });
    }

    // add group of samples
    $('#add_group').on('click', function() {
        $('#group2').removeClass('d-none');
        $('#add_group').addClass('d-none');
        $('#info').removeClass('d-none');
    });

    // remove group of samples
    $('#remove_group').on('click', remove_group);
    function remove_group() {
        // clear Choices
        group2.destroy();
        $('li#group2').empty();
        $('li#group2').append(group2_html);
        group2 = new Choices('#second_group', {
            removeItems: true,
            removeItemButton: true,
            noChoicesText: "All samples selected"
        });
        $('#add_group').removeClass('d-none').removeClass('d-none');
        $('#group2').addClass('d-none');
        $('#remove_group').on('click', remove_group);
    }

    // tooltips
    $('#number_of_genes1').tooltip({'delay':0});
    $('#number_of_genes2').tooltip({'delay':0});
});