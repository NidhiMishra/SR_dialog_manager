from chatterbot import ChatBot

#if training for the first time uncomment this part
"""
chatbot = ChatBot(
    'AIA bot',
    logic_adapters = [
					{
			            'import_path': 'chatterbot.logic.BestMatch',
			            "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
			        },
			        # {
			        #     'import_path': 'chatterbot.logic.TimeLogicAdapter'
			        # },
			        {
			            'import_path': 'chatterbot.logic.MathematicalEvaluation'
			        },
			        {
			            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
			            'threshold': 0.90,
			            'default_response': 'I am sorry, but I do not understand.'
			        }
    ],
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)
"""

#if trained already uncomment this part
#"""
chatbot = ChatBot(
    'Nadia bot',
    #read_only = True,
    logic_adapters = [
					{
			            'import_path': 'chatterbot.logic.BestMatch',
			            "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
			        },
			        # {
			        #     'import_path': 'chatterbot.logic.TimeLogicAdapter'
			        # },
			        {
			            'import_path': 'chatterbot.logic.MathematicalEvaluation'
			        },
			        {
			            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
			            'threshold': 0.60,
			            'default_response': 'I am sorry, but I do not understand.'
			        }
    ],
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)
#"""


# Train based on Nadia
chatbot.train("G:\IMI-PROJECTS\i2p_Nadine_Robot\development\i2p_interaction\i2p_dialog_manager\chatterbotMemory\Nadia.yml")

#AIA_log = open("AIA_UAT_log.txt","a")
while(True) :
	Question = raw_input('Enter your question: ')
	# Get a response to an input statement
	chatterbot = chatbot.get_response(Question)
	chatterbot = str(chatterbot)
	print "Chatbot response: ", chatterbot

	# if AIAChatbot_response in open('AIA_Valid_Answers.txt').read():
	#     print "Valid AIA answer: \n"
	#     # print(AIAChatbot_response)
	# else :
	#     print "Invalid AIA answer: \n"
	#     AIA_log.write("Question:" + Question + "\n")
	#     AIA_log.write("Invalid AIA answer\n")
	#     AIA_log.write(str(AIAChatbot_response) + "\n")
	

#AIA_log.close()