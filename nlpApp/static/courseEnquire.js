$(document).ready(function () {
    var current_login_name = get_login_name()
    console.log(current_login_name)
    intitialize_datatable();
});

// const csrftoken = getCookie('csrftoken');
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

//convert a dictionary object to json, by replacing ' to "
function context_to_json(context) {
    const a = context.replace(/'/g, '"');
    return JSON.parse(a);
}

$('.yearpicker').yearpicker()

//
function get_login_name() {
    let current_login_name = $("#current_login_name").text()
    return current_login_name
}

$("#btnSearch").click(function (){
    Search();
})

//swapping the json key value pair
function swapJsonKeyValues(JsonInput) {
    let one, JsonOutput = {};
    for (one in JsonInput) {
        if (JsonInput.hasOwnProperty(one)) {
            JsonOutput[JsonInput[one]] = one;
        }
    }
    return JsonOutput;
}

function intitialize_datatable() {
    var searchTable = $('#datatable').DataTable({
        destroy: true,
        deferRender: true,
        paging: true,
        searching: false,
        pageLength: 30,
        lengthMenu: [[10, 30, 50, 100], [10, 30, 50, 100]],
        // dom: 'Qfrtip',
        // dom: "<'row'l Bf>"+"<'row' i p>" + "<'row'Rt>" + "<'row'i p>",
        colReorder: true,
        // stateSave: true,
        buttons: [{
            extend: 'colvis', text: 'Column Shown',
            collectionLayout: 'fixed three-column '
        }],
        order: [],
        columnDefs: [{

            orderable: false,
            // className: 'm-2',
            targets: 0,
        }],
    });
    // new $.fn.dataTable.SearchBuilder(searchTable, {});
    // searchTable.searchBuilder.container().prependTo(searchTable.table().container());

}


// Enable / disable the department received date to field by clicking the checkbox
$('#dept_received_date_range_check').on('click', function () {
    $('#dept_received_date_to').attr('disabled', !this.checked);
    $('#dept_received_date_to').val('');
});

$("#case_created_by_you").click(function () {
    var checkis = $(this).is(":checked");
    // console.log(checkis);
    if (checkis == true) {
        $("#case_created_by_you").val(get_login_name());
        // console.log($("#case_created_by_you").val())
    } else {
        $("#case_created_by_you").val("");
    }
});

function Search() {
    document.body.style.cursor = 'wait';
    $.ajax({
        url: '/nlpApp/ajax_search/',
        type: 'post',
        headers: {'X-CSRFToken': csrftoken},
        timeout: 50000,
        data: {
            'course_code': $("#course_code").val(),
            'course_name': $("#course_name").val(),
            'academic_year_from': $("#academic_year_from").val(),
            'academic_year_to': $("#academic_year_to").val(),
            'create_by': $("#case_created_by_you").val(),
            },
        error: function (xhr, textStatus, errorThrown) {
            document.body.style.cursor = 'default';
            if (textStatus === 'timeout') {
                alert('Request Timeout');
            }
        },
    }).done(function (ret) {
        document.body.style.cursor = 'default';
        var searchResult = JSON.parse(ret);
        var searchTable = $('#datatable').DataTable({
            autoWidth: false,
            destroy: true,
            deferRender: true,
            paging: true,
            searching: false,
            pageLength: 30,
            lengthMenu: [[10, 30, 50, 100], [10, 30, 50, 100]],
            // dom: 'Qlfrtip',
            // dom: "<'row'l Bf>"+"<'row' i p>" + "<'row'Rt>" + "<'row'i p>",
            colReorder: true,
            // stateSave: true,
            buttons: [{
                extend: 'colvis', text: 'Column Shown',
                collectionLayout: 'fixed three-column '
            }],
            order: [],
            columnDefs: [{
                orderable: false,
                // className: 'select-checkbox',
                targets: 0,
            }],
            // language: {
            //     searchBuilder: {
            //         title: {
            //             0: '<p class="font-weight-bold">Conditions-Based Filtering:</p>',
            //             _: '<p><span class="font-weight-bold">Conditions-Based Filtering</span> - currently applying %d conditions:</p>'
            //         }
            //     }
            // },
            // searchBuilder: {
            //     preDefined: {
            //         criteria: [
            //             {
            //                 // data: 'Record Creator',
            //                 // condition: 'starts',
            //                 // value: get_login_name()
            //             }
            //         ]
            //     }
            // },
            "data": searchResult,
            "columns": [
                {
                    "data": {CREATE_BY: "CREATE_BY", COURSE_INFO_ID: "COURSE_INFO_ID"},
                    "render": function (data, type, row, meta) {

                        console.log(data.CREATE_BY)
                        console.log(get_login_name())
                        if (data.CREATE_BY == get_login_name()) {
                        // if (data.CREATE_BY == get_login_name()) {

                            return data =
                                '<div><a class="case_action" id="actionUpdate_' + data.COURSE_INFO_ID + '" href="#" title="View/Update">' +
                                '<button class="btn-sm btn-outline-warning">View/Update</button></a></div>' +
                                '<div><a class="case_action" id="btnGenerateReport_' + data.COURSE_INFO_ID + '" href="#" title="Generate Report">' +
                                '<button class="btn-sm btn-outline-primary">Generate Report</button></a></div>'

                        } else {
                            return data =
                                '<div><a class="case_action" id="actionDuplicate_' + data.COURSE_INFO_ID + '" href="#" title="View/Duplicate">' +
                                '<button class="btn-sm btn-outline-secondary">View/Duplicate</button></a></div>'
                        }
                    },
                },

                {"data": "COURSE_CODE"},
                {"data": "COURSE_NAME",
                  "render": function (data) {
                        return data
                            = '<div style="white-space:pre-line; word-break:break-word; min-width:100px; width:auto; overflow-y:auto; max-height: 100px;" >' + data + '</div>'
                    }},
                {"data": {ACADEMIC_YEAR_FROM: "ACADEMIC_YEAR_FROM",ACADEMIC_YEAR_TO: "ACADEMIC_YEAR_TO"},
                "render":function (data) {
                        return data
                            = '<span>' + data.ACADEMIC_YEAR_FROM +'-'+ data.ACADEMIC_YEAR_TO + '</span>'
                    }},
                {"data": "ACADEMIC_SEMESTER"},
                {"data": "TEACHER_LECTURER"},
                {
                    "data": "COURSE_DESP",
                    "render": function (data) {
                        return data
                            = '<div style="white-space:pre-line; word-break:break-word; min-width:200px; width:auto; overflow-y:auto; max-height: 100px;" >' + data + '</div>'
                    }
                },
                {"data": "CREATE_BY"},
                // {"data": "last_update_date_st"},
            ]
        });
        // new $.fn.dataTable.SearchBuilder(searchTable, {});
        // searchTable.searchBuilder.container().prependTo(searchTable.table().container());
    })
}

// Change the action button URLs to POST method for security considerations
$("#datatable tbody").on("click", ".case_action", function (event) {
    event.preventDefault();
    let url = '';
    // const url = $(this).prop('href').split('?');
    const elementId = $(this).prop('id').split('_');

    const btnType = elementId[0];
    const course_info_id = elementId[1];
    console.log(course_info_id)
    if (btnType == 'btnGenerateReport'){
        url = '/nlpApp/courseReport/'
    }else{
        url = '/nlpApp/courseDetail/';
    }

    // const params = (url.length > 1) ? url[1].split('&') : []
    const form = document.createElement('form');
    form.setAttribute('method', 'post');
    form.setAttribute('action', url);
    form.setAttribute("target", '_blank');

    const inp = document.createElement('input');
    inp.setAttribute('type', 'text');
    inp.setAttribute('name', 'course_info_id');
    inp.setAttribute('value', course_info_id);
    form.appendChild(inp);

    const inp1 = document.createElement('input');
    inp1.setAttribute('type', 'text');
    inp1.setAttribute('name', 'btnType');
    inp1.setAttribute('value', btnType);
    form.appendChild(inp1);

    const inp2 = document.createElement('input');
    inp2.setAttribute('type', 'hidden');
    inp2.setAttribute('name', 'csrfmiddlewaretoken');
    inp2.setAttribute('value', csrftoken);
    form.appendChild(inp2);

    document.querySelector("body").appendChild(form);
    form.submit();
    form.remove();
    event.stopPropagation();
});

window.addEventListener("message", function (event) {
    if (event.origin !== window.location.origin) {
        console.log(event.origin);
        console.log(window.location.origin);
        return;
    }
    const message = event.data.message;
    if (message !== undefined) {
        if (message === "reload") {
            document.querySelector("#btnSearch").click();
        } else {
            alert(message);
        }
    }
});

$("#btnSearchbtnClear").click(function () {
    $("input").each(function () {
        $(this).val("")
    })
    $("#case_created_by_you").prop('checked',false)
})