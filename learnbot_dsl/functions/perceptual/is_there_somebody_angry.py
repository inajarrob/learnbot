from __future__ import print_function


def is_there_somebody_angry(lbot, params=None, verbose=False):
    emotions = lbot.getEmotions()
    print(emotions)
    for e in emotions:
        if e.emotion =="Angry":
            return True
    return False