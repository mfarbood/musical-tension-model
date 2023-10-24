# musical-tension-model
An implemention of Farbood (2012) musical tension model. Currently the input format is a MIDI file.  

tensionModel.py is the implementation of the actual model. It takes as input musical feature descriptions and outputs a tension prediction. While the model itself can be used with any type of input - i.e., feature vectors automatically extracted from either symbolic or audio files or analyzed by hand - the analysis functions included currently only provides automatic analysis of MIDI files.

testTensionModel.py is a sample script showing how the model can be used.  

Note on feature analysis components:
These are are somewhat preliminary and include melodic contour analysis, loudness analysis (based on MIDI velocities), tempo analysis (based on MIDI tempo change messages), dissonance, and harmonic tension. The harmonic tension values are calculated using [Guo's midi-miner](https://github.com/ruiguo-bio/midi-miner), which produces tonal tension values based on Chew's spiral array model. The dissonance values are roughly based on [Sethares's dissonance calculations](https://sethares.engr.wisc.edu/comprog.html).
 
