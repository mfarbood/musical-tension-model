# Sample script for reading in MIDI file and automatically producing a tension prediction based on musical feature
# Note that in this sample code, no empirical data ("target") is displayed/compared to the tension prediction

import numpy as np 
import featureAnalysis as analysis
import dataProcessing
import tensionModel

SAMPLE_RATE = 10

# Original feature weights from Farbood (2012) (minus the dissonsance)
featureWeights = [2, 3, 3, 2, 1, 1] # ["Onset freq", "Melodic contour", "Loudness", "Tempo", "Harmony", "Dissonance"]

showFigure = True
inputFile = "midi/Brahms.mid"

# Flags for deciding which features to extract from music and input into the model
bOnsetFreq = True
bMelodicContour = True
bLoudness = True
bTempo = True
bHarmony = True
bDissonance = False

# Extract the features
features = analysis.extractFeaturesMidi(inputFile, SAMPLE_RATE, bOnsetFreq, bMelodicContour, bLoudness, bTempo, bHarmony, bDissonance)

# Set parameters for the tension model
initOffset = 0
memoryWindowDur = 3
attentionalWindowDur = 3
windowShift = .25
name = inputFile
memoryWeight = 5
initSlope = 1
lag = 1 # To-do error checking: check if too large also
sliderOnset = True

featureLen = len(features[0])

# No empirical data to compare to in this example
target = []

# Normalize features
for i in range(0, analysis.NUM_FEATURES):
    features[i,:] = dataProcessing.normalize(features[i,:])

# Get the tension prediction given the features
tensionPrediction = tensionModel.runModel(features, target, analysis.featureList, featureWeights, memoryWindowDur, SAMPLE_RATE, 
    attentionalWindowDur, windowShift, name, memoryWeight, initSlope, lag, sliderOnset)

# Normalize tension prediction
tensionPrediction = dataProcessing.normalize(tensionPrediction)

# Plot all features along with the tension prediction
numPoints = featureLen
if showFigure:
    tensionModel.graphFeatures(tensionPrediction, features, analysis.featureList, SAMPLE_RATE, name, numPoints, analysis.NUM_FEATURES)

