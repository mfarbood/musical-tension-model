# Some functions to resample vectors so they conform to a certain length or sample rate
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import resampy

def resampleByRate(y, oldRate, newRate):
    numPoints = len(y)
    newNumPoints = int(newRate/oldRate * numPoints)
    resampled = resampy.resample(y, oldRate, newRate, filter='kaiser_fast')

    showPlot = False
    if showPlot:
        totalTime = numPoints/oldRate
        x1 = np.linspace(0, totalTime, numPoints, endpoint=False)
        x2 = np.linspace(0, totalTime, newNumPoints, endpoint=False)

        plt.plot(x1, y, 'go-', x2, resampled, '.-')
        plt.legend(['data', 'resampled'], loc='best')
        plt.show()
    
    return resampled

def resampleByNumPoints(y, newNumPoints, oldSampleRate=10):
    numPoints = len(y)
    resampled = signal.resample(y, newNumPoints)
 
    showPlot = False
    if showPlot:
        totalTime = numPoints/oldSampleRate
        x1 = np.linspace(0, totalTime, numPoints, endpoint=False)
        x2 = np.linspace(0, totalTime, newNumPoints, endpoint=False)
        plt.plot(x1, y, 'go-', x2, resampled, '.-')
        plt.legend(['data', 'resampled'], loc='best')
        plt.show()

    return resampled


# Arguments: input is a list of vals NOT a matrix
def normalize(input, filterLen=0):
    # Get z-scores
    normalizedVals = np.array(input)
    stdev = np.std(normalizedVals)
    
    if stdev != 0:
        normalizedVals = (normalizedVals - np.mean(normalizedVals))/ stdev
    else:
        normalizedVals = np.zeros(len(input))
    
    # Optionally, smooth the feature graphs - THIS IS NOT IMPLEMENTED YET
    # TO-DO optionally filter signal here if filterLen > 0 
    
    return normalizedVals

# Argument: vector is a list; newLen is a new length
def resampleGivenLength(vector, newLen):
    oldLen = len(vector)
    resampledVector = np.array([])
    
    # Up sample
    if newLen > oldLen:
        nextNewIndex = 0
        currNewIndex = 0
        for i in range(1,oldLen):
            nextNewIndex = int(i/oldLen * newLen)
            while currNewIndex < nextNewIndex:
                resampledVector = np.concatenate((resampledVector, [vector[i-1]]))
                currNewIndex+=1
        while currNewIndex < newLen:
            resampledVector = np.concatenate((resampledVector, [vector[-1]]))
            currNewIndex+=1
    # Down sample
    elif newLen < oldLen:
        #resampledVector = resampleByNumPoints(vector, newLen)
        oldIndex = 0
        for i in range(0,newLen):
            oldIndex = int(i/newLen * oldLen)
            resampledVector = np.concatenate((resampledVector, [vector[oldIndex]]))
             
    return resampledVector

