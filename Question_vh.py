# This file defines the questions about IMI
import sys
sys.path.append("gen-py")
import Control.ttypes

##Question={"What's the full name of IMI": "The full name of IMI is Institute of Media Inovation",
##          "How many phd students are there in IMI":"There are more than 50 students who come from different schools study in IMI",
##          "How many professors are there in IMI": "More than 20 professors take part in the projects in IMI",
##          "Do you know James": "Yes, he is a phd student here whose topic is emotional interaction",
##          "Do you know professor Zheng": "Yes, he focuses on computer graphics",
##          "How often is the phd seminar": "At least once in a month",
##          "What is the being there project": "It is a five year project of IMI about 3D telepresence",
##          "Do researchers in IMI work on virtual human": "Yes, not only virtual human, but also social robot"   
##    }

PositiveComment=["I like you so much",
                 "You look pretty today",
                 "You are so nice",
                 "Your voice sounds charming",
                 "You are so interesting",
                 "You are my best friend"]
NegativeComment=["I don't like you",
                 "You look ugly today",
                 "You are so mean",
                 "Your voice sounds sleepy",
                 "You are so boring",
                 "I don't like to talk with you"]

def speechTone(_str,moodLevel):
    if moodLevel in ["Very Angry","Crazy Angry"]:
        res="<voice emotion='cross'>"+_str+"</voice>"
        return res
    elif moodLevel in ["Very Happy","Crazy Happy"]:
        res="<voice emotion='happy'>"+_str+"</voice>"
        return res
    elif moodLevel in ["Slight Angry","Mild Angry"]:
        res="<voice emotion='calm'>"+_str+"</voice>"
        return res
    else:
        return _str

def appraiseEmotion(_str):
    if _str in PositiveComment:
        return "GRATITUDE 0.5"
    elif _str in NegativeComment:
        return "ANGER 0.5"
    return None

# after user makes positive comment
PositiveResponse={"Slight Angry":["It sounds good.",
                                 "<spurt audio=\"g0001_013\">cough cough</spurt> I feel much better.",
                                  "<spurt audio=\"g0001_014\">cough cough</spurt>You are right."],
                  "Mild Angry":["Really? You think so?",
                                 "It sounds better.",
                                "<spurt audio=\"g0001_010\">cough cough</spurt> Ok."],
                  "Very Angry":["<spurt audio=\"g0001_050\">cough cough</spurt> stop kidding me",
                                "Are you satirizing me?",
                                "bla bla, you talk too much"],
                  "Crazy Angry":["<voice emotion='cross'>Let us have no more of this, I do not believe you!</voice>",
                                 "<voice emotion='cross'>I cannot say the same for you</voice>",
                                 "<voice emotion='cross'> you are not.</voice>"],
                  "Slight Happy":["<voice emotion='happy'>Oh, thank you.</voice>",
                                  "<voice emotion='happy'>Really? Thank you</voice>"],
                  "Mild Happy":["<voice emotion='happy'>You are so nice, my friend!</voice>",
                                "<voice emotion='happy'>So nice you are!</voice>",
                                "<voice emotion='happy'>You are so kind.</voice>"],
                  "Very Happy":["<voice emotion='happy'>I am happy, I am enjoying our conversation so much! <spurt audio=\"g0001_010\">cough cough</spurt></voice>",
                                "<voice emotion='happy'><spurt audio=\"g0001_037\">cough cough</spurt>It is my great pleasure to hear that. It makes me feel good.</voice>",
                                "<voice emotion='happy'><spurt audio=\"g0001_028\">cough cough</spurt>You are really kind. I really like you.</voice>"],
                  "Crazy Happy":["<voice emotion='happy'><spurt audio=\"g0001_025\">cough cough</spurt>I am so so happy. You are such a kind person</voice>",
                                 "<voice emotion='happy'> I have never felt so happy before <spurt audio=\"g0001_010\">cough cough</spurt></voice>",
                                 "<voice emotion='happy'><spurt audio=\"g0001_025\">cough cough</spurt>You know what, I love you more than myself</voice>",]}
