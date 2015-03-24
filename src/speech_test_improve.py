# -*- encoding: UTF-8 -*-
""" Say `My {Body_part} is touched` when receiving a touch event
"""

import argparse
import copy
import sys
import time

from naoqi import ALBroker
from naoqi import ALModule
from naoqi import ALProxy


# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None

class ReactToTouch(ALModule):
    
    #WORD_LIST = "yes;no;okay"
    VISUAL_EXPRESSION = True
    ENABLE_WORD_SPOTTING = True
    "Confidence threshold (%)"
    CONFIDENCE_THRESHOLD = 5
    
    """ A simple module able to react
        to touch events. """
    def __init__(self, name, wordList):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy for later use
        self.asr = ALProxy("ALSpeechRecognition")
        self.asr.pause(True)
        self.asr.setVocabulary(wordList.split(';'), self.ENABLE_WORD_SPOTTING)
        self.asr.pause(False)
        self.lastWord = "none"
        self.isWordRecognized = False

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("WordRecognized",
            "ReactToTouch",
            "onWordRecognized")

        
    ''' methode die aufgerufen wird wenn was kommt '''
    def onWordRecognized(self, key, value, message):
        
        memory.unsubscribeToEvent("WordRecognized",
            "ReactToTouch")
        
        if(len(value) > 1 and value[1] >= self.CONFIDENCE_THRESHOLD / 100.):
            self.wordRecognized(value[0])  # ~ activate output of the box
            #self.lastWords = copy(value)
            self.lastWord = value [0]
            self.isWordRecognized = True   
        else:
            self.onNothing()
            
        memory.subscribeToEvent("WordRecognized",
            "ReactToTouch",
            "onWordRecognized")


    def onNothing(self):
        print "nothing recognized"
        
    def wordRecognized(self, wordRecognized):
        self.isWordSaid = True
        print "this is recoqnized " + wordRecognized
        
    def getLastWord(self):
        return self.lastWord
    
    #def isWordRecognized(self):
    #    return self.isWordRecognized
    #    


def waitUntilWordWasRecognized(ip, port, wordsToRecoqnize):
    """ Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       ip,          # parent broker IP
       port)        # parent broker port


    global ReactToTouch
    ReactToTouch = ReactToTouch("ReactToTouch", wordsToRecoqnize)
    
    isRecognized = False

    # wait until something is recognized
    while(not ReactToTouch.isWordRecognized): 
        time.sleep(5)
    
    print "this is said: " + ReactToTouch.getLastWord()
    
    lastWord = ReactToTouch.getLastWord()
    
    wordList = wordsToRecoqnize.split(';')
    
    for i in range(len(wordList)):
        if lastWord.find(wordList[i]):
            print wordList[i]
            isRecognized = True
         
    #if lastWord.find("is") == -1:
    #    print "its was yes"
    #else:
    #    print "its was no"

    #try:
    #    while True:
    #        time.sleep(1)
    #except KeyboardInterrupt:
    #    print ReactToTouch.getWords(ReactToTouch)
    #    print
    #    print "Interrupted by user, shutting down"
    #    myBroker.shutdown()
    #    sys.exit(0)
    
    return isRecognized

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.17.16.29",
                        help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559,
                        help="Robot port number")
    args = parser.parse_args()
    print "it was: " + str(waitUntilWordWasRecognized(args.ip, args.port, "yes;no;okay"))
