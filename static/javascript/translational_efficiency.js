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

    $('#apply_filter').on('click', function() {
        if ($(this).is(':checked')) {
            $('#filters').removeClass('d-none');
        } else {
            $('#filters').addClass('d-none');
        }
    });

    if ($('#plot').length != 0) {
         var series = $('#plot').attr('data-series');
         series = series.replace(/'/g, '"'); //");
         series = JSON.parse(series);
         y_max = $('#plot').attr('data-ymax');
         y_min = $('#plot').attr('data-ymin');
         var ch = Highcharts.chart('plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: "Translational Efficiency (based on RPKM)"
            },
            xAxis: {
                title: {
                    text: "Log2(RNA-seq)",
                },
            },
            yAxis: {
                title: {
                    text: "Log2(RNA-seq) / Log2(RP)",
                },
                max: y_max,
                min: y_min,
            },
            plotOptions: {
                scatter: {
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '<b>Gene: </b>{point.gene_name}<br><b>RPKM(RNA-seq): </b>{point.rpkm_rna:.2f}<br>' +
                        '<b>RPKM(RP): </b>{point.rpkm_rp:.2f}<br><b>Log2(RNA-seq): </b>{point.log2(rna):.2f}<br>'+
                        '<b>Log2(RP): </b>{point.log2(rp):.2f}<br><b>X (log2(RNA-seq)): </b>{point.x:.2f}<br>' +
                        '<b>Y (log2(RNA-seq) / log2(RP)): </b>{point.y:.2f}'
                    }
                },
                series: {
                    turboThreshold: 1000000,
                    marker: {
                        enabled: true,
                        symbol: 'circle',
                        radius: 2
                    },
                }
            },
            series: series
        });
    }
});

