'''
Created on 23.03.2015

 modified class from nao choregraphe

@author: Andy Klay
'''
import sys
import time

from naoqi import ALProxy


class Speech():
    
    WORD_LIST = "yes;no;okay"
    VISUAL_EXPRESSION = True
    ENABLE_WORD_SPOTTING = False
    "Confidence threshold (%)"
    CONFIDENCE_THRESHOLD = 30
    
    
    def __init__(self, IP, PORT):
        try:
            self.asr = ALProxy("ALSpeechRecognition", IP, PORT)
            self.asr.setLanguage("English")
        except Exception as e:
            self.asr = None
            self.logger.error(e)
        self.memory = ALProxy("ALMemory", IP, PORT)


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
                    self.memory.unsubscribeToEvent("WordRecognized", self.getName())
                if (self.hasPushed and self.asr):
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
            self.memory.subscribeToEvent("WordRecognized", self.getName(), "onWordRecognized")
            self.hasSubscribed = True
        except RuntimeError, e:
            self.mutex.release()
            self.onUnload()
            raise e
        self.mutex.release()

    def onInput_onStop(self):
        if(self.bIsRunning):
            self.onUnload()
            '''self.onStopped()'''

    ''' methode die aufgerufen wird wenn was kommt '''
    def onWordRecognized(self, key, value, message):
        if(len(value) > 1 and value[1] >= self.CONFIDENCE_THRESHOLD / 100.):
            self.wordRecognized(value[0])  # ~ activate output of the box
        else:
            self.onNothing()

    def onNothing(self):
        print "nothing recognized"
        
    def wordRecognized(self, wordRecognized):
        self.isWordSaid = True
        print wordRecognized

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
        
        
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    tts.say("test")
    time.sleep(2.0)    
    s = Speech(IP, PORT)
    s.onLoad()
    s.onInput_onStart()
    time.sleep(15.0)
    tts.say("okay")
    s.onInput_onStop()
    print str(s.isSearchedWordSaid())
    