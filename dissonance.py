# Calculates dissonance based on sensory dissonance (Sethares) for 12 tone equal temperament (rough values)
import numpy as np

intervalDissonance = {0 : 0, 1 : 0.85, 2 : 0.4, 3 : 0.255, 4 : 0.225, 5 : 0.15, 6 : 0.275, 7 : 0.075, 8 : 0.275, 9 : 0.175, 10 : 0.225, 11 : 0.4}

# Arguments: notes is a list of notes denoting a chord
def calculateChordDissonance12tet(notes):
    numNotes = len(notes)
    totalDissonance = 0
    for i in range(0,numNotes):
        for j in range(i+1,numNotes):
            interval = (abs(notes[i] - notes[j])) % 12
            currDissonance = intervalDissonance[interval]
            totalDissonance+=currDissonance


    if np.isnan(totalDissonance):
        print("NAN dissonance!!!")
        
    return totalDissonance

"""
#Example usage:
chord = [60, 64, 67, 72]
print(chord)
calculateChordDissonance(chord)
"""
