import hashlib
import json
import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from sqlalchemy import or_

from nlpApp.classModel.Models import USER, COURSE_INFO, COURSE_SYLLABUS, COURSE_ASSESSMENTS, INFO_ENQUIRY, \
    QUESTION_ANSWERING, SENTIMENT_ANALYSIS
from nlpApp.util.report import generateReport
from nlpApp.views.constants import ge_proposed_area, academic_semester, medium, yes_no
from nlpProject.settings import Session

logger = logging.getLogger(__name__)
info_result = {}
context={}


def return_ten_item(dataList):
    if len(dataList) < 10:
        for each in range(10 - len(dataList)):
            dataList.append(None)
    return dataList

def index(request):
    return render(request, 'index.html')


def url_courseRegistration(request):
    context['current_login'] = request.session.get('user')
    logger.info(f'passed login: {context["current_login"] }')
    context['action'] = 'actionReg'
    return render(request, 'courseRegistration.html', context=context)

def url_courseEnquire(request):
    context['current_login'] = request.session.get('user')
    logger.info(f'passed login: {context["current_login"] }')
    return render(request, 'courseEnquire.html', context=context)

def url_courseDetail(request):
    context['current_login'] = request.session.get('user')
    logger.info(f'passed login: {context["current_login"] }')

    course_info_id = ''
    btnType = ''

    course_info_id = request.POST.get('course_info_id')
    btnType = request.POST.get('btnType')

    logger.info(f'course_info_id:{course_info_id}')
    logger.info(f'btnType:{btnType}')


    # query database to get the detail
    session = Session()
    course_info = session.query(COURSE_INFO).filter(course_info_id == COURSE_INFO.COURSE_INFO_ID).one()
    course_syllabus = session.query(COURSE_SYLLABUS).filter(course_info_id == COURSE_SYLLABUS.COURSE_INFO_ID).all()
    course_assessments = session.query(COURSE_ASSESSMENTS).filter(course_info_id == COURSE_ASSESSMENTS.COURSE_INFO_ID).all()
    logger.info(f'course_assessments:{course_assessments}')
    logger.info(type(course_assessments))

    context['course_info'] = course_info
    context['course_syllabus'] = return_ten_item(course_syllabus)
    context['course_assessments'] = return_ten_item(course_assessments)
    context['action'] = btnType
    context['ge_proposed_area'] = ge_proposed_area
    context['academic_semester'] = academic_semester
    context['medium'] = medium
    context['yes_no'] = yes_no
    return render(request, 'courseDetail.html', context=context)
    # return render(request, 'courseDetail.html', context=context)


def login_authentication(request):
    # if request.method == 'POST':
    login_para = json.loads(request.POST.get('data'))
    login_username = login_para['USERNAME']
    login_password = login_para['PASSWORD']

    # login_username = request.POST.get('username')
    # login_password = hashlib.md5(request.POST.get('password'))

    logger.info(f'username:{login_username},password:{login_password}')
    session = Session()
    current_login = session.query(USER) \
        .filter(USER.USERNAME == login_username) \
        .filter(USER.PASSWORD == login_password).one_or_none()
    logger.info(f'have user:{current_login}')
    if current_login:
        request.session['user'] = current_login.USERNAME
        session_user = request.session.get('user')
        logger.info(f'Session: {session_user}')
        return JsonResponse({
            'success': True,
            'url': reverse('courseEnquire'),
            # 'url': reverse('courseRegistration', args=[current_login.USERNAME]),
        })

    else:
        return JsonResponse({ 'success': False })

        # eJSON = json.dumps(info_result, default=str)
        # return HttpResponse(json.dumps(eJSON), content_type='application/json')

def url_courseReport(request):
    # "ask question, question category, count occurance"
    # logger.info()

    context['current_login'] = request.session.get('user')
    logger.info(f'passed login: {context["current_login"]}')

    course_info_id = ''
    btnType = ''

    course_info_id = request.POST.get('course_info_id')
    btnType = request.POST.get('btnType')

    session = Session()
    courseInfo = session.query(COURSE_INFO).filter(COURSE_INFO.COURSE_INFO_ID == course_info_id).one()
    infoEnquiry = session.query(INFO_ENQUIRY).filter(INFO_ENQUIRY.COURSE_INFO_ID == course_info_id).all()
    knowledgeEnquiry = session.query(QUESTION_ANSWERING).filter(QUESTION_ANSWERING.COURSE_INFO_ID == course_info_id).all()
    sentimentAnalysis = session.query(SENTIMENT_ANALYSIS).filter(SENTIMENT_ANALYSIS.COURSE_INFO_ID == course_info_id).all()
    # print(knowledgeEnquiry[23].LECTURE)
    report = generateReport(courseInfo, infoEnquiry, knowledgeEnquiry, sentimentAnalysis)

    return report

