# Extract features from a MIDI file representation of music
import music21
import numpy as np 
import noteObj
import tonalTension

# Indices for each feature
iOnsetFreq = 0
iMelodicContour = 1
iLoudness = 2
iTempo = 3
iHarmony = 4
iDissonance = 5
NUM_FEATURES = 6 # This can change in the future, but it's the max for now
featureList = ["Onset freq", "Melodic contour", "Loudness", "Tempo", "Harmony", "Dissonance"]


# Get the tension profile for music in MIDI file format
def extractFeaturesMidi(inputFile, sampleRate=10, bOnsetFreq=True, bMelodicContour=True, bLoudness=True, bTempo=True, bHarmony=True, bDissonance=True):
    
    # Read MIDI file
    # TO-DO: THIS NEEDS TO BE RECONSIDERED - quantization is not the solution to perceptual issues
    #score = music21.converter.parse(inputFile, forceSource=True, quantizePost=False)
    score = music21.converter.parse(inputFile, quarterLengthDivisors=[256]) 
    flatScore = score.flatten()

    onsetsAll = {} # Dictionary of all notes (as the form of noteObjs) keyed by onset time
    tempoChanges = {0 : [0, 120]} # Initalized to default MIDI tempo value 

    # Go through the entire score. Get all the notes and their respective onset times, durations, pitches, and MIDI velocity values;
    # and get tempo changes
    prevPitch = 0
    for ele in flatScore.secondsMap:
        element = ele['element']
        offsetSeconds = ele['offsetSeconds']
        if isinstance(element, music21.note.Note) or isinstance(element, music21.chord.Chord):
            if offsetSeconds in onsetsAll.keys():
                # NoteObj contains onset, pitch, endTime, velocity
                onsetsAll[offsetSeconds].extend(noteObj.returnNotes(offsetSeconds, element))
            else:
                onsetsAll[offsetSeconds] = noteObj.returnNotes(offsetSeconds, element)
            #for note in onsetsAll[offsetSeconds]:
            #    note.print()
            #print("-----")
        # Get tempo change messages
        elif isinstance(element, music21.tempo.MetronomeMark):
            tempoChanges[offsetSeconds] = [offsetSeconds, element.number]

    ################################################################################################################################
    ################################################################################################################################
    #   Extract individual features
    ################################################################################################################################
    ################################################################################################################################
    
    # Sometimes music21 has a NAN value for this (sigh)
    totalDuration = flatScore.seconds
    if np.isnan(totalDuration):
        lastNote = flatScore.secondsMap[-1]
        totalDuration = lastNote["endTimeSeconds"]

    totalSamples = int(totalDuration * sampleRate)
    features = np.zeros((NUM_FEATURES,totalSamples))

    #print("Total dur: ", "{:.2f}".format(totalDuration), "sec; Total samples: ", totalSamples)

    ################################################################################################################################
    # Onset frequency
    ################################################################################################################################

    # Create onset frequency graph at the given sample rate
    if bOnsetFreq:
        onsetTimes = np.array([])
        for onset, noteList in onsetsAll.items():
            onsetTimes = np.append(onsetTimes, onset)

        onsetFreq = np.diff(onsetTimes)
        onsetFreq = 1/onsetFreq
        onsetFreq = np.concatenate([[0], onsetFreq])  

        numOnsets = len(onsetTimes)
        sampleIndex = 0
        for j in range(1,numOnsets): # start at the second onset val because the values will be filled in with the previous onset val
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextOnsetTime = int(onsetTimes[j] * 100000)
            while currSampleTime < nextOnsetTime:
                features[iOnsetFreq,sampleIndex] = onsetFreq[j-1]                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)

        while sampleIndex <= totalSamples - 1:
            features[iOnsetFreq,sampleIndex] = onsetFreq[numOnsets-1]
            sampleIndex = sampleIndex + 1

    
    ################################################################################################################################
    # Melodic contour: 
    # Takes the highest current onset, but only if it's higher than all the current held notes; this is a hack and
    # ideally there needs to be a more polyphonic approach that produces (possibly) multiple perceptually relevant musical lines.
    # See function noteObj.getMelodicLine(), which calculates these values
    ################################################################################################################################

    # Extract a melodic contour
    if bMelodicContour:
        highestPitches = noteObj.getMelodicLine(onsetsAll)

        numNotesInMelodyLine = len(highestPitches)
        sampleIndex = 0
        prevVal = 0
        for key, val in highestPitches.items():
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextNoteTime = int(key * 100000)
            while currSampleTime < nextNoteTime:
                features[iMelodicContour,sampleIndex] = prevVal                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)
            prevVal = val    

        while sampleIndex <= totalSamples - 1:
            features[iMelodicContour,sampleIndex] = val
            sampleIndex = sampleIndex + 1

        # If there are zeros at the beginning of the melodic contour vector, make them the same value as the first non-zero MIDI value
        currIndex = 0
        currMidiPitch = features[iMelodicContour,currIndex]
        while currIndex < totalSamples - 1 and currMidiPitch == 0:
            currIndex += 1
            currMidiPitch = features[iMelodicContour,currIndex]

        # If the whole vector isn't zero (should never be the case, but error checking here)
        if currIndex != totalSamples - 1:
            for i in range(0,currIndex):
                features[iMelodicContour, i] = currMidiPitch
 
    
    ################################################################################################################################
    # Loudness:
    # This takes into account multiple note ons but is not strictly additive.  Additional lower notes in a chord/simulteneous onsets
    # scaled.  See the function noteObj.getLoudness() which calculates these values
    ################################################################################################################################

    if bLoudness:
        loudness = noteObj.getLoudness(onsetsAll)

        numLoudnessVals = len(loudness)
        sampleIndex = 0
        prevVal = 0
        for key, val in loudness.items():
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextVal = int(key * 100000)
            while currSampleTime < nextVal:
                features[iLoudness,sampleIndex] = prevVal                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)
            prevVal = val    

        while sampleIndex <= totalSamples - 1:
            features[iLoudness,sampleIndex] = val
            sampleIndex = sampleIndex + 1   


    ################################################################################################################################
    # Tempo:
    # Tempo changes are determined by MIDI tempo messages.  If the MIDI file is screwy, the tempo changes might not make
    # much sense.
    ################################################################################################################################

    if bTempo:
        numTempoChanges = len(tempoChanges)
        sampleIndex = 0
        prevVal = 0
        for key, val in tempoChanges.items():
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextTempoTime = int(val[0] * 100000)
            while currSampleTime < nextTempoTime:
                features[iTempo,sampleIndex] = prevVal                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)
            prevVal = val[1]    

        while sampleIndex <= totalSamples - 1:
            features[iTempo,sampleIndex] = val[1]
            sampleIndex = sampleIndex + 1

    
    ################################################################################################################################
    # Harmonic tension:
    # This uses R. Guo's midi-miner code, slightly modified to work within the current framework:
    # Original code: https://github.com/ruiguo-bio/midi-miner
    # This calculates harmonic tension based on Chew's sprial array model.  Reference:
    # Guo R, Simpson I, Magnusson T, Kiefer C., Herremans D. 2020. A variational autoencoder for music generation 
    # controlled by tonal tension. Joint Conference on AI Music Creativity (CSMC + MuMe).
    #
    # Ideally, a version of Lerdahl's (2001) tonal tension model should be another option. 
    ################################################################################################################################

    if bHarmony:
        outputDir = "output" # if empty, no data files are saved
        windowSize = 2  # 1 = every beat; 2 = every 2 beats; -1 = every downbeat
        endRatio = 1
        keyChanged=False
        keyName=''
        
        harmonicTension, times = tonalTension.analyzeTonalTension(inputFile, outputDir, windowSize, endRatio, keyChanged, keyName)

        numPoints = len(harmonicTension)
        sampleIndex = 0
        for j in range(1,numPoints): 
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextVal = int(times[j] * 100000)
            while currSampleTime < nextVal:
                features[iHarmony,sampleIndex] = harmonicTension[j-1]                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)

        while sampleIndex <= totalSamples - 1:
            features[iHarmony,sampleIndex] = harmonicTension[numPoints-1]
            sampleIndex = sampleIndex + 1


    ################################################################################################################################
    # Dissonance
    ################################################################################################################################

    if bDissonance:
        dissonanceVals = noteObj.getDissonance(onsetsAll)

        sampleIndex = 0
        prevVal = 0
        for key, val in dissonanceVals.items():
            currSampleTime = int(sampleIndex/sampleRate * 100000)  
            nextOnsetTime = int(key * 100000)

            while currSampleTime < nextOnsetTime:
                features[iDissonance,sampleIndex] = prevVal                       
                sampleIndex = sampleIndex + 1
                currSampleTime = int(sampleIndex/sampleRate * 100000)
            prevVal = val

        while sampleIndex <= totalSamples - 1:
            features[iDissonance,sampleIndex] = val
            sampleIndex = sampleIndex + 1

    return features

