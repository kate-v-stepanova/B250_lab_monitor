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

    // initializing constants and removing attributes from html elements
    var PLOT_SERIES = $('#psite_plot').attr('data-plot-series');

    if (PLOT_SERIES != undefined && PLOT_SERIES.length != 0) {
        PLOT_SERIES = PLOT_SERIES.replace(/'/g, '"'); //");
        PLOT_SERIES = PLOT_SERIES.replace(/"null"/g, null);

        if (PLOT_SERIES.length != 0) {
            PLOT_SERIES = JSON.parse(PLOT_SERIES);
        }

        var x_categories = $('#psite_plot').attr('data-x_categories');

        x_categories = x_categories.replace(/'/g, '"'); //");
        x_categories = JSON.parse(x_categories);

        var y_categories = $('#psite_plot').attr('data-y_categories');
        y_categories = y_categories.replace(/'/g, '"'); //");
        y_categories = JSON.parse(y_categories);

        var dataset_id = $('#psite_plot').attr('data-dataset_id');

        var min_fc = $('#psite_plot').attr('data-min');
        var max_fc = $('#psite_plot').attr('data-max');
        var middle_val = $('#psite_plot').attr('data-max');
        var norm = $('#psite_plot').attr('data-norm');

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
                text: 'Dataset: ' + dataset_id,
            },
            xAxis: {
                categories: x_categories,
                labels: {
                    rotation: 270,
                }
            },
            yAxis: {
                categories: y_categories,
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
                layout: 'horizontal',
                margin: 15,
                verticalAlign: 'bottom',
                y: 50,
                symbolHeight: 20
            },
            tooltip: {
                formatter: function (e) {
                    var contrast = this.point.contrast;
                    var s1 = contrast.split('__vs__')[0];
                    var s2 = contrast.split('__vs__')[1];
                    res = '<b>Contrast: </b>' + this.point.contrast + '<br>' +
                            '<b>Site: </b>' + this.point.site + '<br>'
                    if (this.point.codon != undefined) {
                        res += '<b>Codon: </b>' + this.point.codon + '<br>'
                    }
                    res +=  '<b>AA: </b>' + this.point.aa + '<br>' +
                            '<b>' + s1 + ': </b>' + this.point[s1] + '<br>' +
                            '<b>' + s2 + ': </b>' + this.point[s2] + '<br>' +
                            '<b>' + norm + '(' + s1 + '): </b>' + this.point[norm + '_' + s1] + '<br>' +
                            '<b>' + norm + '(' + s2 + '): </b>' + this.point[norm + '_' + s2] + '<br>' +
                            '<b>(' + s1 + ' - ' + s2 + ') / ' + s2 + ': </b>' + this.point.value;
                    return res;
                }
            },
            series: [{
                pointPadding: 1,
                nullColor: 'white',
                data: PLOT_SERIES,
                borderWidth: 1,
            }]
        });
    }
});
