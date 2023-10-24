# The NoteObj class is a mid-level representation of a score that helps with  manipulating 
# symbolic/MIDI music data in a more easier and more intuitive way

import music21
import dissonance as diss

SIXTEENTH = .25
EIGHTH = .5
QUARTER = 1
HALF = 2
DOTTED_EIGHTH = .75

class NoteObj:
    def __init__(self, onset, endTime, pitch, velocity, isRest=False, isTied=False):
        self.onset = onset
        self.endTime = endTime
        self.pitch = pitch
        self.velocity = velocity
        self.durationInSec = endTime - onset
        self.isRest = isRest
        self.isTied = isTied
    
    def print(self):
        print("Onset: ", "{:.2f}".format(self.onset), " End: ", "{:.2f}".format(self.endTime), " Pitch: ", self.pitch, " Vel: ", self.velocity)


def copy(note):
    n = NoteObj(note.onset, note.endTime, note.pitch, note.velocity, note.isRest, note.isTied)
    return n

def addOnset(note, newOnset):
    note.onset += newOnset
    note.endTime += newOnset

def removeRests(noteList):
    i = len(noteList) - 1
    while i >= 0:
        if noteList[i].isRest:
            noteList.pop(i)
        i -= 1      

def mergeTiedNotes(noteList):
    i = len(noteList) - 1
    while i > 0:
        currNote = noteList[i]
        if currNote.isTied:
            prevNote = noteList[i-1]
            # weak checking - assumes the immediately preceding event is the note tied over
            if prevNote.pitch == currNote.pitch:
                updateEndTime(prevNote, currNote.endTime)
                noteList.pop(i)
        i -= 1

def updateEndTime(note, newEndTime):
        note.endTime = newEndTime
        note.durationInSec = note.endTime - note.onset

def newNotebyDur(onset, dur, pitch, velocity, isRest=False, isTied=False):
    endTime = onset + dur
    return NoteObj(onset, endTime, pitch, velocity, isRest, isTied)
    
def returnNotes(offsetSeconds, element: music21.note.GeneralNote):
      if isinstance(element, music21.note.Note): 
            return [NoteObj(offsetSeconds, offsetSeconds+element.seconds, element.pitch.midi, element.volume.velocity)]
      elif isinstance(element, music21.chord.Chord):
            noteList = []
            chordPitches = element.pitches
            for note in chordPitches:
                noteList.append(NoteObj(offsetSeconds, offsetSeconds+element.seconds, note.midi, element.volume.velocity))
            return noteList

# Given a list of NoteObjs, return a list of only the pitches                 
def getListofPitches(noteList):
    pitches = []
    for n in noteList:
        pitches.append(n.pitch)
    return pitches

def getHighestPitch(noteList):
    currMax = -1
    for note in noteList:
          if note.pitch > currMax:
               currMax = note.pitch
    return currMax

def getHighestVelocity(noteList):
    currMax = -1
    i = 0
    for note in noteList:
        if note.velocity > currMax:
            currMax = note.velocity
            index = i

    return currMax, index

def getHighestNote(noteList):
    currMax = -1
    onset = -1
    pitch = -1
    endTime = -1
    velocity = -1
    for note in noteList:
        if note.pitch > currMax:
            onset = note.onset
            pitch = note.pitch
            endTime = note.endTime
            velocity = note.velocity
            currMax = note.pitch
               
    maxNote = NoteObj(onset, endTime, pitch, velocity)
    return maxNote

# Select the highest pitch available; takes into account overlapping note durations
def getMelodicLine(onsetsAll):
    # onsetsAll is a dict keyed by onset time; the items are a list of noteObjs
    minOnsetDiff = .01 # 10ms buffer between notes when judging when a note on and note off overlap
    prevPitch = -1
    prevOnset = -1
    prevEndTime = -1
    melodicLine = {}
    for key, notes in onsetsAll.items():
        currOnset = key
        noteList = notes
        currHighestforOnset = getHighestNote(noteList)
        currPitch = currHighestforOnset.pitch
        currEndTime = currHighestforOnset.endTime
        
        if prevEndTime - currOnset < minOnsetDiff or (prevEndTime > currOnset and currPitch > prevPitch):
            melodicLine[currOnset] = currPitch
            #print("Selected: ", currPitch)
            prevPitch = currPitch
            prevOnset = currOnset
            prevEndTime = currEndTime

    return melodicLine
             
          
# Estimate loudness from MIDI velocity values; for each onset, loudness is the velocity value of the
# loudness note plus all the velocities of the other notes in the chord scaled down. 
# Argument: onsetsAll is a dict keyed by onset time; the items are a list of noteObjs
def getLoudness(onsetsAll):
 
    SCALE_FACTOR = .1
    loudness = {}

    for key, notes in onsetsAll.items():
        currOnset = key
        noteList = notes
        totalVelocity = 0

        highestVelocity, index = getHighestVelocity(noteList)
        numNotes = len(noteList)

        for i in range(0, numNotes):
            if i == index:
                totalVelocity += noteList[i].velocity;
            else:
                totalVelocity +=  SCALE_FACTOR * noteList[i].velocity
        
        loudness[currOnset] = totalVelocity
        
    return loudness


# For each onset, determine dissonance value
def getDissonance(onsetsAll):
    # onsetsAll is a dict keyed by onset time; the items are a list of noteObjs
    prevPitch = -1
    prevOnset = -1
    prevEndTime = -1
    dissonanceVals = {}

    for key, notes in onsetsAll.items():
        currOnset = key
        noteList = notes
        chordPitches = getListofPitches(noteList)
        dissonanceVals[currOnset] = diss.calculateChordDissonance12tet(chordPitches)

    return dissonanceVals

    
