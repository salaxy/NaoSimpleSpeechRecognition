#!/usr/bin/env python
'''
Created on 23.03.2015

 modified class from nao choregraphe

@author: Andy Klay
'''
import copy
import sys
import time

from naoqi import ALProxy, ALModule, ALBroker


class SpeechTestClass(ALModule):
    
    WORD_LIST = "yes;no;okay"
    VISUAL_EXPRESSION = True
    ENABLE_WORD_SPOTTING = True
    "Confidence threshold (%)"
    CONFIDENCE_THRESHOLD = 10
    
    lastWords = None
    
    
    def __init__(self, IP, PORT):
        ALModule.__init__(self, "SpeechTestClass")
        try:
            self.asr = ALProxy("ALSpeechRecognition")
            self.asr.setLanguage("English")
        except Exception as e:
            self.asr = None
            self.logger.error(e)
        self.memory = ALProxy("ALMemory")


    '''erste methode! nachm start'''
    def onLoad(self):
        from threading import Lock
        self.bIsRunning = False
        self.mutex = Lock()
        self.hasPushed = False
        self.hasSubscribed = False
        self.BIND_PYTHON(self.getName(), "onWordRecognized")
        
        self.isWordSaid = False

    '''  dannach wenn alles fertig ist'''
    def onUnload(self):
        from threading import Lock
        self.mutex.acquire()
        try:
            if (self.bIsRunning):
                if (self.hasSubscribed):
                    self.memory.unsubscribeToEvent("WordRecognized", "SpeechTestClass")
                if (self.hasPushed and self.asr):
                    self.asr.pause(True)
                    self.asr.popContexts()
        except RuntimeError, e:
            self.mutex.release()
            raise e
        self.bIsRunning = False;
        self.mutex.release()

    ''' aufrufen wenn aktiv sein soll '''
    def onInput_onStart(self):
        from threading import Lock
        self.mutex.acquire()
        self.asr.pause(True)
        if(self.bIsRunning):
            self.mutex.release()
            return
        self.bIsRunning = True
        try:
            if self.asr:
                self.asr.setVisualExpression(self.VISUAL_EXPRESSION)

                self.asr.pushContexts()
                
            self.hasPushed = True
            if self.asr:
                self.asr.setVocabulary(self.WORD_LIST.split(';'), self.ENABLE_WORD_SPOTTING)
            self.memory.subscribeToEvent("WordRecognized", "SpeechTestClass", "onWordRecognized")
            self.hasSubscribed = True
        except RuntimeError, e:
            self.mutex.release()
            self.onUnload()
            raise e
        self.mutex.release()
        self.asr.pause(False)

    def onInput_onStop(self):
        if(self.bIsRunning):
            self.onUnload()
            #self.onStopped()

    ''' methode die aufgerufen wird wenn was kommt '''
    def onWordRecognized(self, key, value, message):
        
        if(len(value) > 1 and value[1] >= self.CONFIDENCE_THRESHOLD / 100.):
            self.wordRecognized(value[0])  # ~ activate output of the box
            self.lastWords = copy(value)
        else:
            self.onNothing()

    def onNothing(self):
        print "nothing recognized"
        
    def wordRecognized(self, wordRecognized):
        self.isWordSaid = True
        print wordRecognized
        
    def getWords(self):
        return self.lastWords
        
    def isSearchedWordSaid(self):
        return self.isWordSaid

if __name__ == '__main__':
    
    # Replace here with your NaoQi's IP address.
    #IP = "nao.local"  
    IP = "172.17.16.29"
    PORT = 9559
    
    # Read IP address from first argument if any.
    if len(sys.argv) > 1:
        IP = sys.argv[1]
        
        
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       IP,          # parent broker IP
       PORT)        # parent broker port


    #global SpeechTestClass
        
    tts = ALProxy("ALTextToSpeech")
    tts.say("test")
    time.sleep(2.0)    
    SpeechTestClass = SpeechTestClass(IP, PORT)
    SpeechTestClass.onLoad()
    SpeechTestClass.onInput_onStart()
    time.sleep(10.0)
    tts.say("OK")
    print str(SpeechTestClass.isSearchedWordSaid()) + " before stopped"
    SpeechTestClass.onInput_onStop()
    print str(SpeechTestClass.isSearchedWordSaid())
    
    print "i got all these words: "
    list = SpeechTestClass.getWords()
    for p in list:
        print p

    
    
    