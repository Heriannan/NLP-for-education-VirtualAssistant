$(document).ready(function () {})
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

$("#signup_checkbox").click(function(){
    if(this.checked){
        $(".email_block").removeClass('d-none')
    }
    else{
        $(".email_block").addClass('d-none')
    }
})

$("#btn_login").click(function (){
     //check not null
    let data = {};
    data['USERNAME'] = $("#login_username").val()
    data['PASSWORD'] = $.md5($("#login_password").val())
    //pass data to backend
     $.ajax({
            url: '/nlpApp/login_authentication/',
            data: {'data': JSON.stringify(data)},
            type: 'post',
            headers: {'X-CSRFToken': csrftoken },
        }).done(function (data) {
        if (data.success){
            // window.open('/nlpApp/courseRegistration/')
             window.location.href = data.url;
        }
        else{
            $("#login_error").html("Invalid username or password.")
        }
    })
})

$("#btn_signup").click(function (){
    //pass data to backend
    let data = {};
    data['USERNAME'] = $("#login_username").val()
    data['PASSWORD'] = $.md5($("#login_password").val())
    data['EMAIL'] = $("#login_email").val()
    //check not null
    alert(data)
    $.ajax({
        url: '/nlpApp/signup_account/',
        data: { 'data': JSON.stringify(data) },
        type: 'post',
        headers: {'X-CSRFToken': csrftoken },
    }).done(function (ret) {
        console.log('ajax finished')
        var result = JSON.parse(ret)
        console.log(result)
        if (result['result'] === true){
            alert ('Account created successfully!')
        }
        else{
            alert('Username or Email is already taken.')
        }
    })
})
