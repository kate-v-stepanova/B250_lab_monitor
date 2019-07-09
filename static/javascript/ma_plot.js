$(document).ready(function() {
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    if ($("div.ma_plot").length != 0) {
        var contrast = $('div.ma_plot').attr('data-contrast');
        contrast = contrast.replace(/__/g, ' ');
        var plot_series = $('div.ma_plot').attr('data-series');
        plot_series = plot_series.replace(/'/g, '"'); //");
        if (plot_series.length != 0) {
            plot_series = JSON.parse(plot_series);
        }
        Highcharts.chart('ma_plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: contrast
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: 'Mean of normalized counts'
                },
                startOnTick: true,
                endOnTick: true,
                showLastLabel: true,
                min: 0
            },
            yAxis: {
                title: {
                    text: 'Log2 fold change'
                }
            },

            plotOptions: {
                scatter: {
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '<b>Counts: </b>{point.x:.2f}<br><b>Log2 fc: </b>{point.y:.2f}<br><b>Transcript: </b>{point.transcript}'
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
            series: [plot_series]
        });
    }
});