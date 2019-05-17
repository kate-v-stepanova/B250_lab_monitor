$(document).ready(function() {
    var samples = $('#samples').attr('data-samples');
    samples = samples.replace(/'/g, '"'); //");
    samples = JSON.parse(samples);
    for (i=0; i<samples.length;i++) {
        sample = samples[i];
        // get 4 plots
        var start_5p_data = $('#'+sample+"_start_5p").attr('data-plot-series');
        start_5p_data = start_5p_data.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //")
        start_5p_data = JSON.parse(start_5p_data);
        var stop_5p_data = $('#'+sample+"_stop_5p").attr('data-plot-series');
        stop_5p_data = stop_5p_data.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //")
        stop_5p_data = JSON.parse(stop_5p_data);
        var start_3p_data = $('#'+sample+"_start_3p").attr('data-plot-series');
        start_3p_data = start_3p_data.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //"
        start_3p_data = JSON.parse(start_3p_data);
        var stop_3p_data = $('#'+sample+"_stop_3p").attr('data-plot-series');
        stop_3p_data = stop_3p_data.replace(/'/g, '"').replace(/3"/g, "3'").replace(/5"/g, "5'"); //"'
        stop_3p_data = JSON.parse(stop_3p_data);
        // delete attributes
        $('#'+sample+"_start_5p").removeAttr('data-plot-series');
        $('#'+sample+"_stop_5p").removeAttr('data-plot-series');
        $('#'+sample+"_start_3p").removeAttr('data-plot-series');
        $('#'+sample+"_stop_3p").removeAttr('data-plot-series');
        // plot data
        chart1 = Highcharts.chart(sample+'_start_5p', {
            chart: {
                type: 'heatmap',
            },
            title: {
                text: '',
            },
            xAxis: {
                title: {
                    text: "Distance from start (nt)"
                }
            },
            yAxis: [{
                title: {
                    text: 'Read Length'
                },
                tickPositions: [22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                min: 22,
                max: 31,
            }, {
                className: "h5",
                title: {
                    text: "5' end",
                }
            }],

            colorAxis: {
                stops: [
                    [0, 'white'],
                    [0.1, '#666666'],
                    [0.2, '#333333'],
                    [1, 'black']
                ],
                min: 0,
                max: 2000,
                startOnTick: false,
                endOnTick: false,
            },
            series: [{
                    turboThreshold: 10000,
                    data: start_5p_data,
            }]
        });
        chart2 = Highcharts.chart(sample+'_stop_5p', {
            chart: {
                type: 'heatmap',
            },
            title: {
                text: ''
            },
            xAxis: {
                title: {
                    text: "Distance from start (nt)"
                }
            },
            yAxis: {
                title: {
                    text: "Read Length"
                },
                tickPositions: [22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                min: 22,
                max: 31,
            },

            colorAxis: {
                stops: [
                    [0, 'white'],
                    [0.1, '#666666'],
                    [0.2, '#333333'],
                    [1, 'black']
                ],
                min: 0,
                max: 2000,
                startOnTick: false,
                endOnTick: false,
            },
            series: [{
                    turboThreshold: 10000,
                    data: stop_5p_data,
            }]
        });
        chart3 = Highcharts.chart(sample+'_start_3p', {
            chart: {
                type: 'heatmap',
            },
            title: {
                text: ''
            },
            legend: {
                enabled: false
            },
            xAxis: {
                title: {
                    text: "Distance from start (nt)"
                }
            },
            yAxis: [{
                title: {
                    text: 'Read Length'
                },
                tickPositions: [22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                min: 22,
                max: 31,
            }, {
                className: "h5",
                title: {
                    text: "3' end",
                }
            }],

            colorAxis: {
                stops: [
                    [0, 'white'],
                    [0.1, '#666666'],
                    [0.2, '#333333'],
                    [1, 'black']
                ],
                min: 0,
                max: 2000,
                startOnTick: false,
                endOnTick: false,
            },
            series: [{
                    turboThreshold: 10000,
                    data: start_3p_data,
            }]
        });
        chart4 = Highcharts.chart(sample+'_stop_3p', {
            chart: {
                type: 'heatmap',
            },
            title: {
                text: ''
            },
            xAxis: {
                title: {
                    text: "Distance from start (nt)"
                }
            },
            yAxis: {
                title: {
                    text: "Read Length"
                },
                tickPositions: [22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                min: 22,
                max: 31,
                reversed: true
            },

            colorAxis: {
                stops: [
                    [0, 'white'],
                    [0.1, '#666666'],
                    [0.2, '#333333'],
                    [1, 'black']
                ],
                min: 0,
                max: 2000,
                startOnTick: false,
                endOnTick: false,
            },
            series: [{
                    turboThreshold: 10000,
                    data: stop_3p_data,
            }]
        });
    }
});