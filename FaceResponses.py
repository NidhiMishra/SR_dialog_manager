__author__ = 'IMI-User'

FaceSentenceResponses={
    "Joy":{
        "beforeInteraction":[
                          "You look happy",
                          ],
        "duringInteraction":{
            "goodMood":["You look happy"],
            "badMood":["You look happy"]
        }
    },
    ###################################
    "Fear":{
        "beforeInteraction":[
                           "You look scared"],
        "duringInteraction":{
            "goodMood":[
                           "You look scared"],
            "badMood":[
                            "You look scared"]
        }
    },
    ####################################
    "Disgust":{
        "beforeInteraction":[],
        "duringInteraction":{
            "goodMood":[],
            "badMood":[]
        }
    },

    ####################################
    "Sadness":{
        "beforeInteraction":[
            "You look sad"],
        "duringInteraction":{
            "goodMood":[
                "You look sad"],
            "badMood":[
                "You look sad"
            ]
        }
    },

    ####################################
    "Anger":{
        "beforeInteraction":[
            "You look angry"],
        "duringInteraction":{
            "goodMood":[
                "You look angry"
            ],
            "badMood":[
               "You look angry"]
        }
    },

    ####################################
    "Surprise":{
        "beforeInteraction":[
        ],
        "duringInteraction":{
            "goodMood":[

            ],
            "badMood":[

            ]
        }
    },

    ####################################
    "Contempt":{
        "beforeInteraction":[],
        "duringInteraction":{
            "goodMood":[],
            "badMood":[]
        }
    }
}


FaceEmotionResponse={
    "Joy":{
        "goodMood":"JOY",
        "badMood":"ANGER"
    },
    ###################################
    "Fear":{
        "goodMood":"PITY",
        "badMood":"PITY"
    },
    ####################################
    "Disgust":{
        "goodMood":"SHAME",
        "badMood":"ANGER"
    },

    ####################################
    "Sadness":{
        "goodMood":"PITY",
        "badMood":"PITY"
    },

    ####################################
    "Anger":{
        "goodMood":"SHAME",
        "badMood":"ANGER"
    },

    ####################################
    "Surprise":{
        "goodMood":"",
        "badMood":""
    },

    ####################################
    "Contempt":{
        "goodMood":"SHAME",
        "badMood":"ANGER"
    }
}