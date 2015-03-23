'''
Created on 23.03.2015

@author: Salaxy
'''
import sys

from naoqi import ALProxy


class Speech():
    
    WORD_LIST = 
    VISUAL_EXPRESSION =
    ENABLE_WORD_SPOTTING = 
    
    "Confidence threshold (%)"
    CONFIDENCE_THRESHOLD = 30
    
    
    def __init__(self, IP, PORT):
        try:
            self.asr = ALProxy("ALSpeechRecognition", IP, PORT)
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
        '''self.BIND_PYTHON(self.getName(), "onWordRecognized")'''

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
                self.asr.setVisualExpression(VISUAL_EXPRESSION)
                self.asr.pushContexts()
            self.hasPushed = True
            if self.asr:
                self.asr.setVocabulary(WORD_LIST.split(';'), ENABLE_WORD_SPOTTING)
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
        if(len(value) > 1 and value[1] >= CONFIDENCE_THRESHOLD / 100.):
            self.wordRecognized(value[0])  # ~ activate output of the box
        else:
            self.onNothing()


if __name__ == '__main__':
    
    # Replace here with your NaoQi's IP address.
    #IP = "nao.local"  
    IP = "172.17.16.29"
    PORT = 9559
    
    # Read IP address from first argument if any.
    if len(sys.argv) > 1:
        IP = sys.argv[1]
        
    s = Speech(IP, PORT)