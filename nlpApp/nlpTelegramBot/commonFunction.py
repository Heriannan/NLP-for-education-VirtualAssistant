import collections
import logging
import numpy as np
from datetime import datetime

from torch.cuda import device
from transformers import default_data_collator
from tqdm.auto import tqdm
from nlpApp.classModel.Models import COURSE_INFO, INFO_ENQUIRY, SENTIMENT_ANALYSIS, QUIZ_QUESTION, QA_CONTEXT, \
    QUESTION_ANSWERING, COURSE_ASSESSMENTS, COURSE_SYLLABUS
from nlpProject.settings import Session
from sqlalchemy import insert
import numpy
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel, Trainer, TrainingArguments, \
    AutoModelForQuestionAnswering
import torch
from torch import cuda

logger = logging.getLogger(__name__)

label_names = ["ASSESSMENT_INFO", "COURSE_DESP", "COURSE_NAME", "COURSE_START_DAY", "CREDIT_UNIT",
               "COURSE_REGISTRATION", "GE_PROPOSED_AREA", "TUTORIAL_INFO", "MEDIUM", "TEACHER", "COURSE_SYLLABUS"]

tokenizer = AutoTokenizer.from_pretrained("roberta-base")
model_checkpoint = "roberta-base"
device = 'cuda' if cuda.is_available() else 'cpu'
MAX_LEN = 512

# sa_model_dir = '/nlpApp/nlpModels/sentimentAnalysis/'
print('start to load model...')

qa_model_dir = r'''C:\nlpProject\nlpApp\nlpModels\questionAnswering'''
qa_loaded_model = AutoModelForQuestionAnswering.from_pretrained(qa_model_dir)


def searchCourse(courseCode):
    courseCode = courseCode
    session = Session()
    course = session.query(COURSE_INFO) \
        .filter(COURSE_INFO.COURSE_CODE.ilike(f'%{courseCode}%')).all()
    if course:
        courseInfo = []
        for each in course:
            courseInfo.append(f'ID: {each.COURSE_INFO_ID}\n'
                              f'Course Code: {each.COURSE_CODE}\n'
                              f'Course Name: {each.COURSE_NAME}\n'
                              f'Semester: {each.ACADEMIC_YEAR_FROM}-{each.ACADEMIC_YEAR_TO} sem {each.ACADEMIC_SEMESTER}\n'
                              f'Lecturer: {each.TEACHER_LECTURER}\n')
        return courseInfo
    return False


def getCourse(courseInfoId):
    print(f'passed id: {courseInfoId}')
    session = Session()
    course = session.query(COURSE_INFO) \
        .filter(COURSE_INFO.COURSE_INFO_ID == courseInfoId).one_or_none()
    if course:
        print(course)
        return course
    return False


def get_key(val, my_dict):
    for key, value in my_dict.items():
        if val == value:
            return key


def classify_courseInfo(sentence, in_loaded_model):
    encode_dict = {'ASSESSMENT_INFO': 0,
                   'COURSE_DESP': 1,
                   'COURSE_NAME': 2,
                   'COURSE_REGISTRATION': 3,
                   'COURSE_START_DAY': 4,
                   'COURSE_SYLLABUS': 5,
                   'CREDIT_UNIT': 6,
                   'GE_PROPOSED_AREA': 7,
                   'MEDIUM': 8,
                   'TEACHER': 9,
                   'TUTORIAL_INFO': 10}
    in_loaded_model.eval()

    inputs = tokenizer.encode_plus(
        sentence,
        None,
        add_special_tokens=True,
        max_length=MAX_LEN,
        pad_to_max_length=True,
        return_token_type_ids=True,
        truncation=True
    )
    ids = torch.tensor(inputs['input_ids']).to(device, dtype=torch.long)
    mask = torch.tensor(inputs['attention_mask']).to(device, dtype=torch.long)
    outputs = in_loaded_model(ids.unsqueeze(0), mask.unsqueeze(0))
    big_val, big_idx = torch.max(outputs.data, dim=1)
    index = big_idx.item()
    print(f'index:{index}')
    class_name = get_key(index, encode_dict)

    print(f'completed:{class_name}')
    return class_name


