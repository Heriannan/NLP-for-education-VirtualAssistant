$(document).ready(function () {
    $("#courseReg_haveTut").click()
    $("#courseReg_haveAsm").click()
})
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

$("#courseReg_haveTut").click(function () {
    if ($(this).val() == 'Y') {
        $(".courseReg_tutDesp").removeClass("d-none")
    } else {
        $(".courseReg_tutDesp").addClass("d-none")
    }
})
$("#courseReg_haveAsm").click(function () {
    if ($(this).val() == 'Y') {
        $("#courseReg_AsmBlock").removeClass("d-none")
    } else {
        $("#courseReg_AsmBlock").addClass("d-none")
    }
})

$("#courseReg_courseStartDay").change(function () {
    if ($(this).val() != "") {

        start_month = $(this).val().split('-')[1]
        if (inRange(start_month, 9, 12)) {
            $("#courseReg_academicSemester").val("A")
            start_year = $(this).val().split('-')[0]
            end_year = parseInt(start_year) + 1
        } else if (inRange(start_month, 1, 5)) {
            $("#courseReg_academicSemester").val("B")
            end_year = $(this).val().split('-')[0]
            start_year = parseInt(end_year) - 1
        } else {
            $("#courseReg_academicSemester").val("Summer")
            end_year = $(this).val().split('-')[0]
            start_year = parseInt(end_year) - 1
        }
        year_range = start_year + "-" + end_year


        $("#courseReg_academicYear").val(year_range)


    }
})

function inRange(n, nStart, nEnd) {
    if (n >= nStart && n <= nEnd) return true;
    else return false;
}

function validate() {
    if ($("#courseReg_courseName").val() == '' ||
        $("#courseReg_courseCode").val() == '' ||
        $("#courseReg_courseStartDay").val() == '' ||
        $("#courseReg_lecturer").val() == '' ||
        $("#courseReg_courseDesp").val() == '' ||
        $("#courseReg_creditUnit").val() == '' ||
        $("#courseReg_geArea").val() == '' ||
        $("#courseReg_mediumInstruction").val() == '' ||
        $("#courseReg_mediumAsm").val() == '' ||
        $("#courseReg_haveTut").val() == '' ||
        $("#courseReg_haveAsm").val() == ''
    ) {
        alert('Please complete all * field first.')
        return false
    } else {
        return true
    }
}

function loopEachElement(data_type) {
    // console.log(data_type)
    let list = []
    // $('input[data-type=data_type]').each(function(){
    $(data_type).each(function () {

        let value = $(this).val();
        let id = $(this).attr('id');
        // console.log('id: ' + id + ' value:' + value);
        list.push(value)
    });
    for (i = 0; i < list.length; i++) {
        if (list[i] != "") {
            return list;
        }
    }
    return false;
}

function getData(action, url) {
    let course_info = {}
    let course_syllabus = {}
    let course_assessments = {}
    // course_info['ID']=$("#")
    course_info['COURSE_NAME'] = $("#courseReg_courseName").val()
    course_info['COURSE_CODE'] = $("#courseReg_courseCode").val()
    course_info['COURSE_START_DAY'] = $("#courseReg_courseStartDay").val()

    course_info['ACADEMIC_YEAR_FROM'] = $("#courseReg_academicYear").val().split('-')[0]
    course_info['ACADEMIC_YEAR_TO'] = $("#courseReg_academicYear").val().split('-')[1]
    course_info['ACADEMIC_SEMESTER'] = $("#courseReg_academicSemester").val()
    course_info['TEACHER_LECTURER'] = $("#courseReg_lecturer").val()
    course_info['TEACHER_TA'] = $("#courseReg_ta").val()
    course_info['PREREQUISITES'] = $("#courseReg_prerequisites").val()
    course_info['HAVE_ASSESSMENTS'] = $("#courseReg_haveAsm").val()

    course_info['COURSE_DESP'] = $("#courseReg_courseDesp").val()
    course_info['CREDIT_UNIT'] = $("#courseReg_creditUnit").val()
    course_info['GE_PROPOSED_AREA'] = $("#courseReg_geArea").val()
    course_info['MEDIUM_OF_INSTRUCTION'] = $("#courseReg_mediumInstruction").val()
    course_info['MEDIUM_OF_ASSESSMENT'] = $("#courseReg_mediumAsm").val()
    course_info['PRECURSORS'] = $("#courseReg_precursors").val()
    course_info['EQUIVALENT_COURSES'] = $("#courseReg_equivalentCourses").val()
    course_info['EXCLUSIVE_COURSES'] = $("#courseReg_exclusiveCourses").val()
    course_info['HAVE_TUTORIAL'] = $("#courseReg_haveTut").val()
    if ($("#courseReg_tutDesp").val() != "") {
        course_info['TUTORIAL_DESP'] = $("#courseReg_tutDesp").val()
    }
    // course_info['LAST_UPDATE_BY']=$("#").val()
    // course_info['LAST_UPDATE_DATE']=$("#").val()
    if (action == 'update') {
        course_info['COURSE_INFO_ID'] = $("#courseReg_infoId").text()
    }

    for (let i = 1; i < 11; i++) {
        let getAsm = '.courseReg_asm' + i
        let getSyllabus = '.courseReg_syllabus' + i
        // console.log(data_type)
        let asmList = loopEachElement(getAsm)
        let syllabusList = loopEachElement(getSyllabus)
        // console.log(list)
        if (asmList != false) {
            course_assessments[i] = asmList
        }
        if (syllabusList != false) {
            course_syllabus[i] = syllabusList
        }
        // console.log(course_assessments)
    }
    console.log(course_assessments)
    console.log(course_syllabus)
    console.log(course_info)

    $.ajax({
        url: url,
        data: {
            'course_info': JSON.stringify(course_info),
            'course_assessments': JSON.stringify(course_assessments),
            'course_syllabus': JSON.stringify(course_syllabus)
        },
        type: 'post',
        headers: {'X-CSRFToken': csrftoken},
    }).done(function (ret) {
        var result = JSON.parse(ret)
        console.log(result)
        if (result['result'] === true) {
            if (action == 'update') {
                alert('Course updated successfully.')
            } else {
                alert('Course registered successfully.')
            }
        } else {
            alert('Failed to perform your action.')
        }
    })

}

$("#btn_courseRegSubmit").click(function () {
    if (validate() == true) {
        url = '/nlpApp/ajax_courseRegistration/'
        action = 'register'
        getData(action, url)
        $("#btn_courseRegClear").click()
    }
})

$("#btn_courseDuplicate").click(function () {
    if (validate() == true) {
        url = '/nlpApp/ajax_courseRegistration/'
        action = 'duplicate'
        getData(action, url)
    }
})

$("#btn_courseUpdate").click(function () {
    if (validate() == true) {
        url = '/nlpApp/ajax_courseUpdate/'
        action = 'update'
        getData(action, url)
    }
})

$("#btn_courseRegClear").click(function () {
    $("input").each(function () {
        $(this).val("")
    })
    $("textarea").each(function () {
        $(this).val("")
    })
    $("select").each(function () {
        $(this).val("")
    })
})