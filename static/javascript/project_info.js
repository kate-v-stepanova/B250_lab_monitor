$(document).ready(function() {
    $.fn.editable.defaults.mode = 'inline';
    $('#project_name').editable();
    $('#description').editable({
       type:  'textarea',
    });
    $('#prepared_by').editable();
    $('#protocol').editable({
        type: 'select',
        value: $('#protocol').text(),
        source: [
              {value: 'New', text: 'New'},
              {value: 'Old', text: 'Old'},
              {value: 'N/A', text: 'N/A'}
           ]
    });

    $('#save_project').on("click", function() {
        var data = {};
        $('.editable-unsaved').each(function() {
            var el_id = $(this).attr('id');
            data[el_id] = $('#'+el_id).text();
        });
        if ($.isEmptyObject(data)) {
            alert("Project info has not been changed")
        } else {
            var url = $(location).attr('href');
            $.post(url, data, function(data, status) {
                $('.editable-unsaved').removeClass('editable-unsaved');
                alert('Successfully updated');
            });
        }
    });

    $('#bc_split_stats').on('click', function() {
        var stats = $(this).text();
        var project_id = $(location).attr("href").split('/').pop();
        var url = "/" + stats + "/" + project_id;
        $.post(url, function(data) {
            if (data.length != 0) {
                data = JSON.parse(data);
                samples = data['samples'];
                Highcharts.chart('plot_div', {
                    chart: {
                        type: 'column',
                    },
                    title: {
                        text: 'Reads per sample',
                    },
                    xAxis: {
                        categories: samples,
                    },
                    yAxis: {
                        title: {
                            text: "# Reads"
                        }
                    },
                    tooltip: {
                        shared: true,
                        headerFormat: 'Total: {series.total} {point.stackTotal}<br>',
                        //pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            pointWidth: 60
                        }
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        itemMarginBottom: 5,
                    },
                    exporting: {
                        filename: project_id + '_bc_split_stats'
                    },
                    series: data['series']
                });
                $('#plot_div').removeClass('d-none');
                $('#hide_plot').removeClass('d-none');
            }
        });
    });

    $('#cutadapt_stats').on('click', function() {
        var stats = $(this).text();
        var project_id = $(location).attr("href").split('/').pop();
        var url = "/" + stats + "/" + project_id;
        $.post(url, function(data) {
            if (data.length != 0) {
                Highcharts.chart('plot_div', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'Cutadapt stats'
                    },

                    yAxis: {
                        title: {
                            text: "# Reads"
                        }
                    },
                    tooltip: {
                        shared: true,
                        headerFormat: ''
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        itemMarginBottom: 15,
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            pointWidth: 60,
                        }
                    },
                    exporting: {
                        filename: project_id + '_cutadapt_stats'
                    },
                    series: JSON.parse(data)
                });
                $('#plot_div').removeClass('d-none');
                $('#hide_plot').removeClass('d-none');
            }
        });
    });

    $('#transcript_regions').on('click', function() {
        var project_id = $(location).attr('href').split('/').pop();
        var url = "/transcript_regions/" + project_id;
        $.post(url, function(data) {
            if (data.length != 0) {
                data = JSON.parse(data);
                series = data["series"];
                samples = data["samples"];
                Highcharts.chart('plot_div', {
                    chart: {
                        type: "column",
                    },
                    colors: ["#b3d9ff", "#538cc6", "#0077b3", "#204060"],
                    title: {
                        text: 'Distribution of reads in transcript regions'
                    },

                    xAxis: {
                        categories: samples
                    },
                    yAxis: {
                        title: {
                            text: "# Reads"
                        }
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            pointWidth: 40,
                        },
                    },
                    tooltip: {
                        shared: true,
                        headerFormat: '<b>{point.key}</b><br>'
                    },
                    exporting: {
                        filename: project_id + "_transcript_regions"
                    },
                    series: series,
                });

                $('#plot_div').removeClass('d-none');
                $('#hide_plot').removeClass('d-none');
            }
        });
    });


    $('#diricore_stats').on('click', function() {
        var project_id = $(location).attr('href').split('/').pop();
        var url = "/diricore_stats/" + project_id;
        $.post(url, function(data) {
            if (data.length != 0) {
                data = JSON.parse(data);
                series = data["series"];
                samples = data["samples"];
                Highcharts.chart('plot_div', {
                    chart: {
                        type: "bar",
                    },
                    title: {
                        text: 'Diricore stats'
                    },

                    xAxis: {
                        categories: samples
                    },
                    yAxis: {
                        title: {
                            text: "# Reads"
                        }
                    },
                    plotOptions: {
                        series: {
                            stacking: 'normal'
                        }
                    },
                    tooltip: {
                        shared: true,
                        headerFormat: '<b>{point.key}</b><br>Total: {point.total}<br>',

                    },
                    exporting: {
                        filename: project_id + "_diricore_stats"
                    },
                    series: series,
                });

                $('#plot_div').removeClass('d-none');
                $('#hide_plot').removeClass('d-none');
            }
        })
    });

    $('#rrna_genes').on('click', function() {
        var project_id = $(location).attr("href").split('/').pop();
        var url = "/rrna_genes/" + project_id;
        $.post(url, function(data) {
            data = JSON.parse(data);
            series = data["series"];
            samples = data["samples"];
            Highcharts.chart('plot_div', {
                chart: {
                    type: 'column',
                },
                colors: ["#538cc6", "#0077b3", "#204060"],
                title: {
                    text: "rRNA genes",
                },
                xAxis: {
                    categories: samples
                },
                yAxis: {
                    title: {
                        text: "# Reads"
                    }
                },
                plotOptions: {
                    series: {
                        stacking: 'normal',
                    }
                },
                tooltip: {
                    shared: true,
                    headerFormat: "",
                },
                exporting: {
                    filename: project_id + "_rRNA_genes"
                },
                series: series
            });

            $('#plot_div').removeClass('d-none');
            $('#hide_plot').removeClass('d-none');
        });
    });

    $('#hide_plot').on('click', function() {
        $(this).addClass('d-none');
        $('#plot_div').addClass('d-none');
    });
});