def signup_account(request):
    logger.info('signup_account')
    signup_para = json.loads(request.POST.get('data'))
    signup_username = signup_para['USERNAME']
    signup_password = signup_para['PASSWORD']
    signup_email = signup_para['EMAIL']

    logger.info(f'username:{signup_username},password:{signup_password},email:{signup_email}')
    session = Session()
    # check_username_exist = session.query(USER).all()
    check_username_exist = session.query(USER) \
        .filter(or_(USER.USERNAME == signup_username, USER.EMAIL == signup_email)).all()

    if not check_username_exist:

        user = USER(**signup_para)
        session.add(user)
        session.commit()
        session.refresh(user)
        username = user.USERNAME

        logger.info(f'registered user: {username}')

        info_result['result'] = True
    else:
        logger.info(f'username or email is taken already.')
        info_result['result'] = False

    logger.info(info_result)

    eJSON = json.dumps(info_result, default=str)
    return HttpResponse(json.dumps(eJSON), content_type='application/json')

def ajax_courseRegistration(request):
    current_login= request.session.get('user')

    course_info_para =json.loads(request.POST.get('course_info'))
    course_assessments_dict =json.loads(request.POST.get('course_assessments'))
    course_syllabus_dict =json.loads(request.POST.get('course_syllabus'))
    course_assessments_para={}
    course_syllabus_para={}

    del_list = []
    for key in course_info_para.keys():
        if course_info_para[key] == "":
            del_list.append(key)

    for key in del_list:
        del course_info_para[key]
    logger.info(course_info_para)

    course_info_para['CREATE_BY']=current_login
    course_info_para['CREATE_DATE']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    course_info_para['LAST_UPDATE_BY']=current_login
    course_info_para['LAST_UPDATE_DATE']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f'course_info_para: {course_info_para}')
    session = Session()
    # save the course information first
    course_info = COURSE_INFO(**course_info_para)
    session.add(course_info)
    session.commit()
    session.refresh(course_info)
    logger.info(f'course_info_id: {course_info.COURSE_INFO_ID}')

    # get the info id and use it to store the assessments and syllabus
    logger.info(course_syllabus_dict)
    course_syllabus_para['COURSE_INFO_ID'] = course_info.COURSE_INFO_ID
    for col in course_syllabus_dict:
        logger.info(f'each col: {course_syllabus_dict[col]}')
        row = course_syllabus_dict[col]
        if row[0]!="":
            course_syllabus_para['COURSE_SYLLABUS'] = row[0]
        if row[1]!="":
            course_syllabus_para['COURSE_SYLLABUS_DESP'] = row[1]
        course_syllabus = COURSE_SYLLABUS(**course_syllabus_para)
        session.add(course_syllabus)
        session.commit()
        session.refresh(course_syllabus)

    # get the info id and use it to store the assessments and syllabus
    logger.info(course_assessments_dict)
    course_assessments_para['COURSE_INFO_ID'] = course_info.COURSE_INFO_ID
    for col in course_assessments_dict:
        logger.info(f'each col: {course_assessments_dict[col]}')
        row = course_assessments_dict[col]
        if row[0] != "":
            course_assessments_para['ASSESSMENT_TYPE'] = row[0]
        if row[1] != "":
            course_assessments_para['WEIGHTING'] = row[1]
        if row[2] != "":
            course_assessments_para['SUBMIT_DATE'] = row[2]
        if row[3] != "":
            course_assessments_para['DETAILS'] = row[3]
        course_assessments = COURSE_ASSESSMENTS(**course_assessments_para)
        session.add(course_assessments)
        session.commit()
        session.refresh(course_assessments)

    info_result['result'] = True


    eJSON = json.dumps(info_result, default=str)
    return HttpResponse(json.dumps(eJSON), content_type='application/json')

