from framelen import AudioDuration


while True:
    Audio_prop = AudioDuration("answer.mp3")
    Audio_Dur = Audio_prop.len()
    print("In Other Lang:", str(Audio_Dur))
    Audio_prop = AudioDuration("G:\\IMI-PROJECTS\\i2p_Nadine_Robot\\development\\i2p_interaction\\i2p_nadine_control\\build\\lipAnim.wav")
    Audio_Dur = Audio_prop.len()
    print("In English:", str(Audio_Dur))
    c = raw_input("To continue?")
    if c == "y":
        print("Next iteration")
    else:
        break
