# Musical tension trend-salience model
# Author: Morwaread Farbood
#
# Return value: the tension prediction, given the features
# Function parameters
#   features: 2D matrix with rows containing feature graphs
#   target: vector representing the empirical data (e.g., mean continuous tension response)
#   featureList: cell array containing strings describing the features
#   featureWeights: vector containing relative weights for each feature
#   memoryWindowDur: memory window duration in seconds
#   sampleRate: numbers of samples per second for both the features and target
#   attentionalWindowDur: attentional window duration in seconds
#   windowShift: the hopfactor of moving window in seconds (recommended: .25 sec)
#   name: identifier used to save/label results
#   showGraph: true = display figures
#   memoryWeight: weighted effect of memory window on attentional window (recommended value: 5)
#   initSlope: initial starting slope (recommended: positive value)
#   lag: for display/comparison purposes; the amount of lag in seconds, assumed for target

import numpy as np
import math
import helperFunctions as hf
import matplotlib as mpl
import matplotlib.pyplot as plt

def runModel(features, target, featureList, featureWeights, memoryWindowDur, sampleRate, 
                       attentionalWindowDur, windowShift, name, memoryWeight, initSlope, lag, sliderOnset=False, showFigures=False):

    predictionResult = []
    # Convert to numpy arrays
    target = np.array(target)
    features = np.array(features)
    
    error = False
    # error checking to make sure dimensions of arguments match
    if len(featureWeights) != len(features):
        print('ERROR: featureWeights length does not match number of feature graphs\n')
        error = True
    if len(featureWeights) != len(featureList):
        print('ERROR: featureWeights length does not match featureList length\n')
        error = True
    if target.size > 0 and target.size != len(features[0]):
        print('ERROR: feature vector lengths (%(featureLen)d) do not match target length (%(targetLen)d).\n' %
              {'featureLen': len(features[0]), 'targetLen': target.size})
        error = True
    
    if (error):
        return predictionResult
    
    # Flag to indicate whether a target vector has been provided or not
    if target.size == 0:
        targetSpecified = False
    else:
        targetSpecified = True

    numPoints = len(features[0])
    numFeatures = len(featureWeights)

# Loop the excerpt in attentionalWindowDuration chunks until the end is reached
    samplesPerAttentionalWindow = hf.normal_round(sampleRate * attentionalWindowDur)
    samplesPerMemoryWindow = hf.normal_round(memoryWindowDur * sampleRate)

    # numWindows = ceil(numPoints/samplesPerAttentionalWindow);
    prediction = []
    endReached = False
    shift = hf.normal_round(windowShift * sampleRate)
    if shift == 0:
       shift = 1

    startWindowDur = 2 * sampleRate # two (one) seconds for the initial slider motion upwards
    prevSlope = initSlope

    # Weights are divided by this value so all the feature weights add to 1
    absoluteValsofWeights = [int(math.fabs(ele)) for ele in featureWeights]
    scaleWeightFactor = sum(absoluteValsofWeights)
    weights =  np.array(featureWeights)/scaleWeightFactor
    # Hard coded slope value for the initial upward movement of slider
    initialSliderMovementSlope = .25/scaleWeightFactor; 
    memoryMultiplier = memoryWeight
    memoryWindowActive = False

    # Attentional window is minimally 2 samples in length (thus the initally index of -samplesPerAttentionalWindow+2)
    for i in range(-samplesPerAttentionalWindow+2, numPoints, shift):
        # find the start and end points of current window of time in question
        startpt = i    
        endpt = samplesPerAttentionalWindow + i - 1
        x = np.array(range(0,samplesPerAttentionalWindow))
        # if near the end, the attentional window is smaller
        if numPoints - endpt <= 0:
            endpt = numPoints - 1 
            x = np.array(range(0, endpt - startpt + 1))
        # In the beginning when the attentional window is still less than designated duration
        elif startpt < 0:
            startpt = 0
            endpt = samplesPerAttentionalWindow + i - 1
            if endpt < 1:
                endpt = 1
            x = np.array(range(0, endpt - startpt + 1))
    
        # Find start and end points of memory window if applicable
        if memoryWindowDur > 0:
            memEnd = startpt - 1
            memStart = memEnd - samplesPerMemoryWindow + 1
            if memStart < 0:
                memStart = 0
            if memEnd >= 3: # need at least 2 values for memory window
                memoryWindowActive = True
            else:
                memoryWindowActive = False
     
       
        if not endReached and endpt > startpt:
            # Get the parts of the feature graphs that correspond to the current window
            currFeatures = features[:,startpt:endpt+1]
  
            # Find the slope and linear fit for each feature at current window in time
            slopes = np.zeros(numFeatures)        
            for j in range(0,numFeatures):
                p = np.polyfit(x,currFeatures[j],1)
                slopes[j] = p[0]
                if np.isnan(slopes[j]):
                    slopes[j] = 0
                    print("WARNING: NAN in data!!")
             
            # Get the slopes of the memory windows, if there are any
            if memoryWindowDur > 0 and memoryWindowActive:                
                currMemoryWindowSamples = memEnd - memStart + 1
                xMem = range(0,currMemoryWindowSamples)
                p1 = np.polyfit(xMem,prediction[memStart:memEnd+1],1)
                prevSlope = p1[0]
                if np.isnan(prevSlope):
                    prevSlope = 0

            # Dealing with the intial slider movement upwards
            if sliderOnset and i <  startWindowDur:
                # hard coded slope value -- pretty steep
                slopeTotal = initialSliderMovementSlope 
            else:
                slopeTotal = sum(weights * slopes)
            
            if np.isnan(slopeTotal):
                print("NANs!!")

            # If the trend in this window is same as the trend in the previous
            # window (positive or negation) increase magnitude of predicted slope.
            epsilon = .0001
            decay = .001

            if memoryWindowDur > 0 and memoryWindowActive:
                # If there is no change in attentional slope (practically
                # speaking) following no change in the memory window, add a
                # decrease the slope of the attentional window slightly.
                if slopeTotal < epsilon and slopeTotal > -epsilon and prevSlope < epsilon and prevSlope > -epsilon:
                    slopeTotal = slopeTotal - decay
                # if both attentional and memory windows are in the same
                # direction, negative or positive, strengthen the attentional
                # window slope in the current direction
                elif (slopeTotal > 0 and prevSlope > 0) or (slopeTotal < 0 and prevSlope < 0):
                    slopeTotal = slopeTotal * memoryMultiplier
                            
            # This is our new predicted line
            y = slopeTotal * x

            # Now add the current y to the overall prediction line
            if startpt == 0:
                prediction = y
            # The middle is the part that needs to be averaged with the
            else:
                start = prediction[0:startpt] 
                originalStartMergeVal = prediction[startpt]
                middle = np.array(y[0:len(prediction)-startpt] + prediction[startpt:])/2  

                if middle.size > 0:
                    offset1 = originalStartMergeVal - middle[0]
                    middle = middle + offset1

                endChunk = y[len(middle):]                
                if endChunk.size > 0 and middle.size > 0:
                    offset2 = middle[-1] - endChunk[0]
                    endChunk = endChunk + offset2

                prediction = np.concatenate((start, middle, endChunk), axis=0)
        
        if endpt == numPoints - 1:
            endReached = True

    # Normalize prediction curve
    prediction = (prediction - np.mean(prediction))/np.std(prediction, ddof=1)

    lagOffset = int(lag * sampleRate)
    if (lagOffset > 0):
        trim = np.zeros(lagOffset)
        #trim[:] = np.NAN
        trim[:] = prediction[0]
        predictionTrimmed = prediction[0:-lagOffset]
        predictionLagged = np.concatenate((trim, predictionTrimmed), axis=0)
        prediction = predictionLagged

    if showFigures:
        currName = name + '_result'
        target = target.conj().transpose() 
        # Graph prediction along with target (empirical data) if available for comparison
        graphPrediction(prediction, target, currName, sampleRate, numPoints)
        graphFeatures(target, features, featureList, sampleRate, name, numPoints, numFeatures)

    return prediction