# after user makes negative comment
NegativeResponse={"Slight Angry":["<spurt audio=\"g0001_039\">cough cough</spurt> <voice emotion='calm'>I am sorry for that, I hope you can change your mind.</voice>",
                                  "<voice emotion='calm'> To be frankly, I can not agree with you.</voice>",
                                  "<spurt audio=\"g0001_050\">cough cough</spurt> <voice emotion='calm'> Ok, let us talk something else.</voice>"],
                  "Mild Angry":["<voice emotion='cross'>I am unhappy, why you say such bad words to me!</voice>",
                                "<voice emotion='cross'>What is wrong with you today.</voice>",
                                "<voice emotion='cross'>I am a little angry.</voice>"],
                  "Very Angry":["<voice emotion='cross'>I am sad, I hope we can stop this conversation! </voice>",
                                "<voice emotion='cross'>Stop here.</voice>",
                                "<voice emotion='cross'>Let us stop.</voice>"],
                  "Crazy Angry":["<voice emotion='cross'>How you dare to say so, get out of here!</voice>",
                                 "<voice emotion='cross'><spurt audio=\"g0001_038\">cough cough</spurt>go to hell!</voice>",
                                 "<voice emotion='cross'>Sorry, I have something else to do.</voice>"],
                  "Slight Happy":["<spurt audio=\"g0001_014\">cough cough</spurt> It sounds bad!",
                                  "<spurt audio=\"g0001_020\">cough cough</spurt> Stop to say that",
                                  "<spurt audio=\"g0001_026\">cough cough</spurt>Sorry?"],
                  "Mild Happy":["Really? You think so?",
                                "Do not fool me",
                                "Excuse me?"],
                  "Very Happy":["Do not say so, we are good friends!",
                                "Good friend does not say such word",
                                "Come on."],
                  "Crazy Happy":["<voice emotion='calm'>But I like you, my friend!</voice>",
                                 "<voice emotion='calm'>Whatever you say, we are good friend!</voice>",
                                 "<voice emotion='calm'>Come on please.</voice>"]}

# Positive Animation
PositiveAnimation={"Slight Angry":[Control.ttypes.Animation.ROCK],
                  "Mild Angry":[Control.ttypes.Animation.OFFER],
                  "Very Angry":[Control.ttypes.Animation.OFFER],
                  "Crazy Angry":[Control.ttypes.Animation.NOD_NO],
                  "Slight Happy":[Control.ttypes.Animation.RIGHT_SWEEP,
                                Control.ttypes.Animation.OFFER,
                                Control.ttypes.Animation.NOD_YES],
                  "Mild Happy":[Control.ttypes.Animation.RIGHT_SWEEP,
                                Control.ttypes.Animation.OFFER,
                                Control.ttypes.Animation.NOD_YES],
                  "Very Happy":[Control.ttypes.Animation.RIGHT_SWEEP,
                                Control.ttypes.Animation.OFFER,
                                Control.ttypes.Animation.NOD_YES],
                  "Crazy Happy":[Control.ttypes.Animation.RIGHT_SWEEP,
                                Control.ttypes.Animation.OFFER,
                                Control.ttypes.Animation.NOD_YES]}

# Negative Animation
NegativeAnimation={"Slight Angry":[Control.ttypes.Animation.ROCK,
                                   Control.ttypes.Animation.WHY,
                                   Control.ttypes.Animation.NOD_NO],
                  "Mild Angry":[Control.ttypes.Animation.ROCK],
                  "Very Angry":[Control.ttypes.Animation.WHY],
                  "Crazy Angry":[Control.ttypes.Animation.ROCK],
                  "Slight Happy":[Control.ttypes.Animation.ROCK],
                  "Mild Happy":[Control.ttypes.Animation.OFFER],
                  "Very Happy":[Control.ttypes.Animation.WHY],
                  "Crazy Happy":[Control.ttypes.Animation.ROCK]}

if __name__ == "__main__":
    print len(Question)
    print NegativeResponse["Crazy Happy"]["Excuse me, your accent is too strange"]
    
