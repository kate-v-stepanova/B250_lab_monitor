$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    // apply filters
    $("#apply_filters").on('change', function() {
        if(this.checked) {
          $('#data_filters').removeClass('d-none');
        } else {
            $('#data_filters').addClass('d-none');
        }
    });

    if ($("#ma_plot").length != 0) {
        var contrast = $('#ma_plot').attr('data-contrast');
        contrast = contrast.replace(/__/g, ' ');
        var plot_series = $('#ma_plot').attr('data-series');
        plot_series = plot_series.replace(/'/g, '"'); //");
        if (plot_series.length != 0) {
            plot_series = JSON.parse(plot_series);
        }
        var genes = $('#ma_plot').attr('data-genes');
        var xmax = $('#ma_plot').attr('data-xmax');
        var ymax = $('#ma_plot').attr('data-ymax');
        var ymin = -1 * ymax;
        var filters = $('#ma_plot').attr('data-filters');
        var x_axis = {
            title: {
                enabled: true,
                text: 'Normalized counts'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true,
            min: 0,
        }
        var y_axis = {
            title: {
                text: 'Log2 fold change'
            }
        }
        if (filters == "True") {
            if (xmax != "") {
                x_axis["max"] = parseInt(xmax);
            }
            if (ymin != "") {
                y_axis["min"] = parseFloat(ymin);
            }
            if (ymax != "") {
                y_axis["max"] = parseFloat(ymax);
            }
        }
        var ch = Highcharts.chart('ma_plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: contrast
            },
            subtitle: {
                text: "Number of genes: " + genes,
            },
            xAxis: x_axis,
            yAxis: y_axis,
            plotOptions: {
                scatter: {
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '<b>Counts: </b>{point.x:.0f}<br><b>Log2 fc: </b>{point.y:.2f}<br><b>p value: </b>' +
                            '{point.pvalue:.2f}<br><b>Gene name: </b>{point.gene_name}<br><b>Gene ID: </b>{point.gene_id}'
                    }
                },
                series: {
                    turboThreshold: 1000000,
                    marker: {
                        enabled: true,
                        symbol: 'circle',
                        radius: 2
                    },
                    color: "#204060",
                }
            },
            legend: {
                enabled: false
            },
            series: [plot_series]
        });
    }
});