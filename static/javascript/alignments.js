$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    var samples = new Choices('#selected_samples', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "All samples selected"
    });

    $('#genes').selectpicker({
        maxOptions: 1,
        width: '100%'
    });

    if ($('#plot').length != 0) {
        var series = $('#plot').attr('data-series').replace(/'/g, '"'); //");
        series = JSON.parse(series);
        gene = $('#plot').attr('data-gene');
        var chart = Highcharts.chart('plot', {
            title: {
                text: 'Reads distribution in CDS. Gene: ' + gene,
            },
            yAxis: {
                title: {
                    text: '# Reads'
                }
            },
            series: series
        });
    }

});