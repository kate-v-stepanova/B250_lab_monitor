$(document).ready(function() {
    // initializing constants and removing attributes from html elements
    var plots = $('#plots').attr('data-plots').replace(/'/g, '"'); //");
    if (plots.length != 0) {
        plots = JSON.parse(plots);
    }
    $('#plot').removeAttr('data-plots');
    for (i=0; i<plots.length; i++) {
        plot_name = plots[i];
        var plot_series = $('#'+plot_name).attr('data-plot-series').replace(/'/g, '"'); //");
        plot_series = JSON.parse(plot_series);
        $('#'+plot_name).removeAttr('data-plot-series')
        var chart = Highcharts.chart(plot_name, {
            chart: {
                type: 'column',
                zoomType: 'xy'
            },
            title: {
                text: 'Reads per position. ' + plot_name
            },
            xAxis: {
                title: {text: 'Position'},
            },
            yAxis: {
                title: {
                    text: '# Reads'
                }
            },
            plotOptions: {
                series: {
                    lineWidth: 1,
                    turboThreshold: 10000,
                },
                    pointStart: 0,
            },
            tooltip: {
                headerFormat: '<b>' + plot_name + '</b><br>',
                pointFormat: 'Start position: {point.x}<br>Total reads: {point.y}<br>Reads length: <br> • {point.reads_info}',
            },
//            series: plot_series,
            series: [{
                showInLegend: false,
                name: plot_series['name'],
                data: plot_series['data'],
            }],

            exporting: {
                chartOptions: {
                    plotOptions: {
                        series: {
                            dataLabels: {
                                enabled: true
                            }
                        }
                    }
                }
            }
        });
    }
});
