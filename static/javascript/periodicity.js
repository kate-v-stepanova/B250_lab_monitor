$(document).ready(function() {

    // initializing constants and removing attributes from html elements
    var plots = $('#plots').attr('data-plots');
    plots = plots.replace(/'/g, '"'); //");

    if (plots.length != 0) {
        plots = JSON.parse(plots);
    }
    $('#plots').removeAttr('data-plots');
    for (i=0; i<plots.length; i++) {
        sample = plots[i];
        var plot_series1 = $('#1_'+sample).attr('data-plot-series');
        var plot_series2 = $('#2_'+sample).attr('data-plot-series');
        var plot_series3 = $('#3_'+sample).attr('data-plot-series');
        var plot_series4 = $('#4_'+sample).attr('data-plot-series');

        plot_series1 = plot_series1.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //');
        plot_series2 = plot_series2.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); // ');
        plot_series3 = plot_series3.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); // ');
        plot_series4 = plot_series4.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); // ');

        plot_series1 = JSON.parse(plot_series1);
        plot_series2 = JSON.parse(plot_series2);
        plot_series3 = JSON.parse(plot_series3);
        plot_series4 = JSON.parse(plot_series4);

        $('#1_'+sample).removeAttr('data-plot-series');
        $('#2_'+sample).removeAttr('data-plot-series');
        $('#3_'+sample).removeAttr('data-plot-series');
        $('#4_'+sample).removeAttr('data-plot-series');

        chart1 = Highcharts.chart("1_"+sample, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: "",
            },
            yAxis: [{
                title: {
                    text: 'Read Length'
                }
            }, {
                className: "h5",
                title: {
                    text: "5' end",
                }
            }],
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom'
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
                headerFormat: '',
                pointFormat: '<b>{point.sample}</b><br>Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series1
        });

        chart2 = Highcharts.chart("2_"+sample, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: "",
            },
            yAxis: {
                title: {
                    text: 'Read Length'
                }
            },

            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom'
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
                headerFormat: '',
                pointFormat: '<b>{point.sample}</b><br>Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series2
        });

        chart3 = Highcharts.chart("3_"+sample, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: "",
            },

            yAxis: [{
                title: {
                    text: 'Read Length'
                }
            }, {
                className: "h5",
                title: {
                    text: "3' end",
                }
            }],
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom'
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
                headerFormat: '',
                pointFormat: '<b>{point.sample}</b><br>Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series3
        });

        chart4 = Highcharts.chart("4_"+sample, {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: "",
            },
            yAxis: {
                title: {
                    text: 'Read Length'
                }
            },

            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom'
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
                headerFormat: '',
                pointFormat: '<b>{point.sample}</b><br>Length: {point.length}<br>Distance: {point.x}<br>Count: {point.y}<br>Region: {point.region}<br>End: {point.end}',
            },
            series: plot_series4
        });
    }
});
