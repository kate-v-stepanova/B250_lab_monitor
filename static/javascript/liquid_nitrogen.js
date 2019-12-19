$(document).ready(function() {

    // edit fields of cell line
    $.fn.editable.defaults.mode = 'inline';
    $('#cell_line_ID').editable();
    $('#comments').editable({
       type:  'textarea',
    });
    $('#protocol').editable({
        type: 'select',
        value: $('#protocol').text(),
        source: [
              {value: 'New', text: 'New'},
              {value: 'Old', text: 'Old'},
              {value: 'N/A', text: 'N/A'}
           ]
    });

    $('#cell_line_ID').on('change', function(e, editable) {

        today = new Date();


        console.log(today);
        $('#date').text(today.getDate() + '.' + today.getMonth() + '.' + today.getFullYear());
    });
    
    Highcharts.chart('towers', {
//        colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572',
//             '#FF9655', '#FFF263', '#6AF9C4'],
        colors: [Highcharts.getOptions().colors[0]],
        chart: {
            type: 'column',
            height: 420,
            width: 200,
            marginRight: 0,
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['Tower 7']
        },
        yAxis: {
            min: 0,
            title: {
                text: ''
            },
//            labels: {
//                formatter: function () {
//                    return 'Rack' + this.value;
//                }
//            },
            labels: [],
            tickPositions: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        },
        tooltip: {
            headerFormat: "",
            pointFormat: '{series.name}',
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                events: {
                    click: showRackContent,
                }
            },
            series: {
                    allowPointSelect: true,
            },
        },
        exporting: {
            enabled: false,
        },
        legend: false,
        series: [{
            name: 'Rack9',
            data: [1],
            rack: 9,
        }, {
            name: 'Rack8',
            data: [1],
        }, {
            name: 'Rack7',
            data: [1],
        }, {
            name: 'Rack6',
            data: [1],
        }, {
            name: 'Rack5',
            data: [1],
        }, {
            name: 'Rack4',
            data: [1],
        }, {
            name: 'Rack3',
            data: [1],
        }, {
            name: 'Rack2',
            data: [1],
        }, {
            name: 'Rack1',
            data: [1],
        }]
    });

    var rack_series = $('#rack').attr('data-series');
    rack_series = rack_series.replace(/'/g, '"'); //");
    rack_series = JSON.parse(rack_series);

    var cell_lines = $('#cell_lines').attr('data-cell_lines');
    cell_lines = cell_lines.replace(/'/g, '"'); //");
    cell_lines = JSON.parse(cell_lines);

    function showRackContent(e) {
        var rack = this.name;
        data = rack_series[rack];
        if (data == undefined) {
            data = [
            {'x': 0, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 0, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 1, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 2, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 3, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 4, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 5, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 6, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 7, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 8, 'value': 0, 'color': '#FFFFFF'},
            {'x': 0, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 1, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 2, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 3, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 4, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 5, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 6, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 7, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 8, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            {'x': 9, 'y': 9, 'value': 0, 'color': '#FFFFFF'},
            ]
        }
        $('#cell_lines').find('table').addClass('d-none');
        $('#cell_lines').find('p').addClass('d-none');
        $('#save_changes').addClass('d-none');
        Highcharts.chart('rack', {
            chart: {
                type: 'heatmap',
                height: 450,
                width: 430,
            },
            title: {
                text: this.name,
            },
            xAxis: {
                categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            },
            yAxis: {
                categories: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
                title: {
                    text: ''
                }
            },
            legend: false,
            exporting: {
                enabled: false,
            },
            series: [{
                 tooltip: {
                    headerFormat: '',
                    pointFormat: '<b>Rack{point.Rack}, {point.pos}</b><br>{point.ID}<br>(click to see details)'
                },
                borderWidth: 1,
                data: data,
                events: {
                    click: show_cell_line_details
                },
                allowPointSelect: true,
            }],
        });
    }

    function show_cell_line_details(e) {
        var cell_line = e.point.ID;
        $('#cell_lines').find('table').removeClass('d-none');
        $('#cell_lines').find('p.h5').removeClass('d-none');
        $('#save_changes').removeClass('d-none');
        $('#cell_lines').find('p.h5').text('Rack' + e.point.Rack);
        if (e.point.value == 0) {
            $('#cell_lines').find("td[id]").text('');
        } else {
            data = cell_lines[cell_line];
            $('#cell_line_ID').text(data['ID']);
            $('#cell_line').text(data['Cell line']);
            $('#media').text(data['Media (Freezing Medium)']);
            $('#plasmid').text(data['Transferred plasmid']);
            $('#selection').text(data['Selection']);
            $('#type').text(data['Typ']);
            $('#biosafety').text(data['Biosafety Level']);
            $('#mycoplasma').text(data['Mycoplasma checked']);
            $('#source').text(data['Source']);
            $('#date').text(data['Date']);
            $('#responsible').text(data['Responsible person']);
            $('#comments').text(data['Comments']);
        }
        $('#location').text('Rack' + e.point.Rack + ", " + e.point.pos);
    }

    // edit fields of cell line
    $.fn.editable.defaults.mode = 'inline';
    $('#cell_line_ID').editable();
    $('#comments').editable({
       type:  'textarea',
    });
    $('#protocol').editable({
        type: 'select',
        value: $('#protocol').text(),
        source: [
              {value: 'New', text: 'New'},
              {value: 'Old', text: 'Old'},
              {value: 'N/A', text: 'N/A'}
           ]
    });

    $('#cell_line_ID').on('change', function(e, editable) {

        today = new Date();


        console.log(today);
        $('#date').text(today.getDate() + '.' + today.getMonth() + '.' + today.getFullYear());
    });
});
