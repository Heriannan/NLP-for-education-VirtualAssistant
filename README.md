# NLP-for-education-VirtualAssistant
Steps to set up the environment  
1.Create your pycharm project and add an app. (https://www.jetbrains.com/help/pycharm/creating-django-application-in-a-project.html)  
2.Clone this repository, then copy the files to your project.  
3.Set up a database according to the structure of "nlpApp/classModel/Models.py", then connect it to your project.  
4.Add a folder "nlpApp/nlpModels" and create three sub folders to place your models. ("nlpApp/nlpModels/infoClassification", "nlpApp/nlpModels/questionAnswering", "nlpApp/nlpModels/sentimentAnalysis")  
5.Create a telegram bot, place your token in "nlpProject/settings.py" {telegram_bot_token = 'your token'}.  
