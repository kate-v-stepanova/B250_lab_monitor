$(document).ready(function() {

    // initializing constants and removing attributes from html elements
    var plots = $('#plots').attr('data-plots');
    plots = plots.replace(/'/g, '"'); //");

    if (plots.length != 0) {
        plots = JSON.parse(plots);
    }
    $('#plots').removeAttr('data-plots');
    for (i=0; i<plots.length; i++) {
        plot_name = plots[i];
        var plot_series1 = $('#1_'+plot_name).attr('data-plot-series');
        var plot_series2 = $('#2_'+plot_name).attr('data-plot-series');

        plot_series1 = plot_series1.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //');
        plot_series2 = plot_series2.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); // ');

        $('#1_'+plot_name).removeAttr('data-plot-series');
        $('#2_'+plot_name).removeAttr('data-plot-series');

        plot_series1 = JSON.parse(plot_series1);
        plot_series2 = JSON.parse(plot_series2);

        chart1 = Highcharts.chart("1_"+plot_name, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: plot_name + ". Distance from start (nt)",
            },
            yAxis: {
                title: {
                    text: 'P-site'
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle'
            },
            plotOptions: {
                series: {
                    label: {
                        connectorAllowed: false
                    },
                    pointStart: -25,
                },
            },
            tooltip: {
                headerFormat: '<b>Sample: {point.sample}</b><br>',
                pointFormat: 'Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series1
        });

        chart2 = Highcharts.chart("2_"+plot_name, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: plot_name + ". Distance from stop (nt)",
            },
            yAxis: {
                title: {
                    text: 'P-site'
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle'
            },

            plotOptions: {
                series: {
                    label: {
                        connectorAllowed: false
                    },
                    pointStart: -25,
                },
            },
            tooltip: {
                headerFormat: '<b>Sample: {point.sample}</b><br>',
                pointFormat: 'Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series2
        });
    }
});
