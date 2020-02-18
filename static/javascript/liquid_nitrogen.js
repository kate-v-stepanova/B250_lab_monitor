$(document).ready(function() {

    // edit fields of cell line
    $.fn.editable.defaults.mode = 'inline';
    $('#comments').editable({
       type:  'textarea',
    });
    $('#responsible_name').editable();
    $('#date').editable();

    var cell_lines_dropdown = $('#cell_lines').attr('data-dropdown');
    cell_lines_dropdown = cell_lines_dropdown.replace(/'/g, '"'); //");
    cell_lines_dropdown = JSON.parse(cell_lines_dropdown);

    function validate_cell_line(value) {
        // that's not exactly how this function is supposed to be used,
        // but I couldn't find any other way to update the other fields.

        // show modal -> to enter responsible name and comments
        // after entering, click OK and call $('#modal-ok').on('click') function
        if (value == 'add_new') {
            $('#new_cell_line').modal();
            /*
                // here will be processed modal inputs
            */
            value = $('#new_cell_line_id').val();
        } else {
            $('#modal-2').modal();
            /*
                // here will be processed modal inputs
            */
        }
        var cell_line = cell_lines[value];



        // then update fields
        $('#cell_line').text(cell_line['Cell line']);
        $('#media').text(cell_line['Media (Freezing Medium)']);
        $('#plasmid').text(cell_line['Transferred plasmid']);
        $('#selection').text(cell_line['Selection']);
        $('#type').text(cell_line['Typ']);
        $('#biosafety').text(cell_line['Biosafety Level']);
        $('#mycoplasma').text(cell_line['Mycoplasma checked']);
        $('#source').text(cell_line['Source']);
        // mark with bold (updated values)
        $('#cell_line_ID').addClass('font-weight-bold');
    }

    $('#cell_line_ID').editable({
        type: 'select',
        value: $('#cell_line_ID').text(),
        source: cell_lines_dropdown,
        emptytext: 'Empty',
        validate: validate_cell_line,
    });

    $('#create_new').on('click', function(e) {
        var data = {
            'new_id': $('#new_cell_line_id').val(),
            'new_name': $('#new_cell_line_name').val(),
            'media': $('#new_media').val(),
            'plasmid': $('#new_plasmid').val(),
            'selection': $('#new_selection').val(),
            'type': $('#new_type').val(),
            'biosafety': $('#new_biosafety').val(),
            'mycoplasma': $('#new_mycoplasma').val(),
            'source': $('#new_source').val(),
        }

        var url = window.location.href + "/create_cell_line";
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function() {
            alert( "success" );
          }).fail(function() {
            alert( "error" );
          })

    });

    $('#modal-ok').on('click', function(e) {
        var resp = $('#responsible-2').val();
        var comments = $('#comments-2').val();
        var today = get_today();
        $('#date').text(today);
        $('#responsible_name').text(resp);
        $('#comments').text(comments);
        if (resp == "") {
            $('#error').text('Please enter your name. Name is required');
            $('#error').removeClass('d-none');
        }

        // mark with bold (updated values)
        $('#responsible_name').addClass('font-weight-bold');
        $('#date').addClass('font-weight-bold');
        if (comments != "") {
            $('#comments').addClass('font-weight-bold');
        }

        // close modal and clear input
        if (resp != "") {
            $('#modal-2').modal('hide');
            $('#responsible-2').val('');
            $('#comments-2').val('');
        }
    });


    $('#modal-cancel').on('click', function(e) {
        // load previous values
        var prev_val = $('#cell_line').attr('data-unchanged-val');
        var val = 1;
        if (prev_val == "" || prev_val == undefined) {
            val = 0;
        }
        var location = $('#location').text(); // Rack3, B9
        var rack = location.split(', ')[0].replace('Rack', '');
        var pos = location.split(', ')[1];
        var ee = {point: {ID: prev_val, value: val, Rack: rack, pos: pos}}
        show_cell_line_details(ee);
    });

    Highcharts.chart('towers', {
//        colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572',
//             '#FF9655', '#FFF263', '#6AF9C4'],
        colors: [Highcharts.getOptions().colors[0]],
        chart: {
            type: 'column',
            height: 420,
            marginRight: 0,
            marginLeft: 0,
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['tower7', 'tower8', 'tower9', 'tower10']
        },
        yAxis: {
            min: 0,
            title: {
                text: ''
            },
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
                    groupPadding: 0,
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
            data: [1, 1],
        }, {
            name: 'Rack7',
            data: [1, 1],
        }, {
            name: 'Rack6',
            data: [1, 1, 1, 1],
        }, {
            name: 'Rack5',
            data: [1, 1, 1, 1],
        }, {
            name: 'Rack4',
            data: [1, 1, 1, 1],
        }, {
            name: 'Rack3',
            data: [1, 1, 1, 1],
        }, {
            name: 'Rack2',
            data: [1, 1, 1, 1],
        }, {
            name: 'Rack1',
            data: [1, 1, 1, 1],
        },
        ]
    });

    var rack_series = $('#rack').attr('data-series');
    rack_series = rack_series.replace(/'/g, '"'); //");
    rack_series = JSON.parse(rack_series);

    var cell_lines = $('#cell_lines').attr('data-cell_lines');
    cell_lines = cell_lines.replace(/'/g, '"'); //");
    cell_lines = JSON.parse(cell_lines);

    function showRackContent(e) {
        var tower = e.point.category;
        var rack = this.name;
        var key = tower + '_' + rack;
        data = rack_series[key];
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
        $('#discard_changes').addClass('d-none');
        $('#erase').addClass('d-none');
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
                    click: function(e){show_cell_line_details(e); $('#cell_line').attr('data-unchanged-val', e.point.ID);}
                },
                allowPointSelect: true,
                states: {
                    select: {
                        color: "#098AB9"
                    }
                }
            }],
        });
    }

    function show_cell_line_details(e) {
        var cell_line = e.point.ID;
        $('#cell_lines').find('table').removeClass('d-none');
        $('#cell_lines').find('p.h5').removeClass('d-none');
        $('#save_changes').removeClass('d-none');
        $('#discard_changes').removeClass('d-none');
        $('#cell_lines').find('p.h5').text('Rack' + e.point.Rack + ', ' + e.point.pos);
        $('#erase').removeClass('d-none');
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
            $('#responsible_name').text(data['Responsible person']);
            $('#comments').text(data['Comments']);
        }
        $('#location').text('Rack' + e.point.Rack + ", " + e.point.pos);
    }

    $('#remove_from_rack').on('click', function(e) {
        if ($('#cell_line').text() != "") {
            var position = $('#location').text();
            position = position.split(', ');
            var rack = position[0];
            position = position[1];
            var responsible = $('#responsible').val();
            if (responsible == "") {
                $('#error-1').removeClass('d-none');
                $('#error-1').text('Enter your name. Name is required');
            } else {

                var comments = $('#comments-1').val();
                $('#cell_line_ID').text('');
                $('#cell_line').text('');
                $('#media').text('');
                $('#plasmid').text('');
                $('#selection').text('');
                $('#type').text('');
                $('#biosafety').text('');
                $('#mycoplasma').text('');
                $('#source').text('');
                var today = get_today();
                $('#date').text(today);
                $('#responsible_name').text(responsible);
                $('#comments').text(comments);

                // mark with bold updated values
                $('#date').addClass('font-weight-bold');
                $('#responsible_name').addClass('font-weight-bold');
                if (comments != "") {
                    $('#comments').addClass('font-weight-bold');
                }
                $('#confirm_erase').modal('hide');
            }
        } else {
            $('#confirm_erase').modal('hide');
        }
    });

    function get_today() {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1;
        var yyyy = today.getFullYear();
        if(dd<10){dd='0'+dd;}
        if(mm<10){mm='0'+mm;}
        today = dd+'.'+mm+'.'+yyyy;
        return today;
    }

    $('#discard_changes').on('click', function(e) {
        var cell_line = $('#cell_line').attr('data-unchanged-val');
        var val = 1;
        if (cell_line == "" || cell_line == undefined) {
            val = 0;
        }
        var location = $('#location').text();
        var rack = location.split(', ')[0].replace('Rack', '');
        var pos = location.split(', ')[1];
        var ee = {point: {ID: cell_line, value: val, Rack: rack, pos: pos}}
        show_cell_line_details(ee);
    });

    $('#save_changes').on('click', function(){
        var location = $('#location').text();
        var rack = location.split(', ')[0].replace('Rack', '');
        var pos = location.split(', ')[1];
        var prev_cell_line = $('#cell_line').attr('data-unchanged-val');
        var cell_line = $('#cell_line_ID').text();
        var responsible = $('#responsible_name').text();
        var date = $('#date').text();
        var comments = $('#comments').text();

        var prev_data = cell_lines[prev_cell_line];
        var prev_resp = prev_data['Responsible person'];
        var prev_comments = prev_data['Comments'];
        var prev_date = prev_data['Date'];

        data = {
//            tower: tower,
            rack: rack,
            pos: pos,
            prev_cell_line: prev_cell_line,
            cell_line: cell_line,
            responsible: responsible,
            date: date,
            comments: comments,
            prev_resp: prev_resp,
            prev_comments: prev_comments,
            prev_date: prev_date
        }

        var url = window.location.href + "/update_rack";
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function() {
            alert( "success" );
          }).fail(function() {
            alert( "error" );
          })
    });
});
