$(document).ready(function() {
    // close error message
    $('span.close').on('click', function() {
        $(this).parent().parent().parent().addClass('d-none');
    });

    if ($('#plot').length != 0) {
         var series = $('#plot').attr('data-series');
         series = series.replace(/'/g, '"'); //");
         series = JSON.parse(series);
         y_max = $('#plot').attr('data-ymax');
         y_min = $('#plot').attr('data-ymin');
         var ch = Highcharts.chart('plot', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: "Translational Efficiency"
            },
            xAxis: {
                title: {
                    text: "Log2(RNA-seq)",
                },
            },
            yAxis: {
                title: {
                    text: "Log2(FC_TE)",
                },
//                max: y_max,
//                min: y_min,
            },
            plotOptions: {
                scatter: {
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '<b>Gene: </b>{point.gene_id}<br><b>counts(RNA-seq): </b>{point.cntRnaMean:.2f}<br>' +
                        '<b>counts(RP): </b>{point.cntRiboMean:.2f}<br><b>Log2(RNA-seq): </b>{point.log2_RNA:.2f}<br>'+
                        '<b>Log2(RP): </b>{point.log2_RP:.2f}<br><b>pvalue: </b>{point.padj:.2f}'
                    }
                },
                series: {
                    turboThreshold: 1000000,
                    marker: {
                        enabled: true,
                        symbol: 'circle',
                        radius: 2
                    },
                }
            },
            series: series
        });
    }
});

