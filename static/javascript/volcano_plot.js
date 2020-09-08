$(document).ready(function() {
    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#volcano_plot').attr('data-plot-series').replace(/'/g, '"'); //");
    if (PLOT_SERIES.length != 0) {
        PLOT_SERIES = JSON.parse(PLOT_SERIES);
    }
    var contrast = $('#contrast_select').val();
    var left = $('#volcano_plot').attr('data-left-line');
    var right = $('#volcano_plot').attr('data-right-line');
    var bottom = $('#volcano_plot').attr('data-bottom-line');

    // removing attributes
    $('#volcano_plot').removeAttr('data-plot-series');

    // plotting chart
    var chart = Highcharts.chart('volcano_plot', {
        chart: {
            type: 'scatter',
            zoomType: 'xy',
            height: 600,
        },
        legend: {
            enabled: false
        },
        title: {
            text: 'Differential expression for samples: <b>' + contrast + '</b>'
        },
        xAxis: {
            title: {
                text: 'log2(fc)'
            },
            plotLines: [{
                color: 'black',
                dashStyle: 'dash',
                value: right,
                width: 1,
                label: {
                    text: 'log2(fc)=' + right,
                }
            },
            {
                color: 'black',
                dashStyle: 'dash',
                value: left,
                width: 1,
                label: {
                    text: 'log2(fc)=' + left,
                }
            }]
        },
        yAxis: {
            title: {
                text: '-log10(pval)'
            },
            plotLines: [{
                color: 'black',
                dashStyle: 'dash',
                value: bottom,
                width: 1,
                label: {
                    text: '-log10(pval)=' + bottom,
                }
            }]
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 5,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    headerFormat: '<b>contrast: ' + contrast+'</b><br>',
                    pointFormatter: function() {
                        var log_10;
                        if (this.infinity == true) {
                            log_10 = 'plus infinity'
                        } else {
                            log_10 = this.y
                        }
                        return '<b>gene: ' + this.gene + '</b><br>' +
                        '<b>-log10(pval):</b>' + this.x + '<br><b>log2(fc):</b> ' + log_10 +'<br>' +
                            '<b>pvalue:</b>' + this.pvalue + '<br><b>fc:</b> ' + this.fc;
                    },
                }
            }
        },
        series: PLOT_SERIES,
    });
});