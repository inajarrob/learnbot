from learnbot_dsl.Clients.Devices import Emotions

def am_I_Sadness(lbot):
    if lbot.getCurrentEmotion() == Emotions.Sadness:
        return True
    return False
