$(document).ready(function() {

    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    // initialize multiselect
    new Choices('#selected_contrasts', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "No contrasts to select"
    });

    // genes multiselect
    new Choices('#search_gene', {
        removeItems: true,
        removeItemButton: true,
        noChoicesText: "No genes to select"
    });

    function plot_psite(site, p_series){
        // site should be: psite, esite or asite
        // series = {'contrast': [{'name': 'all_points', 'data': data}, {'name': 'Above threshold', 'data': data}]
        $.each(p_series, function(contrast, data) {
            var sample = contrast.split('__vs__')[0];
            var control = contrast.split('__vs__')[1];
            var div_id = site + '_' + contrast;
            var plot_title = site.replace('psite', 'P-site').replace('asite', 'A-site').replace('esite', 'E-site') + ' signal';
            Highcharts.chart(div_id, {
                chart: {
                    type: 'scatter',
                    zoomType: 'xy',
                },
                plotOptions: {
                    scatter: {
                        marker: {
                            radius: 2,
                            symbol: 'circle',
                        }
                    }
                },
                subtitle: {
                    text: plot_title,
                },
                title: {
                    text: contrast,
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
                        res = '<b>Contrast: </b>' + contrast + '<br>';
                        res +=  '<b>gene: </b>' + this.point.gene + '<br>' +
                                '<b>' + norm + '(' + sample + '): </b>' + this.point[norm + '_' + sample] + '<br>' +
                                '<b>' + norm + '(' + control + '): </b>' + this.point[norm + '_' + control] + '<br>' +
                                '<b>log2(' + sample + '): </b>' + this.point.x + '<br>' +
                                '<b>log2(' + control + '): </b>' + this.point.y + '<br>';

                        return res;
                    }
                },
                series: p_series[contrast],
            });
        });
    };

    var norm = $('#norm').val();

    var p_series = $('#plot').attr('data-pseries');
    if (p_series != undefined  && p_series.length != 0) {
        p_series = p_series.replace(/'/g, '"'); //");
        p_series = p_series.replace(/"null"/g, null);

        if (p_series.length != 0) {
            p_series = JSON.parse(p_series);
        }
        plot_psite('psite', p_series);
    }
    var a_series = $('#plot').attr('data-aseries');
    if (a_series != undefined  && a_series.length != 0) {
        a_series = a_series.replace(/'/g, '"'); //");
        a_series = a_series.replace(/"null"/g, null);

        if (a_series.length != 0) {
            a_series = JSON.parse(a_series);
        }
        plot_psite('asite', a_series);
    }
    var e_series = $('#plot').attr('data-eseries');
    if (e_series != undefined  && e_series.length != 0) {
        e_series = e_series.replace(/'/g, '"'); //");
        e_series = e_series.replace(/"null"/g, null);

        if (e_series.length != 0) {
            e_series = JSON.parse(e_series);
        }
        plot_psite('esite', e_series);
    }

    // search genes
    $(document).on('click', '#select_genes', function() {
        var search_genes = $('#search_gene').val();
        var url = window.location.href + "/search_genes";
        var selected_contrasts = $('#selected_contrasts').val();
        var selected_aa = $('#amino_acid').val();
        var norm = $('#norm').val();
        var fc_highlight = $('#fc_highlight').val();
        var genes_highlight = $('#genes_highlight').val();
        var data = {
            'search_genes': search_genes,
            'selected_contrasts': selected_contrasts,
            'selected_aa': selected_aa,
            'norm': norm,
            'fc_highlight': fc_highlight,
            'genes_highlight': genes_highlight,
        };
        $.ajax({
            type: "POST",
            url: url,
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function(response) {
            var p_series = response['p_series'];
            var a_series = response['a_series'];
            var e_series = response['e_series'];
            $(".plot_container").empty();
            plot_psite('psite', p_series);
            plot_psite('esite', e_series);
            plot_psite('asite', a_series);
        }).fail(function(response) {
            console.log(response);
            alert('Error!');
        });
    });

});