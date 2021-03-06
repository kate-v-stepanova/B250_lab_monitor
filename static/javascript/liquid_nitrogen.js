$(document).ready(function() {

    // edit fields of cell line
    $.fn.editable.defaults.mode = 'inline';
    $('#comments').editable({
        type:  'textarea',
        emptytext: '',
    });

    $('#date').editable({
        emptytext: '',
    });

    var responsibles = $('#responsibles').attr('data-responsibles');
    responsibles = responsibles.replace(/'/g, '"'); //");
    responsibles = JSON.parse(responsibles);
    $('#responsibles').remove();

    $('#responsible_name').editable({
        emptytext: '',
        type: 'select',
        value: $('#responsible_name').text(),
        source: responsibles,
    });

    var cell_lines_dropdown = $('#cell_lines').attr('data-dropdown');
    cell_lines_dropdown = cell_lines_dropdown.replace(/'/g, '"'); //");
    cell_lines_dropdown = JSON.parse(cell_lines_dropdown);

    function validate_cell_line(value) {
        // that's not exactly how this function is supposed to be used,
        // but I couldn't find any other way to update the other fields.

        // show modal -> to enter responsible name and comments
        // after entering, click OK and call $('#modal-ok').on('click') function
        if (value == 'add_new') {
            // increment ID
            var last_val = cell_lines_dropdown[cell_lines_dropdown.length-1];
            last_val = last_val['value'];
            var new_val = last_val.replace('FLP', '');
            new_val = parseInt(new_val) + 1;
            new_val = last_val.replace(new_val -1, new_val);
            $('#new_cell_line_id').val(new_val);
            // show modal
            $('#new_cell_line').modal();
            /*
                // here will be processed modal inputs
            */
        } else {
            var cell_line = cell_lines[value];
            if (cell_line != undefined) {
                // then update fields
                $('#cell_line').text(cell_line['Cell line']);
                $('#cell_line_ID').text(value);
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
            // responsible
            var resp = $('#responsible-2').val();
            var comments = $('#comments-2').val();
            var today = get_today();
            $('#date').text(today);
            $('#responsible_name').text(resp);
            $('#comments').text(comments);
        }
    }


    $('#cell_line_ID').editable({
        type: 'select',
        value: $('#cell_line_ID').text(),
        source: cell_lines_dropdown,
        validate: validate_cell_line,
    });

    $('#create_new').on('click', function(e) {
        var new_ID = $('#new_cell_line_id').val();
//        $('#new_cell_line').find('form').valid();
        var new_cell_line_name = $('#new_cell_line_name').val();
        var new_media = $('#new_media').val();
        var new_biosafety = $('#new_biosafety').val();
        var new_type = $('#new_type').val();
        var new_genotype = $('#new_genotype').val();
        var new_clone = $('#new_clone').val();
        var show_alert = false;
        if (new_cell_line_name == '') {
            $('#new_cell_line_name').addClass('is-invalid');
            show_alert = true;
        }
        if (new_media == '') {
            $('#new_media').addClass('is-invalid');
            show_alert = true;
        }
        if (new_biosafety == '') {
            $('#new_biosafety').addClass('is-invalid');
            show_alert = true;
        }
        if (new_type == '') {
            $('#new_type').addClass('is-invalid');
            show_alert = true;
        }
        if (show_alert) {
            alert('Fill in all required fields');
        } else {
            var data = {
                'ID': new_ID,
                'Cell line': new_cell_line_name,
                'Media (Freezing Medium)': new_media,
                'Transferred plasmid': $('#new_plasmid').val(),
                'Selection': $('#new_selection').val(),
                'Typ': new_type,
                'Biosafety Level': new_biosafety,
                'Mycoplasma checked': $('#new_mycoplasma').val(),
                'Source': $('#new_source').val(),
                'Clone number': new_clone,
                'Genotype': new_genotype,

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
            }).done(function(response) {
                if (response['status'] == 'error') {
                    alert(response['error']);
                } else {
                    alert('Successfully created/updated');
                    $('#new_cell_line').modal('hide');
                    // add cell line to a list
                    cell_lines[new_ID] = data;
                    cell_lines_dropdown.push({'value': new_ID, 'text': new_ID});

                    // update editable select
                    $('#cell_line_ID').editable('option', 'source', cell_lines_dropdown);

                    // update table
                    if ($('#' + new_ID).length != 0) {
                        $('#' + new_ID).find('td.Cell_line').text(data['Cell line']);
                    } else {
                        $('#available_cell_lines').append("<tr id='" + new_ID + "'><td class='ID'>" + new_ID +
                        "</td><td class='Cell_line'>" + data['Cell line'] + "</td>" +
                        "<td><button class='btn btn-sm btn-outline-primary edit_cell_line'>✎ Edit</button></td>" +
                        "<td><button class='btn btn-sm btn-outline-danger del_cell_line'>× Delete</button></td>");
                    }

                    // clear modal fields
                    $('#new_cell_line').find('div.form-group').find('input').val('');

                    // update cell_lines
                    cell_lines[new_ID] = data;
                }
            }).fail(function(response) {
                alert(response['responseJSON']['error']);
            });
        }
    }); // }

    $('#erase').on('click', function(){
        var resp = $('#towers').attr('data-cur_user');
        if (resp == undefined) {
            alert('Please select responsible');
        } else {
            $('#responsible_name').text(resp);
        }
        var today = get_today();
        $('#date').text(today);

        // mark with bold (updated values)
        $('#responsible_name').addClass('font-weight-bold');
        $('#date').addClass('font-weight-bold');
        if (comments != "") {
            $('#comments').addClass('font-weight-bold');
        }
    }); // )

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
            $('#comments-2').val('');
        }
    });

    var chart_towers = Highcharts.chart('towers', {
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

    var rack_chart;
    function load_chart_racks(rack_name, rack_data) {
        rack_chart = Highcharts.chart('rack', {
            chart: {
                type: 'heatmap',
                height: 450,
                width: 430,
            },
            title: {
                text: rack_name,
            },
            xAxis: {
                categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            },
            yAxis: {
                categories: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
                title: {
                    text: ''
                },
                reversed: true
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
                data: rack_data,
                events: {
                    click: function(e){
                        if (e.point.pos == "J10" || (e.point.options.x == 9 && e.point.options.y == 9)) {
                            e.preventDefault();
                            alert('J10 is disabled');
                        } else {
                            // for MULTI select
                            // get selected positions
                            selected = rack_chart.getSelectedPoints();
                            var all_same = true;
                            var deselect_current = false;
                            if (selected.length > 0) {
                                var all_val = selected[0].value;
                                for (i=0; i<selected.length; i++) {
                                    if (selected[i].value != all_val) {
                                        all_same = false;
                                    }
                                    if (e.point.pos == selected[i].pos) {
                                        deselect_current = true;
                                    }
                                }
                                if (e.point.value != all_val){
                                    all_same = false;
                                }
                            }
                            if (!all_same) {
                                for (i=0; i<selected.length; i++) {
                                    selected[i].select(false);
                                }
                            }
                            // anyway show content
                            show_cell_line_details(e);
                            $('#cell_line').attr('data-unchanged-val', e.point.ID);

                            // update header (show all selected positions)
                            selected = rack_chart.getSelectedPoints();
                            if (!deselect_current) {
                                selected.push(e.point);
                            }
                            if (selected.length > 1) {
                                $('#location').empty();
                                var all_pos = [];
                                for (i=0; i<selected.length; i++) {
                                    // add all locations to the title
                                    var pos = selected[i].pos;
                                    if (pos == undefined) {
                                        var x = selected[i].x + 1;
                                        var y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'][selected[i].y];
                                        pos = '<span class="badge badge-primary">' + y + x + '</span>';
                                    } else {
                                        pos = '<span class="badge badge-primary">' + pos + '</span>';
                                    }
                                    if (selected[i].pos != e.point.pos || !deselect_current) {
                                        all_pos.push(pos);
                                    }
                                }
                                var rack = $('#rack').find('text.highcharts-title tspan').text();
                                var title = "<span class='rack'>" + rack + '</span> ' + all_pos.join(' ')
                                $('#cell_lines').find('p.h5').html(title);
                                $('#location').append(title);
                            } else if (selected.length == 1) {
                                 var rack = $('#rack').find('text.highcharts-title tspan').text();
                                 var x = e.point.x + 1;
                                 var y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'][e.point.y];
                                 $('#location').text(rack + ", " + y + x);
                            }
                        }
                    }
                },
                allowPointSelect: true,
                states: {
                    select: {
                        color: "#098AB9"
                    }
                }
            }],
        });
    };
    function showRackContent(e) {
        var rack_name = this.name;
        var tower = e.point.category;
        $('#towers').attr('selected-tower', tower);
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
            rack_series[key] = data;
        }
        $('#cell_lines').find('table').addClass('d-none');
        $('#cell_lines').find('p').addClass('d-none');
        $('#save_changes').addClass('d-none');
        $('#discard_changes').addClass('d-none');
        $('#rack_buttons').addClass('d-none');
        load_chart_racks(rack_name, data);
        if ($('#export_rack').hasClass('d-none')) {
            $('#export_rack').removeClass('d-none');
        }
    }

    function show_cell_line_details(e) {
        $('#cell_lines').find('table').removeClass('d-none');
        $('#cell_lines').find('p.h5').removeClass('d-none');
        $('#save_changes').removeClass('d-none');
        $('#discard_changes').removeClass('d-none');
        var rack = $('#rack').find('text.highcharts-title tspan').text();
        var tower = $('#towers').attr('selected-tower');
        var x = e.point.x + 1;
        var y = e.point.y;
        y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'][y];
        // update header
        $('#cell_lines').find('p.h5').text(rack + ', ' + y + x);

        $('#location').text(rack + ", " + y + x);
        var cell_line = e.point.ID;
        // if location is empty
        if (cell_line == undefined || cell_line == '') {
            if (!$('#rack_buttons').hasClass('d-none')) {
                $('#rack_buttons').addClass('d-none');
            }
            $('#cell_line').attr('data-unchanged-val', '');
            $('#responsible_name').text(e.point["Responsible person"]);
            $('#date').text(e.point['Date']);
            $('#comments').text(e.point['Comments']);
        } else {
            $('#rack_buttons').removeClass('d-none');
        }

        if (e.point.value == 0 || e.point.value == undefined || cell_line == '') {
            $('#cell_lines').find("td[id]").text('');
            $('#responsible_name').text(e.point["Responsible person"]);
            $('#date').text(e.point['Date']);
            $('#comments').text(e.point['Comments']);
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
            // get date, comment and responsible from the rack data and update fields
            var rack_data = rack_series[tower + '_' + rack];
            if (rack_data != undefined) {
                $('#date').text(rack_data['Date']);
                $('#responsible_name').text(rack_data['Responsible person']);
                $('#comments').text(rack_data['Comments']);
            } else {
                $('#date').text('');
                $('#responsible_name').text('');
                $('#comments').text('');
            }
        }
//        $('#pos-details').find('tr').removeClass('table-warning');

        if (e.point.value == 2 || e.point.value == '2') { // 2 means to confirm
            $('#pos-details').find('tr').addClass('table-warning');
//            $('tr.to_approve').removeClass('d-none');
//            $('#prev_cell_line').text(data['prev_cell_line']);
//            $('#prev_responsible').text(data['prev_responsible']);
//            $('#prev_comments').text(data['prev_comments']);
//            $('#prev_date').text(data['prev_date']);
        } else {
            $('tr.to_approve').addClass('d-none');
        }

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
                $('#confirm_request').modal('hide');
            }
        } else {
            $('#confirm_request').modal('hide');
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

    // discard assign of a cell line to a position
    function discard_changes() {

        // load previous values
        var cell_line = $('#cell_line').attr('data-unchanged-val');
        var val = 1;
        if (cell_line == "" || cell_line == undefined) {
            val = 0;
        }
        // if multiple positions are selected
        var location = $('#location').html();
        var rack = $('#location').find('span.rack').text();
        var pos = $('#location').find('span.badge').text();
        // if single position is selected, then no span elements -> Rack7, C3
        if (rack == undefined || pos == undefined) {
            rack = location.split(', ')[0].replace('Rack', '');
            pos = location.split(', ')[1];
            var x = pos.substr(1) - 1;
            var y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'].indexOf(pos[0]);
            var ee = {point: {ID: cell_line, value: val, Rack: rack, pos: pos, x: x, y:y}};
            show_cell_line_details(ee);
        } else {
            $('#pos-details').find('tr td:nth-child(2)').text(''); // clear second column
            $('#location').append(location);
        }
    }

    $('#modal-cancel').on('click', function(e) {
        discard_changes();
    });

    $('#discard_changes').on('click', function(e) {
        discard_changes();
    });

    $('#save_changes').on('click', function(){
        var tower = $('#towers').attr('selected-tower');

        // if multiple positions are selected
        var location = $('#location').html();
        var rack = $('#location').find('span.rack').text();
        var pos = $('#location').find('span.badge');
        if (pos.length != 0) {
            pos = $('#location').find('span.badge').map(function() {
                return $(this).text();
            }).get();
        } else {
            rack = $('#location').text().split(', ')[0];
            pos = [$('#location').text().split(', ')[1]];
        }
        rack = rack.replace('Rack', '');
        var prev_cell_line = $('#cell_line').attr('data-unchanged-val');
        var cell_line = $('#cell_line_ID').text();
        var responsible = $('#responsible_name').text();
        var date = $('#date').text();
        var comments = $('#comments').text();
        var prev_data = cell_lines[prev_cell_line];
        if (prev_data == undefined) {
            prev_data = {};
        }
        var prev_resp = prev_data['Responsible person'];
        var prev_comments = prev_data['Comments'];
        var prev_date = prev_data['Date'];
        data = {
            tower: tower,
            Rack: rack,
            pos: pos,
            prev_cell_line: prev_cell_line,
            cell_line: cell_line,
            'Responsible person': responsible,
            Date: date,
            Comments: comments,
            prev_resp: prev_resp,
            prev_comments: prev_comments,
            prev_date: prev_date,
        }

        // add or remove
        var url = window.location.href + "/update_rack";
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function(response) {
            alert( "success" );
            // update rack_series
            var rack_name = 'Rack'+rack;
            for (i=0; i<pos.length;i++) {
                var y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'].indexOf(pos[i][0]);
                var x = parseInt(pos[i].substring(1)) - 1; // pos[i][1:]
                var cur_data = {
                    'x': x,
                    'y': y,
                    'pos': pos[i],
                    'color': '#ffcc00',
                    'value': 2,
                    'status': 'to_confirm',
                    'ID': data['cell_line'],
                    'Comments': comments,
                    'Date': date,
                    'Responsible person': responsible,
                    'tower': tower,
                    'Rack': rack_name,
                };
                var k = x + y * 10;
                rack_series[tower + '_Rack' + rack][k] = cur_data;
            }
            var rack_data = rack_series[tower + '_Rack' + rack];
            load_chart_racks(rack_name, rack_data);
            // update my requests
            for (i=0; i<pos.length; i++) {
                var new_tr = "<tr><td class='tower'>" + data['tower'] + "</td><td class='Rack'>" + data['Rack'] + "</td>" +
                "<td class='pos'>" + pos[i] + "</td><td class='cell_line'>" + data['cell_line'] + "</td>" +
                "<td class='prev_cell_line'>" + data['prev_cell_line'] + "</td><td class='Comments'>" + data['Comments'] + "</td>" +
                "<td class='Date'>" + data['Date'] + "</td><td class='Responsible person'>" + data['Responsible person'] + "</td>" +
                "<td class='status'><span class='badge badge-warning'>pending</span></td>" +
                "<td><button class='btn btn-sm btn-outline-warning ml-2 cancel_req'>× Cancel request</button></td>";
                $('#user_requests').find('tr:last').after(new_tr);
            }
            if ($('#user_requests').hasClass('d-none')) {
                $('#user_requests').removeClass('d-none');
            }
            // update pending requests
            for (i=0; i<pos.length; i++) {
                var new_tr2 = '<tr><td class="tower">' + data['tower'] + '</td><td class="Rack">' + data['Rack'] + '</td>' +
                    '<td class="pos">' + pos[i] + '</td><td class="cell_line">' + data['cell_line'] + '</td>' +
                    '<td class="prev_cell_line">' + data['prev_cell_line'] + '</td><td class="Comments">' + data['Comments'] +
                    '</td><td class="Date">' + data['Date'] + '</td><td class="Responsible person">' + data['Responsible person'] +
                    '</td>';
                if ($('#requests_table').attr('data-admin') == 'True') {
                    new_tr2 += '<td><button class="btn btn-sm btn-outline-success approve_btn">✓ Approve</button></td>' +
                    '<td><button class="btn btn-sm btn-outline-danger decline_btn">× Decline</button></td></tr>';
                }

                $('#requests_table').find('tr:last').after(new_tr2);
            }
            if ($('#requests_table').hasClass('d-none')) {
                $('#requests_table').removeClass('d-none');
            }
        }).fail(function(response) {
            console.log(response);
            alert(response);

        })
    });

    function search_cell_line() {
        var to_search = $('#search').val();
        if (to_search != '') {
            var url = window.location.href + "/search";
            $.ajax({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: url,
                dataType: 'json',
                //json object to sent to the authentication url
                data: to_search,
                contentType: 'text/html',
            }).done(function(response) {
                $('#search_results').empty();
                $('#search_results').append(response['html_result']);
                $('#clear_search').removeClass('d-none');
            }).fail(function(response) {
                console.log(response);
                alert('Failed');

            })
        }
    }

    $('#search_btn').on('click', function() {
        search_cell_line();
    });


    $('#clear_search').on('click', function() {
        $('#search_results').empty();
        $('#search').val('');
        $('#clear_search').addClass('d-none');
    });

    $(document).on('click', '.approve_btn, .decline_btn, .cancel_req', function() {
        var btn = this;
        var url = window.location.href + "/approve_decline";
        var tower = $(this).closest('tr').find('td.tower').text().trim();
        var rack = $(this).closest('tr').find('td.Rack').text().trim();
        var pos = $(this).closest('tr').find('td.pos').text().trim();
        var cell_line_id = $(this).closest('tr').find('td.cell_line').text().trim();

        var action = "";
        if ($(this).hasClass('approve_btn')) {
            action = 'approve';
        } else if ($(this).hasClass('decline_btn')) {
            action = 'decline';
        } else {
            action = 'cancel';
        }

        var to_approve = {
            'tower': tower,
            'Rack': rack,
            'pos': pos,
            'action': action,
            'cell_line_id': cell_line_id,
        };
        $.ajax({
            type: "POST",
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: JSON.stringify(to_approve),
            contentType: 'application/json',
        }).done(function(response) {
            console.log(response)
            $(btn).closest("tr").remove();
        }).fail(function(response) {
            console.log(response);
            alert('Failed');
        });
        $('tr#' + to_approve['tower'] + '_' + to_approve['Rack'] + '_' + to_approve['pos']).removeClass('table-warning').find('td.status').text('');
    });

    $('#export_data').on('click', function() {
        var url = window.location.href + "/export_data";
        $.ajax({
            type: "POST",
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: {},
            contentType: 'application/json',
        }).done(function(response) {
            var csv_content = response['csv_content'];
            var blob = new Blob([csv_content], {type: "text/plain;charset=utf-8"});
            var now = new Date().toLocaleString().replace(/\//g, '-').replace(/\ /g, '_').replace(',', '');
            var file_name = now + '_liquid_nitrogen.csv';
            saveAs(blob, file_name)
        }).fail(function(response) {
            console.log(response);
            alert('Failed');

        });
    });

    // disable form submission when pressing Enter
    $(window).keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            if (event.target.id == 'search') {
                search_cell_line();
            }
            return false;
        }
    });

    // request cell line from search results
    $(document).on('click', '#request_search', function(e) {
        var cell_line_id = $(this).closest('tr').find('td.ID').text();
        var cell_line_name = $(this).closest('tr').find('td.Cell_line').text();
        var tower = $(this).closest('tr').find('td.tower').text();
        var rack = $(this).closest('tr').find('td.Rack').text();
        var pos = $(this).closest('tr').find('td.pos').text();
        var today = get_today();
        $('#confirm_request_from_search').modal('show');
        $('#cell_line_id_search').text(cell_line_id);
        $('#cell_line_name_search').text(cell_line_name);
        $('#tower_search').text(tower);
        $('#rack_search').text(rack);
        $('#pos_search').text(pos);
        $('#date_search').text(today);
    });

    $('#request_from_search').on('click', function(e) {
        var url = window.location.href + "/update_rack";

        var data = {
            cell_line: '',
            prev_cell_line: $('#cell_line_id_search').text(),
            tower: $('#tower_search').text(),
            Rack: $('#rack_search').text(),
            pos: $('#pos_search').text(),
            Date: $('#date_search').text(),
            Comments: $('#comments_search').val(),
            'Responsible person': $('#responsible_search').val(),
        };
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: url,
            dataType: 'json',
            //json object to sent to the authentication url
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function(response) {
            alert( "success" );
            // update rack_series
            var i = parseInt(data['pos'][0]) -1 + parseInt(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'].indexOf(data['pos'][1])) * 10;
            data['color'] = '#ffcc00';
            data['value'] = 2;
            data['x'] = parseInt(data['pos'][0]) - 1;
            data['y'] = parseInt(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'].indexOf(data['pos'][1]));
            data['status'] = 'pending';
            data['ID'] = data['cell_line'];
            var rack_name = 'Rack'+data['Rack'];
            rack_series[data['tower'] + '_Rack' + data['Rack']][i] = data;
            var rack_data = rack_series[data['tower'] + '_Rack' + data['Rack']];
            $('tr#'+data['tower'] + '_' + data['Rack'] + '_' + data['pos']).addClass('table-warning');
            $('tr#'+data['tower'] + '_' + data['Rack'] + '_' + data['pos']).find('td.status').text('pending');
            $('tr#'+data['tower'] + '_' + data['Rack'] + '_' + data['pos']).find('td.Responsible_person').text(data['Responsible person']);
            $('tr#'+data['tower'] + '_' + data['Rack'] + '_' + data['pos']).find('td.Date').text(data['Date']);
            $('tr#'+data['tower'] + '_' + data['Rack'] + '_' + data['pos']).find('button.request_search').remove();
            // add row in requests table
            var new_tr = "<tr><td class='tower'>" + data['tower'] + "</td><td class='Rack'>" + data['Rack'] + "</td>" +
            "<td class='pos'>" + data['pos'] + "</td><td class='cell_line'>" + data['ID'] + "</td>" +
            "<td class='prev_cell_line'>" + data['prev_cell_line'] + "</td><td class='Comments'>" + data['Comments'] + "</td>" +
            "<td class='Date'>" + data['Date'] + "</td><td class='Responsible person'>" + data['Responsible person'] + "</td>" +
            "<td class='status'><span class='badge badge-warning'>pending</span></td>" +
            "<td><button class='btn btn-sm btn-outline-warning ml-2 cancel_req'>× Cancel request</button></td>";
            $('#user_requests').find('tr:last').after(new_tr);
            // make it visible
            if ($('#user_requests').hasClass('d-none')){
                $('#user_requests').removeClass('d-none');
            }

        }).fail(function(response) {
            console.log(response);
            alert(response);
        });
    });

    $('#add_new_cell_line').on('click', function() {
        // increment ID
        var last_val = cell_lines_dropdown[cell_lines_dropdown.length-1];
        last_val = last_val['value'];
        var new_val = last_val.replace('FLP', '');
        new_val = parseInt(new_val) + 1;
        new_val = last_val.replace(new_val -1, new_val);
        $('#new_cell_line_id').val(new_val);
        // show modal
        $('#new_cell_line').modal();
        // clear all inputs
        $('#new_cell_line_name').val('');
        $('#new_media').val('');
        $('#new_plasmid').val('');
        $('#new_selection').val('');
        $('#new_type').val('');
        $('#new_biosafety').val('');
        $('#new_mycoplasma').val('');
        $('#new_source').val('');
        // clear errors
        $('#new_cell_line').find('form').find('input').removeClass('is-invalid');
    });

    $(document).on('click', '.edit_cell_line', function() {
        // get ID
        var cell_line_id = $(this).closest('tr').find('td.ID').text();
        var cell_line_data = cell_lines[cell_line_id];
        // fill in the inputs
        $('#new_cell_line_id').val(cell_line_id);
        $('#new_cell_line_name').val(cell_line_data['Cell line']);
        $('#new_media').val(cell_line_data['Media (Freezing Medium)']);
        $('#new_plasmid').val(cell_line_data['transfected plasmid']);
        $('#new_selection').val(cell_line_data['selection']);
        $('#new_type').val(cell_line_data['Typ']);
        $('#new_biosafety').val(cell_line_data['Biosafety level S1/S2']);
        $('#new_mycoplasma').val(cell_line_data['Mycoplasma checked']);
        $('#new_source').val(cell_line_data['Source']);
        // show modal
        $('#new_cell_line').modal();
        // clear errors
        $('#new_cell_line').find('form').find('input').removeClass('is-invalid');
    });

    // click "Delete" btn in the table
    $(document).on('click', '.del_cell_line', function() {
        var cell_line_id = $(this).closest('tr').find('td.ID').text();
        data = {'cell_line_id': cell_line_id};
        var url = window.location.href + "/get_cell_line_info";
        $.ajax({
            type: "POST",
            url: url,
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function(response) {
            console.log(response);
            var results = response['results'];
            if (results.length != 0) {
                for (i = 0; i < results.length; i++) {
                    var row = results[i];
                    var html = "<tr><td>" + row['tower'] + "</td><td>" + row['Rack'] + "</td>" + "<td>" + row['pos'] + "</td>";
                    if (row['status'] == 'pending') {
                        html += "<td><span class='badge badge-warning'>pending</span></td>"
                    } else if (row['status'] == 'approved') {
                        html += "<td><span class='badge badge-info'>approved</span></td>"
                    } else if (row['status'] == 'declined') {
                        html += "<td><span class='badge badge-danger'>declined</span></td>"
                    }
                    $('#cell_line_positions').append(html);
                }
                $('#cell_line_positions').removeClass('d-none');
            }
            $('#confirm_delete').modal();
            $('#delete_cell_line').removeClass('d-none');
            $('#cancel_delete').text('Cancel');
            $('#error-2').addClass('d-none');
            $('#cell_line_to_delete').text(cell_line_id);
        }).fail(function(response) {
            console.log(response);
        });
    });

    // modal confirm delete
    $('#delete_cell_line').on('click', function() {
        var cell_line_id = $('#cell_line_to_delete').text();
        var url = window.location.href + "/delete_cell_line";
        var data = {'cell_line_id': cell_line_id};
        $.ajax({
            type: "POST",
            url: url,
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).done(function(response) {
            console.log(response);
            var info = response['info'];
            $('#error-2').text(info);
            $('#error-2').removeClass('d-none');
            $('#error-2').removeClass('alert-danger').removeClass('alert-success');
            $('#error-2').addClass('alert-success');
            $('#delete_cell_line').addClass('d-none');
            $('#cancel_delete').text('Close');
            // remove from the table
            $('#' + cell_line_id).remove();
        }).fail(function(response) {
            console.log(response);
        });
    });

    // export Rack data
    $('#export_rack').on('click', function() {
        var tower = $('#towers').attr('selected-tower');
        var rack = $('#rack').find('.highcharts-title').text();
        var rack_data = rack_series[tower + '_' + rack];
        var content = ";"
        // header
        for (i=1; i<=10; i++){
            content += i+';';
        }
        content += "\n";
        for (i=0; i<10; i++) {
            for (j=-1; j<10; j++) {
                // labels A, B, C, etc
                if (j==-1) {
                    content += ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'][i] + ';'
                // cell lines
                } else {
                    var cell_line_id = rack_data[i * 10 + j]['ID'];
                    if (cell_line_id == undefined) {
                        cell_line_id = "";
                    } else if (String(rack_data[i*10 + j]['value']) != '1') {

                        if (rack_data[i*10 + j]['prev_cell_line'] != undefined) {
                            cell_line_id += rack_data[i*10 + j]['prev_cell_line'] + "(not approved)"
                        }
                    }
                    content += cell_line_id + ';';
                }
            }
            content += "\n";
        }

//        var csv_content = response['csv_content'];
        var blob = new Blob([content], {type: "text/plain;charset=utf-8"});
        var file_name = tower + "_" + rack + '.csv';
        saveAs(blob, file_name)
    });


    $(document).on('click', '#edit_info', function() {
        // get ID
        var cell_line_id = $('#pos-details').find('td#cell_line_ID').text();
        var cell_line_data = cell_lines[cell_line_id];
        // fill in the inputs
        $('#new_cell_line_id').val(cell_line_id);
        $('#new_cell_line_name').val(cell_line_data['Cell line']);
        $('#new_media').val(cell_line_data['Media (Freezing Medium)']);
        $('#new_plasmid').val(cell_line_data['transfected plasmid']);
        $('#new_selection').val(cell_line_data['selection']);
        $('#new_type').val(cell_line_data['Typ']);
        $('#new_biosafety').val(cell_line_data['Biosafety level S1/S2']);
        $('#new_mycoplasma').val(cell_line_data['Mycoplasma checked']);
        $('#new_source').val(cell_line_data['Source']);

        // show modal
        $('#new_cell_line').modal();

        // clear errors
        $('#new_cell_line').find('form').find('input').removeClass('is-invalid');
    });

    $("body").tooltip({
        selector: '[data-title]'
    });

    // enable edit of cell line ID
    $('#enable_id').on('click', function() {
        alert('If you enter ID which already exists, this will OVERWRITE the existing cell line!')
        $('#ok_id').removeClass('d-none');
        $('#enable_id').prop('disabled', true);
        $('#new_cell_line_id').prop('disabled', false);
    });

    // disable edit of cell line ID
    $('#ok_id').on('click', function() {
        $('#ok_id').addClass('d-none');
        $('#enable_id').prop('disabled', false);
        $('#new_cell_line_id').prop('disabled', true);
    });


    // edit cell line from search table
    $(document).on('click', '#edit_search', function() {
        // get ID
        var cell_line_id = $(this).closest('tr').find('td.ID').text();
        var cell_line_data = cell_lines[cell_line_id];
        // fill in the inputs
        $('#new_cell_line_id').val(cell_line_id);
        $('#new_cell_line_name').val(cell_line_data['Cell line']);
        $('#new_media').val(cell_line_data['Media (Freezing Medium)']);
        $('#new_plasmid').val(cell_line_data['transfected plasmid']);
        $('#new_selection').val(cell_line_data['selection']);
        $('#new_type').val(cell_line_data['Typ']);
        $('#new_biosafety').val(cell_line_data['Biosafety level S1/S2']);
        $('#new_mycoplasma').val(cell_line_data['Mycoplasma checked']);
        $('#new_source').val(cell_line_data['Source']);

        // show modal
        $('#new_cell_line').modal();

        // clear errors
        $('#new_cell_line').find('form').find('input').removeClass('is-invalid');
    });
});
