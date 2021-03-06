# NLP-for-education-VirtualAssistant
Steps to set up the environment  
1. Create your pycharm project and add an app. (https://www.jetbrains.com/help/pycharm/creating-django-application-in-a-project.html)  
2. Clone this repository, then copy the files to your project.  
3. Set up a database according to the structure of "nlpApp/classModel/Models.py", then connect it to your project.  
4. Add a folder "nlpApp/nlpModels" and create three sub folders to place your models. ("nlpApp/nlpModels/infoClassification", "nlpApp/nlpModels/questionAnswering", "nlpApp/nlpModels/sentimentAnalysis")  
5. Create a telegram bot, place your token in "nlpProject/settings.py" {telegram_bot_token = 'your token'}.  

## Model Training
Info Enquiry:  
distilbert:https://colab.research.google.com/drive/1sRrPzsTAYe-Wt_1AYKSb56elngBZq8Ij  
roberta:https://colab.research.google.com/drive/17gCC3jgr8jn3SttDI99i0mxLc34oWMrE  
bert base uncased:https://colab.research.google.com/drive/1ztsPA9pg1YwfmaJu36rMbL1e24Odac5i  
  
Question Answering:  
distilbert:https://colab.research.google.com/drive/17EIBv7oiHQQX1U0ZilJ5uxlfBPhXPbVT  
roberta:https://colab.research.google.com/drive/1Ah890PbAPI7sqxHJ7UOuh9a5_VwoRRvv  
bert base uncased:https://colab.research.google.com/drive/18nO_y4QQ_pPjN3z8gkRm0-sGKzXsRCPp  
  
Sentiment Analysis:  
distilbert:https://colab.research.google.com/drive/1a143XsZgttuaMVxA12mMDWLdERj5-k4G  
roberta: https://colab.research.google.com/drive/1PVUU8K4CJMHPXAe2Ms3QUH6xCyLKZ3Ra#scrollTo=JrBr2YesGdO_  
bert base uncased: https://colab.research.google.com/drive/1YvWN8gI1KpUDEpPM-iB8e4lMuSerB51g#scrollTo=UNiPzsfz_oHN  
  
**The above model training scripts references on the below authors.**  
1. Datawhalechina. (2021, August 14). Learn-NLP-with-transformers/4.3-问答任务-抽取式问答.ipynb at main · datawhalechina/learn-NLP-with-transformers. GitHub. Retrieved April 12, 2022, from https://github.com/datawhalechina/learn-nlp-with-transformers/blob/main/docs/%E7%AF%87%E7%AB%A04-%E4%BD%BF%E7%94%A8Transformers%E8%A7%A3%E5%86%B3NLP%E4%BB%BB%E5%8A%A1/4.3-%E9%97%AE%E7%AD%94%E4%BB%BB%E5%8A%A1-%E6%8A%BD%E5%8F%96%E5%BC%8F%E9%97%AE%E7%AD%94.ipynb  
2. abhimishra91. (n.d.). Transformers-tutorials/transformers_multiclass_classification.ipynb at master · abhimishra91/transformers-tutorials. GitHub. Retrieved April 12, 2022, from https://github.com/abhimishra91/transformers-tutorials/blob/master/transformers_multiclass_classification.ipynb   

## Training Data
The sentiment analysis dataset is a modified version of 100K Coursera's Course Reviews Dataset. (https://www.kaggle.com/datasets/septa97/100k-courseras-course-reviews-dataset/code)
