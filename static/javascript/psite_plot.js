$(document).ready(function() {
    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#psite_plot').attr('data-plot-series');
    console.log(PLOT_SERIES);
    if (PLOT_SERIES != undefined) {
        PLOT_SERIES = PLOT_SERIES.replace(/'/g, '"'); //");
        PLOT_SERIES = PLOT_SERIES.replace(/"null"/g, null);

        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
        }
        var contrast = $('#contrast_select').val();
        var samples = contrast.split('__vs__');
        var x_categories = $('#psite_plot').attr('data-x_categories');
        x_categories = x_categories.replace(/'/g, '"'); //");
        x_categories = JSON.parse(x_categories);

        var min_fc = $('#psite_plot').attr('data-min');
        var max_fc = $('#psite_plot').attr('data-max');
        var middle_val = $('#psite_plot').attr('data-max');

        console.log(min_fc);
        console.log(max_fc);
        // removing attributes
        $('#psite_plot').removeAttr('data-plot-series');

        // plot custom legend, because stupid highcharts makes it ugly
        var c = document.getElementById("legend");
        var ctx = c.getContext("2d");

        // Create gradient
        var grd = ctx.createLinearGradient(0,0,150,0);
        grd.addColorStop(0,"#3399ff");
        grd.addColorStop(0.5,"white");
        grd.addColorStop(1,"#ff6666");

        // Fill with gradient
        ctx.fillStyle = grd;
        ctx.fillRect(10,10,150,30);

        // plotting chart
        var chart = Highcharts.chart('psite_plot', {
            chart: {
                type: 'heatmap',
                plotBorderWidth: 1
            },
            title: {
                text: contrast
            },
            xAxis: {
                categories: x_categories,
                labels: {
                    rotation: 270,
                }
            },
            yAxis: {
                categories: ['P-site', 'A-site', 'E-site'],
            },
            colorAxis: {
                min: min_fc,
                max: max_fc,
                startOnTick: false,
                endOnTick: false,

                stops: [ // this is PERCENTAGE!!!
                    [0, '#3399ff'],
                    [0.5, 'white'],
                    [1, '#ff6666'],
                ],
            },

            legend: {
                enabled: false,
//                align: 'bottom',
                layout: 'horizontal',
                margin: 15,
                verticalAlign: 'bottom',
                y: 50,
                symbolHeight: 20
            },

            tooltip: {
                headerFormat: '',
                pointFormat: '<b>Site: </b>{point.site}<br>' +
                             '<b>Codon: </b>{point.codon}<br>' +
                             '<b>AA: </b>{point.Aa}<br>' +
                             '<b>' + samples[0] + ': </b>{point.'+samples[0] + '}<br>' +
                             '<b>' + samples[0] + '_norm: </b>{point.' + samples[0] + '_norm}<br>' +
                             '<b>' + samples[1] + ': </b>{point.'+samples[1] + '}<br>' +
                             '<b>' + samples[1] + '_norm: </b>{point.' + samples[1] + '_norm}<br>' +
                             '<b>log2(' + contrast + '): </b>{point.value}',
            },
            series: [{
                pointPadding: 1,
//                nullColor: '#d3d3d3',
                nullColor: 'white',
                data: PLOT_SERIES
            }]
        });
    }
});