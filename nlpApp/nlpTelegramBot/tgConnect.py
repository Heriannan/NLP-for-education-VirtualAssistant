import json
import logging
import random
from pprint import pprint
import time
import telepot
import torch
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from transformers import AutoModel, RobertaTokenizer, RobertaModel
from nlpApp.nlpTelegramBot.commonFunction import getCourse, classify_courseInfo, generateCourseInfoResponse, \
    searchCourse, classify_comment, validateLecture, searchLecture, searchContext, validateContext, \
    generateAnswerFromQAmodel
# sa_model_dir, in_model_dir
from nlpProject.settings import telegram_bot_token

logger = logging.getLogger(__name__)

model_checkpoint = "roberta-base"


class BERTClass(torch.nn.Module):
    # subclassing nn.Module
    # initialize neural layer in _init_
    def __init__(self):
        super(BERTClass, self).__init__()  # mandatory
        self.l1 = AutoModel.from_pretrained(sa_loaded_model, num_labels=5)
        # self.l1 = AutoModel.from_pretrained(loaded_model, num_labels=5)
        self.pre_classifier = torch.nn.Linear(768, 768)  # 768 class?
        self.dropout = torch.nn.Dropout(0.3)  # drop 30% neurons
        self.classifier = torch.nn.Linear(768,
                                          5)  # 768:bert config hidden size, 11:classes (input features & output features)

    def forward(self, input_ids, attention_mask):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)  # pooled output
        # print(f"output 1:{output_1}")
        hidden_state = output_1[0]
        # print(f"output 1[0]:{output_1[0]}")
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        # print(pooler.shape)
        output = self.classifier(pooler)
        return output


class RobertaClass(torch.nn.Module):
    # subclassing nn.Module
    # initialize neural layer in _init_
    def __init__(self):
        super(RobertaClass, self).__init__()  # mandatory
        self.l1 = AutoModel.from_pretrained(in_loaded_model, num_labels=11)
        self.pre_classifier = torch.nn.Linear(768, 768)  # 768 class
        self.dropout = torch.nn.Dropout(0.3)  # drop 30% neurons
        self.classifier = torch.nn.Linear(768,
                                          11)  # 768:bert config hidden size, 11:classes (input features & output features)

    def forward(self, input_ids, attention_mask):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)  # pooled output
        print(f"output 1:{output_1}")
        hidden_state = output_1[0]
        print(f"output 1[0]:{output_1[0]}")
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


sa_model_dir = r'''C:\nlpProject\nlpApp\nlpModels\sentimentAnalysis\sa_model_roberta.bin'''
in_model_dir = r'''C:\nlpProject\nlpApp\nlpModels\infoClassification\pytorch_roberta.bin'''

sa_loaded_model = torch.load(sa_model_dir, map_location=torch.device('cpu'))
in_loaded_model = torch.load(in_model_dir, map_location=torch.device('cpu'))

courseInfoId = ''


def checkCourseCode(chat_id, msg):
    courseInfo = searchCourse(msg['text'])
    if courseInfo:
        bot.sendMessage(chat_id, text=f'There are {len(courseInfo)} result.')
        for info in courseInfo:
            bot.sendMessage(chat_id, text=info)
        bot.sendMessage(chat_id, text='Please input the ID of course you would like to enquire.')
        return 'get course selection'
    else:
        bot.sendMessage(chat_id,
                        text=f"Sorry, the {msg['text']} can not be found. Please try to enter other course code.")
        return 'get course code'


def checkCourseInfoId(chat_id, msg):
    print('checking course info id')
    course = getCourse(msg)
    if course != False:
        mark_up = ReplyKeyboardMarkup(keyboard=[
            ['Ask course information'],
            ['Ask course related knowledge'],
            ['Do quizzes'],
            ['Leave a comment']
        ])
        bot.sendMessage(chat_id, text='What do you want to do?', reply_markup=mark_up)
        return 'get function'
    else:
        bot.sendMessage(chat_id,
                        text=f"Sorry, the {msg['text']} can not be found. Please enter a correct ID.")
        return 'get course selection'


def identify_function(msg):
    if msg == 'Ask course information':
        return 'What do you want to know?', 'Ask course information'
    elif msg == 'Ask course related knowledge':
        return '', 'Ask course related knowledge'
    elif msg == 'Do quizzes':
        return '', 'Do quizzes'
    elif msg == 'Leave a comment':
        return 'What do you think about this course? Please leave your comment here.', 'Leave a comment'