#############################################################################################################
#############################################################################################################


def graphPrediction(prediction, target, currName, sampleRate, numPoints):
    black = [0, 0, 0]
    x = np.linspace(0,numPoints/sampleRate,numPoints)      
    fig, ax = plt.subplots() 
    ax.plot(x, prediction, color='red', label='Prediction')
    
    if np.size(target) > 0:
        ax.plot(x, target, color='blue', label='Target')

    ax.set_xlabel('Time (seconds)')  # Add an x-label to the axes.
    ax.set_ylabel('Tension')  # Add a y-label to the axes.
    ax.set_title("Tension prediction")  # Add a title to the axes.
    ax.legend()  # Add a legend.
    plt.ioff()
    plt.show()

# Graph the features along with (optionally) a tension graph; tension can either be empirical data (target), or the predicted tension
def graphFeatures(tension, features, featureList, sampleRate, name, numPoints, numFeatures):

    # Line styles
    solid = '-'; dashed = '--'; dotted = ':'; dashDotted = '-.'
    tLineStyle = solid
    fLineStyle = solid
    tLineWidth = 2
    fLineWidth = 1

    # Colors
    black = [0, 0, 0]; gray = [.5, .5, .5]; red = [1, 0, 0]; green = [0, 1, 0]
    blue = [0, 0, 1]; purple = [1, 0, 1]; blueGreen = [0, .5, .5] 
    orange = [1, .65, 0]; darkGreen = [0, .5, 0]; lightBlue = [.7, .7, 1]
    
    tColor = black
    fColor = [red, blue, purple, green, gray, orange, lightBlue, gray, darkGreen]
    numColors = len(fColor)

    xLabel = 'Time (seconds)'
    yLabel = 'Normalized Data'
    title = name
    x = np.linspace(0,numPoints/sampleRate,numPoints)      
    fig, ax = plt.subplots() 

    for i in range(0, numFeatures):
        ax.plot(x, features[i,:], color=fColor[i % numColors], linewidth=fLineWidth, linestyle=fLineStyle, label=featureList[i])

    if len(tension) > 0:
        ax.plot(x, tension, color=tColor, linewidth=tLineWidth, linestyle=tLineStyle, label='Tension')

    ax.set_xlabel(xLabel)  # Add an x-label to the axes.
    ax.set_ylabel(yLabel)  # Add a y-label to the axes.
    ax.set_title(title)  # Add a title to the axes.
    ax.legend()  # Add a legend.
    plt.ioff()
    plt.show()
    
