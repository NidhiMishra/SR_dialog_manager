from chatterbot import ChatBot

#if training for the first time uncomment this part
#"""
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
#"""


# Train based on Nadine corpus 1,2 and 3
chatbot.train("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\AIA_database\\Nadine_1.yml")
chatbot.train("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\AIA_database\\Nadine_2.yml")
chatbot.train("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\AIA_database\\Nadine_3.yml")
chatbot.train("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_dialog_manager\\AIA_database\\Nadine_personal.yml")