class ChatbotNLP(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatbotNLP, self).__init__(*args, **kwargs)
        self.indicator = 'null'
        self.status = 0
        self.courseInfoId = ""
        self.questionList = ""
        self.questionIdList = ""
        self.question = ""
        self.questionAnswer = ""
        self.contextList = ""
        self.lecture = ""

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # if self.indicator == 'null':
        if msg['text'] == '/start':
            # classify_comment(msg['text'])
            bot.sendMessage(chat_id, "Please enter the enquired course's code.(e.g.cs1102)")
            self.indicator = 'get course code'

        elif msg['text'] == '/maintain':
            bot.sendMessage(chat_id, 'Please login to add or edit course information. http://127.0.0.1:8000/nlpApp/')
            self.indicator = 'null'
        else:
            if self.indicator == 'get course code':
                self.indicator = checkCourseCode(chat_id, msg)

            elif self.indicator == 'get course selection':
                self.courseInfoId = msg['text']
                print(msg['text'])
                self.indicator = checkCourseInfoId(chat_id, msg['text'])

            elif self.indicator == 'get function':
                text, self.indicator = identify_function(msg['text'])
                if self.indicator == 'Do quizzes':
                    lecture_result = searchLecture(self.courseInfoId)
                    if lecture_result != False:
                        bot.sendMessage(chat_id, text=lecture_result)
                        self.indicator = 'get quizzes'
                        return
                    else:
                        bot.sendMessage(chat_id,
                                        text=f"Sorry,this course do not have any quiz yet. Please enter another course's code to perform further action.(e.g.cs1102)")
                        self.indicator = 'get course code'

                elif self.indicator == 'Ask course related knowledge':
                    context_result = searchContext(self.courseInfoId)
                    if context_result != False:
                        bot.sendMessage(chat_id, text=context_result)
                        self.indicator = 'get question'
                        return
                    else:
                        bot.sendMessage(chat_id,
                                        text=f"Sorry,this course do not support question answering yet. Please enter another course's code to perform further action.(e.g.cs1102)")
                        self.indicator = 'get course code'
                else:
                    bot.sendMessage(chat_id, text=text)
                    return

            elif self.indicator == 'Ask course information':
                print(f'info:{self.courseInfoId}')
                label = classify_courseInfo(msg['text'], in_loaded_model)
                response = generateCourseInfoResponse(self.courseInfoId, label, msg['text'])
                bot.sendMessage(chat_id, text=response)
                self.indicator = 'Ask course information'
                return

            elif self.indicator == 'get question':
                self.contextList = validateContext(msg['text'])
                if self.contextList != False or self.contextList != "":
                    self.lecture = msg['text']
                    bot.sendMessage(chat_id, text='What concepts or ideas do you want to clarify?')
                    self.indicator = 'question answering'
                    return
                else:
                    bot.sendMessage(chat_id,
                                    text=f"Sorry, lecture {msg['text']} can not be found. Please enter a correct lecture number from the above result.")

            elif self.indicator == 'question answering':
                qaAnswer = generateAnswerFromQAmodel(msg['text'],self.contextList, self.courseInfoId, self.lecture )
                bot.sendMessage(chat_id, text=qaAnswer)

            elif self.indicator == 'get quizzes':
                self.questionList, self.questionIdList = validateLecture(msg['text'])
                if self.questionList != False or self.questionList != False:
                    # send question
                    questionId = random.choice(self.questionIdList)
                    self.question = self.questionList[questionId][0]
                    self.questionAnswer = self.questionList[questionId][1]
                    self.questionIdList.remove(questionId)
                    bot.sendMessage(chat_id, text='Quiz Start')
                    bot.sendMessage(chat_id, text=f'Question: {self.question}')
                    self.indicator = 'doing quizzes'
                    return
                else:
                    bot.sendMessage(chat_id,
                                    text=f"Sorry, question of lecture {msg['text']} can not be found. Please enter a correct lecture number from the above result.")


            elif self.indicator == 'doing quizzes':
                if len(self.questionIdList) > 0:
                    bot.sendMessage(chat_id, text=f'Answer: {self.questionAnswer}')
                    questionId = random.choice(self.questionIdList)
                    self.question = self.questionList[questionId][0]
                    self.questionAnswer = self.questionList[questionId][1]
                    self.questionIdList.remove(questionId)
                    bot.sendMessage(chat_id, text=self.question)
                else:
                    bot.sendMessage(chat_id, text=self.QuestionAnswer)
                    bot.sendMessage(chat_id, text="This is the end of the quiz.")

            elif self.indicator == 'Leave a comment':
                label = classify_comment(msg['text'], self.courseInfoId, sa_loaded_model)
                if label == 'Have room of improvements':
                    bot.sendMessage(chat_id, text=f'You think the course have room of improvements.')
                else:
                    bot.sendMessage(chat_id, text=f'You think the course is {label}')
                bot.sendMessage(chat_id, text='Thank you for your comment!')
                self.indicator = 'Leave a comment'


# def on_callback_query(msg):
#     query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
#     bot.answerCallbackQuery(query_id, text='Sold out!')
#     bot.answerCallbackQuery(query_id, text='You have ordered'+query_data)

TOKEN = telegram_bot_token

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(per_chat_id(), create_open, ChatbotNLP, timeout=3600),
])

# MessageLoop(bot, {'chat': ChatbotNLP,
#                   'callback_query': on_callback_query}).run_as_thread()
test1 = MessageLoop(bot).run_as_thread()
print(f'test1: {test1}')

while 1:
    time.sleep(10)
