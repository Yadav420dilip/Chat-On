from tkinter import *
import pygame


def getmixerargs():
    pygame.mixer.init()
    freq, size, chan = pygame.mixer.get_init()
    return freq, size, chan


def initMixer():
    BUFFER = 3072  # audio buffer size, number of samples since pygame 1.8.
    FREQ, SIZE, CHAN = getmixerargs()
    pygame.mixer.init(FREQ, SIZE, CHAN, BUFFER)


def playsound(soundfile):
    """Play sound through default mixer channel in blocking manner.
       This will load the whole sound into memory before playback
    """
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(soundfile)
    clock = pygame.time.Clock()
    sound.play()
    while pygame.mixer.get_busy():
        clock.tick(1000)


def playmusic(soundfile):
    """Stream music with mixer.music module in blocking manner.
       This will stream the sound from disk while playing.
    """
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    pygame.mixer.music.load(soundfile)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(1000)


def stopmusic():
    """stop currently playing music"""
    pygame.mixer.music.stop()

# HOW TO PLAY SONG:


initMixer()

# playmusic(filename)


def FilteredMessage(EntryText):
    """
    Filter out all useless white lines at the end of a string,
    returns a new, beautifully filtered string.
    """
    EndFiltered = ''
    for i in range(len(EntryText) - 1, -1, -1):
        if EntryText[i] != '\n':
            EndFiltered = EntryText[0:i + 1]
            break
    for i in range(0, len(EndFiltered), 1):
        if EndFiltered[i] != "\n":
            return EndFiltered[i:] + '\n'
    return ''


def LoadMyEntry(EntryText, ChatLog):
    if EntryText != '':
        ChatLog.config(state=NORMAL)
        if ChatLog.index('end') is not None:
            LineNumber = float(ChatLog.index('end'))-1
            ChatLog.insert(END, EntryText)
            ChatLog.tag_add("You", LineNumber, LineNumber + 1)
            ChatLog.tag_config("You", foreground="#FF8000", font=("Elephant", 12, "bold"), justify="right")
            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)


def LoadOtherEntry(ChatLog, EntryText):
    if EntryText != '':
        ChatLog.config(state=NORMAL)
        if ChatLog.index('end') is not None:
            try:
                LineNumber = float(ChatLog.index('end'))-1
            except Exception as e:
                print(e)
                pass
            ChatLog.insert(END, EntryText)
            ChatLog.tag_add("Other", LineNumber, LineNumber+1)
            ChatLog.tag_config("Other", foreground="#04B404", font=("Elephant", 12, "bold"))
            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)