def classify_comment(sentence, courseInfoId, sa_loaded_model):
    print(f'classify comment:{sentence}')
    encode_dict = {'Have room of improvements': 0, 'Disappointed': 1, 'Normal': 2, 'Good': 3, 'Excellent': 4}

    print('loaded model')
    sa_loaded_model.eval()
    print(sa_loaded_model)

    inputs = tokenizer.encode_plus(
        sentence,
        None,
        add_special_tokens=True,
        max_length=MAX_LEN,
        pad_to_max_length=True,
        return_token_type_ids=True,
        truncation=True
    )
    ids = torch.tensor(inputs['input_ids']).to(device, dtype=torch.long)
    mask = torch.tensor(inputs['attention_mask']).to(device, dtype=torch.long)
    outputs = sa_loaded_model(ids.unsqueeze(0), mask.unsqueeze(0))
    # print(outputs, outputs.shape)
    big_val, big_idx = torch.max(outputs.data, dim=1)
    # print(big_val)
    # print(big_idx)
    # _, prediction = torch.max(output, dim=1)
    index = big_idx.item()
    print(f'index:{index}')
    result = get_key(index, encode_dict)

    print(f'completed:{result}')
    session = Session()
    # save the question in the db for report generation
    stmt = (
        insert(SENTIMENT_ANALYSIS).values(COURSE_INFO_ID=courseInfoId, COMMENT=sentence, CATEGORY=result,
                                          DATE=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    print(stmt)
    session.execute(stmt)
    session.commit()

    return result


def map_label(int):
    return label_names[int]


def generateCourseInfoResponse(courseInfoId, class_name, question):
    session = Session()
    # save the question in the db for report generation
    stmt = (
        insert(INFO_ENQUIRY).values(COURSE_INFO_ID=courseInfoId, QUESTION=question, CATEGORY=class_name,
                                    DATE=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    print(stmt)
    session.execute(stmt)
    session.commit()

    course = session.query(COURSE_INFO) \
        .filter(COURSE_INFO.COURSE_INFO_ID == courseInfoId).one_or_none()
    if course:
        if class_name == "COURSE_DESP":
            return course.COURSE_DESP
        elif class_name == "COURSE_NAME":
            return course.COURSE_NAME
        elif class_name == "CREDIT_UNIT":
            return course.CREDIT_UNIT
        elif class_name == "GE_PROPOSED_AREA":
            return course.GE_PROPOSED_AREA
        elif class_name == "COURSE_REGISTRATION":
            response = f"Here are some course registration information:\n" \
                       f"PREREQUISITES: {course.PREREQUISITES}\n" \
                       f"PRECURSORS: {course.PRECURSORS}\n" \
                       f"EQUIVALENT COURSES: {course.EQUIVALENT_COURSES}\n" \
                       f"EXCLUSIVE COURSES: {course.EXCLUSIVE_COURSES}\n"
            return response
        elif class_name == "TUTORIAL_INFO":
            response = f"Here are some tutorial information:\n" \
                       f"HAVE TUTORIAL: {course.HAVE_TUTORIAL}\n" \
                       f"TUTORIAL DESP: {course.TUTORIAL_DESP}"
            return response
        elif class_name == "MEDIUM":
            response = f"Here are some course medium information:\n" \
                       f"MEDIUM OF INSTRUCTION: {course.MEDIUM_OF_INSTRUCTION}\n" \
                       f"MEDIUM OF ASSESSMENT: {course.MEDIUM_OF_ASSESSMENT}"
            return response
        elif class_name == "TEACHER":
            response = f"Here are some course teacher information:\n" \
                       f"LECTURER: {course.TEACHER_LECTURER}\n" \
                       f"TEACHING ASSISTANT: {course.TEACHER_TA}"
            return response
        elif class_name == "COURSE_START_DAY":
            return course.COURSE_START_DAY
        elif class_name == "ASSESSMENT_INFO":
            asm = session.query(COURSE_ASSESSMENTS) \
                .filter(COURSE_ASSESSMENTS.COURSE_INFO_ID == courseInfoId).all()
            if len(asm)>0:
                response = f"The course has {len(asm)} assessments: \n"
                count = 0
                for each in asm:
                    count+=1
                    response += f'{count}.\n' \
                                f'ASSESSMENT TYPE:{each.ASSESSMENT_TYPE}\n' \
                                f'WEIGHTING: {each.WEIGHTING}\n' \
                                f'SUBMIT DATE: {each.SUBMIT_DATE}\n' \
                                f'DETAILS: {each.DETAILS}\n'
                return response
            else:
                return 'There is no any assessments information about this course.'
        elif class_name == "COURSE_SYLLABUS":
            syllabus = session.query(COURSE_SYLLABUS) \
                .filter(COURSE_SYLLABUS.COURSE_INFO_ID == courseInfoId).all()
            if len(syllabus) > 0:
                response = f"The course has {len(syllabus)} syllabus: \n"
                count = 0
                for each in syllabus:
                    count += 1
                    response += f'{count}.\n' \
                                f'COURSE SYLLABUS:{each.COURSE_SYLLABUS}\n' \
                                f'COURSE SYLLABUS DESCRIPTION: {each.COURSE_SYLLABUS_DESP}\n'
                return response
            else:
                return 'There is no any assessments information about this course.'
        else:
            return "Sorry, I can't find this information. Try another"

    return "Sorry, I can't find this course. Try another."


def searchLecture(courseInfoId):
    print(f'passed info id: {courseInfoId}')
    session = Session()
    lecture_list = session.query(QUIZ_QUESTION.LECTURE) \
        .filter(QUIZ_QUESTION.COURSE_INFO_ID == courseInfoId).distinct().all()
    if lecture_list:
        format_number = []
        for num in lecture_list:
            format_number.append(num[0])
        format_number.sort()
        msg = f'There are questions from {len(lecture_list)} lecture(s).\n' \
              f'Chapter(s): {format_number}\n' \
              f'Please select one chapter and input the number.'
        return msg
    return False


def searchContext(courseInfoId):
    print(f'passed info id: {courseInfoId}')
    session = Session()
    context_list = session.query(QA_CONTEXT.LECTURE) \
        .filter(QA_CONTEXT.COURSE_INFO_ID == courseInfoId).all()
    if context_list:
        format_number = []
        for num in context_list:
            format_number.append(num[0])
        format_number.sort()
        msg = f'There are {len(context_list)} lecture(s) stored.\n' \
              f'Chapter(s): {format_number}\n' \
              f'Please select one chapter and input the number.'
        return msg
    return False


def validateLecture(lec_no):
    print(f'passed info id: {lec_no}')
    session = Session()
    question = session.query(QUIZ_QUESTION) \
        .filter(QUIZ_QUESTION.LECTURE == lec_no).all()
    if question:
        question_id = []
        question_list = {}
        for each in question:
            question_id.append(each.ID)
            question_list[each.ID] = [each.QUESTION, each.ANSWER]
        return question_list, question_id
    return False, False


def validateContext(lec_no):
    print(f'passed info id: {lec_no}')
    session = Session()
    context = session.query(QA_CONTEXT.CONTEXT) \
        .filter(QA_CONTEXT.LECTURE == lec_no).one_or_none()
    if context:
        print(f'context: {context[0]}')
        context_list = context[0].split('<sep>')
        return context_list
    return False


def selectContext(question, contextList):
    print(f'context list:{contextList}')
    # remove non keyword
    keyword_list = question.split(' ')
    del_keyword_list = ['is', 'am', 'are', 'Who', 'What', 'where', 'when', 'why', 'i', 'dont', 'do', 'can', 'how']

    for each in del_keyword_list:
        if each in keyword_list:
            keyword_list.remove(each)

    # gives the count of `word in text`
    def matches(text):
        return sum(word in text.lower() for word in keyword_list)
    # print the one with the highest count of matches
    context = max(contextList, key=matches)
    print(f'selected context: {context}')
    return context


from datasets import Dataset


def format_user_input(context, question):
    input_dict = {'id': ['1'], 'context': [context], 'question': [question]}
    single_input = Dataset.from_dict(input_dict)
    print(single_input)
    return single_input


def prepare_single_test_features(examples):
    max_length = 384  # 输入feature的最大长度，question和context拼接之后
    doc_stride = 128  # 2个切片之间的重合token数量。
    pad_on_right = tokenizer.padding_side == "right"  # context在右边
    # Tokenize our examples with truncation and maybe padding, but keep the overflows using a stride. This results
    # in one example possible giving several features when a context is long, each of those features having a
    # context that overlaps a bit the context of the previous feature.
    tokenized_examples = tokenizer(
        examples["question" if pad_on_right else "context"],
        examples["context" if pad_on_right else "question"],
        truncation="only_second" if pad_on_right else "only_first",
        max_length=max_length,
        stride=doc_stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    # Since one example might give us several features if it has a long context, we need a map from a feature to
    # its corresponding example. This key gives us just that.
    sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")

    # We keep the example_id that gave us this feature and we will store the offset mappings.
    tokenized_examples["example_id"] = []

    for i in range(len(tokenized_examples["input_ids"])):
        # Grab the sequence corresponding to that example (to know what is the context and what is the question).
        sequence_ids = tokenized_examples.sequence_ids(i)
        context_index = 1 if pad_on_right else 0

        # One example can give several spans, this is the index of the example containing this span of text.
        sample_index = sample_mapping[i]
        tokenized_examples["example_id"].append(examples["id"][sample_index])

        # Set to None the offset_mapping that are not part of the context so it's easy to determine if a token
        # position is part of the context or not.
        tokenized_examples["offset_mapping"][i] = [
            (o if sequence_ids[k] == context_index else None)
            for k, o in enumerate(tokenized_examples["offset_mapping"][i])
        ]

    return tokenized_examples


def postprocess_qa_predictions(examples, features, raw_predictions, n_best_size=20, max_answer_length=30):
    squad_v2 = False
    all_start_logits, all_end_logits = raw_predictions
    # Build a map example to its corresponding features.
    example_id_to_index = {k: i for i, k in enumerate(examples["id"])}
    features_per_example = collections.defaultdict(list)
    for i, feature in enumerate(features):
        features_per_example[example_id_to_index[feature["example_id"]]].append(i)

    # The dictionaries we have to fill.
    predictions = collections.OrderedDict()

    # Logging.
    print(f"Post-processing {len(examples)} example predictions split into {len(features)} features.")

    # Let's loop over all the examples!
    for example_index, example in enumerate(tqdm(examples)):
        # Those are the indices of the features associated to the current example.
        feature_indices = features_per_example[example_index]

        min_null_score = None  # Only used if squad_v2 is True.
        valid_answers = []

        context = example["context"]
        # Looping through all the features associated to the current example.
        for feature_index in feature_indices:
            # We grab the predictions of the model for this feature.
            start_logits = all_start_logits[feature_index]
            end_logits = all_end_logits[feature_index]
            # This is what will allow us to map some the positions in our logits to span of texts in the original
            # context.
            offset_mapping = features[feature_index]["offset_mapping"]

            # Update minimum null prediction.
            cls_index = features[feature_index]["input_ids"].index(tokenizer.cls_token_id)
            feature_null_score = start_logits[cls_index] + end_logits[cls_index]
            if min_null_score is None or min_null_score < feature_null_score:
                min_null_score = feature_null_score

            # Go through all possibilities for the `n_best_size` greater start and end logits.
            start_indexes = np.argsort(start_logits)[-1: -n_best_size - 1: -1].tolist()
            end_indexes = np.argsort(end_logits)[-1: -n_best_size - 1: -1].tolist()

            # to turn [[][][][]] to [None,None,None]
            for i in range(len(offset_mapping)):
                if not offset_mapping[i]:
                    offset_mapping[i] = None
            # print (arr)
            for start_index in start_indexes:
                for end_index in end_indexes:
                    # Don't consider out-of-scope answers, either because the indices are out of bounds or correspond
                    # to part of the input_ids that are not in the context.
                    if (
                            start_index >= len(offset_mapping)
                            or end_index >= len(offset_mapping)
                            or offset_mapping[start_index] is None
                            or offset_mapping[end_index] is None
                    ):
                        continue
                    # Don't consider answers with a length that is either < 0 or > max_answer_length.
                    if end_index < start_index or end_index - start_index + 1 > max_answer_length:
                        continue

                    start_char = offset_mapping[start_index][0]
                    end_char = offset_mapping[end_index][1]
                    valid_answers.append(
                        {
                            "score": start_logits[start_index] + end_logits[end_index],
                            "text": context[start_char: end_char]
                        }
                    )

        if len(valid_answers) > 0:
            best_answer = sorted(valid_answers, key=lambda x: x["score"], reverse=True)[0]
        else:
            # In the very rare edge case we have not a single non-null prediction, we create a fake prediction to avoid
            # failure.
            best_answer = {"text": "", "score": 0.0}

        # Let's pick our final answer: the best one or the null answer (only for squad_v2)
        if not squad_v2:
            predictions[example["id"]] = best_answer["text"]
        else:
            answer = best_answer["text"] if best_answer["score"] > min_null_score else ""
            predictions[example["id"]] = answer

    return predictions



def generateAnswerFromQAmodel(question, contextList, courseInfoId, lectureNo):
    data_collator = default_data_collator
    context = selectContext(question, contextList)
    single_input = format_user_input(context, question)
    single_test_features = single_input.map(prepare_single_test_features, batched=True,
                                            remove_columns=single_input.column_names)
    args = TrainingArguments(
        f"test-squad",
        per_device_eval_batch_size=1,
    )
    trainer = Trainer(
        qa_loaded_model,
        args,
        eval_dataset=single_test_features,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    raw_predictions = trainer.predict(single_test_features)
    single_test_features.set_format(type=single_test_features.format["type"],
                                    columns=list(single_test_features.features.keys()))
    final_predictions = postprocess_qa_predictions(single_input, single_test_features, raw_predictions.predictions)
    print(final_predictions['1'])
    session = Session()
    # save the question in the db for report generation
    stmt = (
        insert(QUESTION_ANSWERING).values(COURSE_INFO_ID=courseInfoId, QUESTION=question, ANSWER=final_predictions['1'], LECTURE = lectureNo,
                                    DATE=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    print(stmt)
    session.execute(stmt)
    session.commit()
    return final_predictions['1']
# def generateAnswerFromQAmodel(question, context):
#     data_collator = default_data_collator
#     # context = selectContext(question, contextList)
#     single_input = format_user_input(context, question)
#     single_test_features = single_input.map(prepare_single_test_features, batched=True,
#                                             remove_columns=single_input.column_names)
#     args = TrainingArguments(
#         f"test-squad",
#         per_device_eval_batch_size=1,
#     )
#     trainer = Trainer(
#         qa_loaded_model,
#         args,
#         eval_dataset=single_test_features,
#         data_collator=data_collator,
#         tokenizer=tokenizer,
#     )
#     raw_predictions = trainer.predict(single_test_features)
#     single_test_features.set_format(type=single_test_features.format["type"],
#                                     columns=list(single_test_features.features.keys()))
#     final_predictions = postprocess_qa_predictions(single_input, single_test_features, raw_predictions.predictions)
#     print(final_predictions['1'])
#     return final_predictions['1']
