from sqlalchemy import Column, ForeignKey, func, literal_column
from sqlalchemy.dialects.mssql import NVARCHAR, CHAR, INTEGER, NUMERIC, DATETIME2, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, column_property

# 创建对象的基类:
Base = declarative_base()


class COURSE_ASSESSMENTS(Base):
    __tablename__ = 'COURSE_ASSESSMENTS'
    __table_args__ = {'implicit_returning': False}
    COURSE_ASSESSMENTS_ID = Column(INTEGER, primary_key=True)
    COURSE_INFO_ID = Column(INTEGER)
    ASSESSMENT_TYPE = Column(NVARCHAR(50))
    DETAILS = Column(NVARCHAR(4000))
    WEIGHTING = Column(NVARCHAR(10))
    SUBMIT_DATE = Column(DATETIME2)


class COURSE_INFO(Base):
    __tablename__ = 'COURSE_INFO'
    __table_args__ = {'implicit_returning': False}
    COURSE_INFO_ID = Column(INTEGER, primary_key=True)
    COURSE_NAME = Column(NVARCHAR(50))
    COURSE_CODE = Column(NVARCHAR(50))
    ACADEMIC_YEAR_FROM = Column(INTEGER)
    ACADEMIC_YEAR_TO = Column(INTEGER)
    ACADEMIC_SEMESTER = Column(NVARCHAR(50))
    TEACHER_LECTURER = Column(NVARCHAR(50))
    TEACHER_TA = Column(NVARCHAR(500))
    COURSE_DESP = Column(NVARCHAR(4000))
    CREDIT_UNIT = Column(INTEGER)
    GE_PROPOSED_AREA = Column(INTEGER)
    MEDIUM_OF_INSTRUCTION = Column(NVARCHAR(10))
    MEDIUM_OF_ASSESSMENT = Column(NVARCHAR(10))
    PREREQUISITES = Column(NVARCHAR(500))
    PRECURSORS = Column(NVARCHAR(500))
    EQUIVALENT_COURSES = Column(NVARCHAR(500))
    EXCLUSIVE_COURSES = Column(NVARCHAR(500))
    HAVE_TUTORIAL = Column(CHAR(1))
    TUTORIAL_DESP = Column(NVARCHAR(4000))
    HAVE_ASSESSMENTS = Column(CHAR(1))
    COURSE_START_DAY = Column(DATETIME2)
    CREATE_BY = Column(NVARCHAR(50))
    CREATE_DATE = Column(DATETIME2)
    LAST_UPDATE_BY = Column(NVARCHAR(50))
    LAST_UPDATE_DATE = Column(DATETIME2)

    last_update_date_st = column_property(
        func.convert(literal_column('VARCHAR(10)'), LAST_UPDATE_DATE, literal_column('23')))
    course_start_date_st = column_property(
        func.convert(literal_column('VARCHAR(10)'), COURSE_START_DAY, literal_column('23')))


class COURSE_SYLLABUS(Base):
    __tablename__ = 'COURSE_SYLLABUS'
    __table_args__ = {'implicit_returning': False}
    COURSE_SYLLABUS_ID = Column(INTEGER, primary_key=True)
    COURSE_INFO_ID = Column(INTEGER)
    COURSE_SYLLABUS = Column(NVARCHAR(50))
    COURSE_SYLLABUS_DESP = Column(NVARCHAR(4000))

class QA_CONTEXT(Base):
    __tablename__ = 'QA_CONTEXT'
    __table_args__ = {'implicit_returning': False}
    ID = Column(INTEGER, primary_key=True)
    COURSE_INFO_ID = Column(INTEGER)
    CONTEXT = Column(NVARCHAR)
    LECTURE = Column(FLOAT)

class QUIZ_QUESTION(Base):
    __tablename__ = 'QUIZ_QUESTION'
    __table_args__ = {'implicit_returning': False}
    ID = Column(INTEGER, primary_key=True)
    COURSE_INFO_ID = Column(INTEGER)
    CONTEXT = Column(NVARCHAR(4000))
    QUESTION = Column(NVARCHAR(500))
    ANSWER = Column(NVARCHAR(500))
    LECTURE = Column(FLOAT)


class INFO_ENQUIRY(Base):
    __tablename__ = 'INFO_ENQUIRY'
    __table_args__ = {'implicit_returning': False}

    ID = Column(INTEGER, primary_key=True)
    QUESTION = Column(NVARCHAR(300))
    CATEGORY = Column(NVARCHAR(50))
    COURSE_INFO_ID = Column(NVARCHAR(50))
    DATE = Column(DATETIME2(7))


class SENTIMENT_ANALYSIS(Base):
    __tablename__ = 'SENTIMENT_ANALYSIS'
    __table_args__ = {'implicit_returning': False}

    ID = Column(INTEGER, primary_key=True)
    COMMENT = Column(NVARCHAR(300))
    CATEGORY = Column(NVARCHAR(50))
    COURSE_INFO_ID = Column(NVARCHAR(50))
    DATE = Column(DATETIME2(7))


class QUESTION_ANSWERING(Base):
    __tablename__ = 'QUESTION_ANSWERING'
    __table_args__ = {'implicit_returning': False}

    ID = Column(INTEGER, primary_key=True)
    QUESTION = Column(NVARCHAR(300))
    ANSWER = Column(NVARCHAR(300))
    LECTURE = Column(FLOAT(5))
    COURSE_INFO_ID = Column(NVARCHAR(50))
    DATE = Column(DATETIME2(7))


class USER(Base):
    __tablename__ = 'USER'
    __table_args__ = {'implicit_returning': False}
    USERNAME = Column(NVARCHAR(50), primary_key=True)
    PASSWORD = Column(NVARCHAR(50))
    EMAIL = Column(NVARCHAR(50))
