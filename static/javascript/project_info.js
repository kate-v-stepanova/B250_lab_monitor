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
                Highcharts.chart('plot_div', {
                    chart: {
                        type: 'column',
                    },
                    title: {
                        text: 'Reads per sample',
                    },
                    tooltip: {
                        headerFormat: '',
                        pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
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
                    series: JSON.parse(data)
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



    $('#hide_plot').on('click', function() {
        $(this).addClass('d-none');
        $('#plot_div').addClass('d-none');
    });
});