def ajax_courseUpdate(request):
    course_info_id = ""
    current_login= request.session.get('user')

    course_info_para =json.loads(request.POST.get('course_info'))
    course_assessments_dict =json.loads(request.POST.get('course_assessments'))
    course_syllabus_dict =json.loads(request.POST.get('course_syllabus'))
    course_assessments_para={}
    course_syllabus_para={}

    del_list = []
    logger.info(course_info_para.keys())
    for key in course_info_para.keys():
        if course_info_para[key] == "":
            del_list.append(key)
        if key == "COURSE_INFO_ID":
            del_list.append(key)
            course_info_id = course_info_para["COURSE_INFO_ID"]
    logger.info(f'course_info_id: {course_info_id}')
    for key in del_list:
        del course_info_para[key]
    logger.info(course_info_para)

    # course_info_para['CREATE_BY']=current_login
    # course_info_para['CREATE_DATE']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    course_info_para['LAST_UPDATE_BY']=current_login
    course_info_para['LAST_UPDATE_DATE']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f'course_info_para: {course_info_para}')
    session = Session()
    session.query(COURSE_INFO)\
        .filter(COURSE_INFO.COURSE_INFO_ID == course_info_id)\
        .update(course_info_para)
    session.commit()

    # # save the course information first
    # course_info = COURSE_INFO(**course_info_para)
    # session.add(course_info)
    # session.commit()
    # session.refresh(course_info)
    # logger.info(f'course_info_id: {course_info.COURSE_INFO_ID}')

    # delete all record
    session.query(COURSE_SYLLABUS).filter(COURSE_SYLLABUS.COURSE_INFO_ID == course_info_id).delete()
    session.query(COURSE_ASSESSMENTS).filter(COURSE_ASSESSMENTS.COURSE_INFO_ID == course_info_id).delete()
    session.commit()
    # session.refresh(COURSE_SYLLABUS)
    # session.refresh(COURSE_ASSESSMENTS)

    # add record
    logger.info(course_syllabus_dict)
    course_syllabus_para['COURSE_INFO_ID'] = course_info_id
    for col in course_syllabus_dict:
        logger.info(f'each col: {course_syllabus_dict[col]}')
        row = course_syllabus_dict[col]
        if row[0]!="":
            course_syllabus_para['COURSE_SYLLABUS'] = row[0]
        if row[1]!="":
            course_syllabus_para['COURSE_SYLLABUS_DESP'] = row[1]
        course_syllabus = COURSE_SYLLABUS(**course_syllabus_para)
        session.add(course_syllabus)
        session.commit()
        session.refresh(course_syllabus)

    # get the info id and use it to store the assessments and syllabus
    logger.info(course_assessments_dict)
    course_assessments_para['COURSE_INFO_ID'] = course_info_id
    for col in course_assessments_dict:
        logger.info(f'each col: {course_assessments_dict[col]}')
        row = course_assessments_dict[col]
        if row[0] != "":
            course_assessments_para['ASSESSMENT_TYPE'] = row[0]
        if row[1] != "":
            course_assessments_para['WEIGHTING'] = row[1]
        if row[2] != "":
            course_assessments_para['SUBMIT_DATE'] = row[2]
        if row[3] != "":
            course_assessments_para['DETAILS'] = row[3]
        course_assessments = COURSE_ASSESSMENTS(**course_assessments_para)
        session.add(course_assessments)
        session.commit()
        session.refresh(course_assessments)

    info_result['result'] = True


    eJSON = json.dumps(info_result, default=str)
    return HttpResponse(json.dumps(eJSON), content_type='application/json')

def ajax_search(request):
    filter_list = []
    course_code= request.POST.get("course_code")
    course_name= request.POST.get("course_name")
    academic_year_from= request.POST.get("academic_year_from")
    academic_year_to= request.POST.get("academic_year_to")
    create_by= request.POST.get("create_by")
    session = Session()

    if course_code != "":
        filter_list.append(COURSE_INFO.COURSE_CODE.ilike(f'%{course_code}%'))
    if course_name != "":
        filter_list.append(COURSE_INFO.COURSE_NAME.ilike(f'%{course_name}%'))
    if academic_year_from != "":
        filter_list.append(COURSE_INFO.ACADEMIC_YEAR_FROM >= academic_year_from)
    if academic_year_to != "":
        filter_list.append(COURSE_INFO.ACADEMIC_YEAR_TO <= academic_year_to)
    if create_by != "":
        filter_list.append(COURSE_INFO.CREATE_BY == create_by)

    query = session.query(COURSE_INFO)

    result = query.filter(*filter_list).order_by(COURSE_INFO.COURSE_INFO_ID.asc()).all()


    cols = [x["name"] for x in query.column_descriptions]
    info_result = []
    # logger.info('result')
    # logger.info(len(result))
    for row in result:
        # logger.info('row')
        # logger.info(row)
        info_row = {}
        for column in row.__table__.columns:
            field = str(getattr(row, column.name))
            if field == 'None':
                field = ''
            info_row[column.name] = field
        info_result.append(info_row)
    session.close()
    # ///('hi')
    logger.info(info_result)
    eJSON = json.dumps(info_result, default=str)
    return HttpResponse(json.dumps(eJSON), content_type='application/json')


    # list=[]
    # current_login= request.session.get('user')
    #
    # session = Session()
    #
    # result = session.query(COURSE_INFO).order_by(COURSE_INFO.COURSE_INFO_ID.asc()).all()
    #
    # # cols = [x["name"] for x in result.column_descriptions]
    # for row in result:
    #     logger.info(row)
    #     info_row = {}
    #     for column in row.__table__.columns:
    #         info_row[column] = getattr(row, column.name)
    #         logger.info(info_row)
    #
    #     list.append(info_row)
    #
    # session.close()
    #
    # eJSON = json.dumps(list, default=str)
    # return HttpResponse(json.dumps(eJSON), content_type='application/json')
