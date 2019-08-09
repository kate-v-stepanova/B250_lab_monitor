$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });


    const choices = new Choices('#selected_samples', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "All samples selected"
    });

    $('#filter_by').change(function() {
        if ($(this).val() === 'list_of_genes') {
            $('#list_of_genes').removeClass('d-none');
            $('#number_of_genes').addClass('d-none');
        } else {
            if (!$('#list_of_genes').hasClass('d-none')) {
                $('#list_of_genes').addClass('d-none');
                $('#number_of_genes').removeClass('d-none');
            }

        }
    });
    var a = $('#inchlib').attr('data-series');
    a = a.replace(/'/g, '"'); //");
    a = JSON.parse(a);
    $('#inchlib').removeAttr('data-series');
    order = $('#inchlib').attr('data-samples');
    order = order.replace(/'/g, '"'); //");
    order = JSON.parse(order);
    $('#inchlib').removeAttr('data-samples');
    window.inchlib = new InCHlib({ //instantiate InCHlib
        target: "inchlib", //ID of a target HTML element
        metadata: true, //turn on the metadata
        draw_row_ids: true,
        max_height: 1200, //set maximum height of visualization in pixels
        width: 1000, //set width of visualization in pixels
        heatmap_colors: "BuWhRd", //set color scale for clustered data
        column_dendrogram: true,
    });
    inchlib.read_data(a);
    inchlib.draw(); //draw cluster heatmap
});