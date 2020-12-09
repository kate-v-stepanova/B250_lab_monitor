$(document).ready(function() {

    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    // initialize multiselect
    var samples = new Choices('#selected_contrasts', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "No contrasts to select"
    });

    var norm = $('#norm').val();

    var p_series = $('#plot').attr('data-pseries');
    if (p_series != undefined  && p_series.length != 0) {
        p_series = p_series.replace(/'/g, '"'); //");
        p_series = p_series.replace(/"null"/g, null);

        if (p_series.length != 0) {
            p_series = JSON.parse(p_series);
        }
        $.each(p_series, function(c, data) {
            var sample = c.split('__vs__')[0];
            var control = c.split('__vs__')[1];
            Highcharts.chart('psite_' + c, {
                chart: {
                    type: 'scatter',
                    zoomType: 'xy'
                },
                plotOptions: {
                    scatter: {
                        marker: {
                            radius: 2,
                        }
                    }
                },
                subtitle: {
                    text: 'P-site signal'
                },
                title: {
                    text: c,
                },
                xAxis: {
                    title: {
                        enabled: true,
                        text: 'log2(' + sample + ')',
                    },
                },
                yAxis: {
                    title: {
                        text: 'log2(' + control + ')',
                    }
                },
                tooltip: {
                    formatter: function (e) {
                        res = '<b>Contrast: </b>' + c + '<br>';
                        res +=  '<b>gene: </b>' + this.point.gene + '<br>' +
                                '<b>' + norm + '(' + sample + '): </b>' + this.point[norm + '_' + sample] + '<br>' +
                                '<b>' + norm + '(' + control + '): </b>' + this.point[norm + '_' + control] + '<br>' +
                                '<b>log2(' + sample + '): </b>' + this.point.x + '<br>' +
                                '<b>log2(' + control + '): </b>' + this.point.y + '<br>';

                        return res;
                    }
                },
                series: p_series[c],
            });
        });
    }
    var a_series = $('#plot').attr('data-aseries');
    if (a_series != undefined  && a_series.length != 0) {
        a_series = a_series.replace(/'/g, '"'); //");
        a_series = a_series.replace(/"null"/g, null);

        if (a_series.length != 0) {
            a_series = JSON.parse(a_series);
        }

        $.each(a_series, function(c, data) {
            var sample = c.split('__vs__')[0];
            var control = c.split('__vs__')[1];
            Highcharts.chart('asite_' + c, {
                chart: {
                    type: 'scatter',
                    zoomType: 'xy'
                },
                plotOptions: {
                    scatter: {
                        marker: {
                            radius: 2,
                        }
                    }
                },
                subtitle: {
                    text: 'A-site signal'
                },
                title: {
                    text: c,
                },
                xAxis: {
                    title: {
                        enabled: true,
                        text: 'log2(' + sample + ')',
                    },
                },
                yAxis: {
                    title: {
                        text: 'log2(' + control + ')',
                    }
                },
                tooltip: {
                    formatter: function (e) {
                        res = '<b>Contrast: </b>' + c + '<br>';
                        res +=  '<b>gene: </b>' + this.point.gene + '<br>' +
                                '<b>' + norm + '(' + sample + '): </b>' + this.point[norm + '_' + sample] + '<br>' +
                                '<b>' + norm + '(' + control + '): </b>' + this.point[norm + '_' + control] + '<br>' +
                                '<b>log2(' + sample + '): </b>' + this.point.x + '<br>' +
                                '<b>log2(' + control + '): </b>' + this.point.y + '<br>';

                        return res;
                    }
                },
                series: a_series[c],
            });
        });
    }
    var e_series = $('#plot').attr('data-eseries');
    if (e_series != undefined  && e_series.length != 0) {
        e_series = e_series.replace(/'/g, '"'); //");
        e_series = e_series.replace(/"null"/g, null);

        if (e_series.length != 0) {
            e_series = JSON.parse(e_series);
        }

        $.each(e_series, function(c, data) {
            var sample = c.split('__vs__')[0];
            var control = c.split('__vs__')[1];
            Highcharts.chart('esite_' + c, {
                chart: {
                    type: 'scatter',
                    zoomType: 'xy'
                },
                plotOptions: {
                    scatter: {
                        marker: {
                            radius: 2,
                        }
                    }
                },
                subtitle: {
                    text: 'E-site signal'
                },
                title: {
                    text: c,
                },
                xAxis: {
                    title: {
                        enabled: true,
                        text: 'log2(' + sample + ')',
                    },
                },
                yAxis: {
                    title: {
                        text: 'log2(' + control + ')',
                    }
                },
                tooltip: {
                    formatter: function (e) {
                        res = '<b>Contrast: </b>' + c + '<br>';
                        res +=  '<b>gene: </b>' + this.point.gene + '<br>' +
                                '<b>' + norm + '(' + sample + '): </b>' + this.point[norm + '_' + sample] + '<br>' +
                                '<b>' + norm + '(' + control + '): </b>' + this.point[norm + '_' + control] + '<br>' +
                                '<b>log2(' + sample + '): </b>' + this.point.x + '<br>' +
                                '<b>log2(' + control + '): </b>' + this.point.y + '<br>';

                        return res;
                    }
                },
                series: e_series[c],
            });

        });
    }

});