$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    if ($("#heatmap").length != 0) {
        var plot_series = $('#heatmap').attr('data-series');
        plot_series = plot_series.replace(/'/g, '"'); //");
        if (plot_series.length != 0) {
            plot_series = JSON.parse(plot_series);
        }
        var x_cat = $('#heatmap').attr('data-xcat');
        x_cat = x_cat.replace(/'/g, '"'); //");
        x_cat = JSON.parse(x_cat);
        var y_cat = $('#heatmap').attr('data-ycat');
        y_cat = y_cat.replace(/'/g, '"'); //");
        y_cat = JSON.parse(y_cat);
        var z = $('#heatmap').attr('data-z');
        z = z.replace(/'/g, '"'); //");
        z = JSON.parse(z);
        var zmax = $('#heatmap').attr('data-zmax');
        zmax = parseInt(zmax);
        var data = [
            {
                z: z,
                x: x_cat,
                y: y_cat,
                type: 'heatmap',
                hovertemplate: "<b>Contrast: </b>%{x}<br><b>Gene: </b>%{y}<br><b>Fold Change: </b>%{z:,.4f}",
                zmin: -1*zmax,
                zmax: zmax,
                colorscale: [
                    ['0.0', 'rgb(0, 102, 204)'],
                    ['0.5', 'rgb(255, 255, 200)'],
                    ['1.0', 'rgb(225, 60, 45)'],
                ],
            }
        ];
        var layout = {
            height: y_cat.length * 25,
            width: x_cat.length * 120,
        }
        Plotly.newPlot('heatmap', data, layout);
    }

});