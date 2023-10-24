# musical-tension-model
An implemention of Farbood (2012) musical tension model. Currently the input format is a MIDI file.  

tensionModel.py is the implementation of the actual model. It takes as input musical feature descriptions and outputs a tension prediction. While the model itself can be used with any type of input - i.e., feature vectors automatically extracted from either symbolic or audio files or analyzed by hand - the analysis functions included currently only provides automatic analysis of MIDI files.

testTensionModel.py is a sample script showing how the model can be used.  

Note on feature analysis components:
These are are somewhat preliminary. In particular, the harmonic/tonal tension component needs to be updated. Currently utilized is R. Guo's midi-miner, which produces tonal tension values based on Chew's spiral array model.
 
