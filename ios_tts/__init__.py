from pyobjus import autoclass, protocol
from pyobjus.dylib_manager import load_framework, INCLUDE
load_framework(INCLUDE.AVFoundation)
load_framework('/System/Library/Frameworks/AppKit.framework')
load_framework('/System/Library/Frameworks/Foundation.framework')
from pyttsx3.voice import Voice
NSTimer = autoclass('NSTimer')
NSString = autoclass('NSString')
NSArray = autoclass('NSArray')
NSObject = autoclass('NSObject')
AVSpeechSynthesizer = autoclass('AVSpeechSynthesizer')
AVSpeechUtterance = autoclass('AVSpeechUtterance')
AVSpeechSynthesisVoice = autoclass('AVSpeechSynthesisVoice')
NSURL = autoclass('NSURL')

from text2sentences import text_to_sentences

def buildDriver(proxy, **kw):
    # return NSSpeechDriver.alloc().initWithProxy(proxy)
    return SpeechDriver(proxy, **kw)

class SpeechDriver:
    def __init__(self, proxy, **kw):
		self._proxy = proxy
		self._tts = AVSpeechSynthesizer.alloc().init()
		self._tts.setDelegate_(self)
		self._completed = True
		self.rate = 180
		self.set_stop_period()
		self.voice = None

	def set_stop_period(self):
		r = 1.0 / float(self.rate)
		self.semi_stop_period = 1.5 * r
		self.sentence_stop_period = 3.0 * r

	def pause(self):
		self._tts.pauseSpeakingAtBoundary()

	def contineu(self):
		self._tts.continueSpeaking()

	def stop(self):
        if self._proxy.isBusy():
            self._completed = False
		self._tts.stopSpeakingAtBoundary()

	def say(self, text):
        self._proxy.setBusy(True)
        self._completed = True
		self.sentences += text_to_sentences(text)

	def set_utterences_by_sentence(self, utterence, sentence):
		if sentence.dialog:
			utterence.pitchModifier = 1.25

	def speak_sentence(self, sentence):
		utterance = AVSpeechUtterance.alloc().initWithString(sentence.text)
		self.set_utterences_by_sentence(utterence, sentence)
		self._tts.speakUtterance(utterance)

    def destroy(self):
        self._tts.setDelegate_(None)
        del self._tts

    def startLoop(self):
        self._proxy.notify('started-utterance')
		speak_next_sentence()

	def speak_next_sentence(self):
		if len(self.sentences) > 0:
			self.speaking_sentence = self.sentences.pop(0)
			self.speak_sentence(self.speaking_sentence)
		else:
			sself.speaking_sentence = None
			self._proxy.notify('finished-utterance', completed=success)
			

    def endLoop(self):
		self.speaking_sentence = None

    def iterate(self):
        self._proxy.setBusy(False)
        yield

    def _toVoice(self, attr):
        try:
            lang = attr['VoiceLocaleIdentifier']
        except KeyError:
            lang = attr['VoiceLanguage']
        return Voice(attr['VoiceIdentifier'], attr['VoiceName'],
                     [lang], attr['VoiceGender'],
                     attr['VoiceAge'])

    def getProperty(self, name):
        if name == 'voices':
            return self.get_all_language()
        elif name == 'voice':
            return self.voice
        elif name == 'rate':
            return None
        elif name == 'volume':
            return None
        elif name == "pitch":
            print("Pitch adjustment not supported when using NSSS")
        else:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
		return
        if name == 'voice':
            # vol/rate gets reset, so store and restore it
			self.voice = value
        elif name == 'rate':
            self._tts.setRate_(value)
        elif name == 'volume':
            self._tts.setVolume_(value)
        elif name == 'pitch':
            print("Pitch adjustment not supported when using NSSS")
        else:
            raise KeyError('unknown property %s' % name)

	def get_all_language(self):
		langs = AVSpeechSynthesisVoice.speechVoices()
		return langs

    def save_to_file(self, text, filename):
        url = NSURL.fileURLWithPath_(filename)
        self._tts.startSpeakingString_toURL_(text, url)

	@protocol('AVSpeechSynthesisDelegate')
    def speechSynthesizer_didCancelSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
    def speechSynthesizer_didContinueSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
    def speechSynthesizer_didPauseSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
    def speechSynthesizer_didStartSpeechUtterance_(self, *args):
		print('args=', args)
		return

	@protocol('AVSpeechSynthesisDelegate')
    def speechSynthesizer_didFinishSpeechUtterance_(self, *args):
		print('args=', args)
		self.speak_next_utterence()
		return
        if not self._completed:
            success = False
        else:
            success = True
        self._proxy.setBusy(False)

	@protocol('AVSpeechSynthesisDelegate')
	def speechSynthesizer_willSpeakRangeOfSpeechString_(self, *args):
		print('args=', args)

