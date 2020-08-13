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
        var one_plot = $('#plot').attr('data-one_plot');
        console.log(one_plot);
        var series = $('#plot').attr('data-series').replace(/'/g, '"'); //");
        series = JSON.parse(series);
        gene = $('#plot').attr('data-gene');
        var normalization = $('#normalization').val();
        if (one_plot == 'one_plot') {
            var chart = Highcharts.chart('plot', {
                chart: {
                    type: 'column',
                    zoomType: 'x',
                    panning: true,
                    panKey: 'shift',
                },
                title: {
                    text: 'Density plot. Gene: ' + gene,
                },
                yAxis: {
                    title: {
                        text: '# Reads (' + normalization + ')',
                    }
                },
                tooltip: {
                    formatter: function () {
                        return '<b>Condition: </b>' + this.series.name + '<br><b>Position: </b>' + this.x +
                        '<br><b>Counts: </b>' + this.y + ' (' + normalization + ')';
                    }
                },
                series: series,
            });
        } else {
            for (i=0; i<series.length; i++) {
                var sample = series[i]['name'];
                var chart = Highcharts.chart('plot_'+sample, {
                    chart: {
                        type: 'column',
                        zoomType: 'x',
                        panning: true,
                        panKey: 'shift'
                    },
                    title: {
                        text: 'Density plot. Gene: ' + gene + 'Sample: ' + sample,
                    },
                    yAxis: {
                        title: {
                            text: '# Reads (' + normalization + ')',
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            return '<b>Condition: </b>' + this.series.name + '<br><b>Position: </b>' + this.x +
                            '<br><b>Counts: </b>' + this.y + ' (' + normalization + ')';
                        }
                    },
                    series: [series[i]],
                });
            }
        }
    }
});