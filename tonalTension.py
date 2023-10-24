
# This is version of R. Guo's midi-miner code that is slightly modified not to work just work from the command line.  
# Original code: https://github.com/ruiguo-bio/midi-miner
# This calculates harmonic tension based on Chew's sprial array model.  Reference:
# Guo R, Simpson I, Magnusson T, Kiefer C., Herremans D. 2020. A variational autoencoder for music generation 
# controlled by tonal tension. Joint Conference on AI Music Creativity (CSMC + MuMe).

import sys
import music21
import numpy as np 
import tension_calculation as tc
import json
import math
import os
import sys
from collections import Counter
import matplotlib.pyplot as plt
from numpy import ndarray

PianoRoll = ndarray

major_enharmonics = {'C#': 'D-',
                     'D#': 'E-',
                     'F#': 'G-',
                     'G#': 'A-',
                     'A#': 'B-'}


minor_enharmonics = {'D-': 'C#',
                     'D#': 'E-',
                     'G-': 'F#',
                     'A-': 'G#',
                     'A#': 'B-'}

octave = 12

pitch_index_to_sharp_names = np.array(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G',
                                       'G#', 'A', 'A#', 'B'])


pitch_index_to_flat_names = np.array(['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G',
                                      'A-', 'A', 'B-', 'B'])


pitch_name_to_pitch_index = {"G-": -6, "D-": -5, "A-": -4, "E-": -3,
                             "B-": -2, "F": -1, "C": 0, "G": 1, "D": 2, "A": 3,
                             "E": 4, "B": 5, "F#": 6, "C#": 7, "G#": 8, "D#": 9,
                             "A#": 10}

pitch_index_to_pitch_name = {v: k for k,
                             v in pitch_name_to_pitch_index.items()}

valid_major = ["G-", "D-", "A-", "E-", "B-", "F", "C", "G", "D", "A", "E", "B"]

valid_minor = ["E-", "B-", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#"]

enharmonic_dict = {"F#": "G-", "C#": "D-", "G#": "A-", "D#": "E-", "A#": "B-"}
enharmonic_reverse_dict = {v: k for k, v in enharmonic_dict.items()}

all_key_names = ['C major', 'G major', 'D major', 'A major',
                 'E major', 'B major', 'F major', 'B- major',
                 'E- major', 'A- major', 'D- major', 'G- major',
                 'A minor', 'E minor', 'B minor', 'F# minor',
                 'C# minor', 'G# minor', 'D minor', 'G minor',
                 'C minor', 'F minor', 'B- minor', 'E- minor',
                 ]


# use ['C','D-','D','E-','E','F','F#','G','A-','A','B-','B'] to map the midi to pitch name
note_index_to_pitch_index = [0, -5, 2, -3, 4, -1, -6, 1, -4, 3, -2, 5]

weight = np.array([0.536, 0.274, 0.19])
alpha = 0.75
beta = 0.75
verticalStep = 0.4
radius = 1.0

def getTonalTension(file_name, output_folder, vertical_step, track_num, window_size, key_name, key_changed, end_ratio):

    retvals = []
    if math.sqrt(2/15) <= vertical_step <= math.sqrt(0.2):
        verticalStep = vertical_step
    else:
        print('invalid vertical step, use 0.4 instead')
        verticalStep = 0.4

    #output_json_name = os.path.join(output_folder, "files_result.json")

    files_result = {}

    # test purpose
    # note_to_note_diff = note_to_note_pos([0,1,2,3,4,5,6,7,8,9,10,11],pitch_index_to_position(note_index_to_pitch_index[0]))
    # note_to_key_diff = note_to_key_pos([0,1,2,3,4,5,6,7,8,9,10,11],major_key_position(0))
    # chord_to_key_diff = chord_to_key_pos([0,1,2,3,4,5,6,7,8,9,10,11],major_key_position(0))
    # key_to_key_diff = key_to_key_pos([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], major_key_position(0))

    if len(file_name) > 0:
        all_names = [file_name]
        input_folder = os.path.dirname(file_name)
    else:
        all_names = os.walk(input_folder)

    for file_name in all_names:

        base_name = os.path.basename(file_name)

        # logger.info(f'working on {file_name}')
        # file_name = '/Users/ruiguo/Downloads/36067affdbefb38a779e510e6edabe6b.mid'
        result = tc.extract_notes(file_name, track_num)

        if result is None:
            continue
        else:
            pm, piano_roll, sixteenth_time, beat_time, down_beat_time, beat_indices, down_beat_indices = result

        try:
            if key_name == '':
                # key_name = get_key_name(file_name)
                key_name = all_key_names

                """ def cal_tension(file_name: str,
                piano_roll: PianoRoll,
                sixteenth_time: ndarray,
                beat_time: ndarray,
                beat_indices: List[int],
                down_beat_time: ndarray,
                down_beat_indices: List[int],
                input_folder: str,
                output_folder: str,
                window_size=1,
                key_name='',
                end_ratio = .2,
                key_changed = False): """

                retvals = tc.cal_tension(
                    file_name, piano_roll, sixteenth_time, beat_time, beat_indices, down_beat_time, down_beat_indices, pm, input_folder, output_folder, window_size, key_name, end_ratio, key_changed)

            else:
                retvals = tc.cal_tension(
                    file_name, piano_roll, sixteenth_time, beat_time, beat_indices, down_beat_time, down_beat_indices, pm, input_folder, output_folder, window_size, [key_name], end_ratio, key_changed)
                    
            total_tension, diameters, centroid_diff, key_name, key_change_time, key_change_bar, key_change_name, new_output_folder, times = retvals

            if key_name == '':
                result_list = []
                result_list.append(key_name)

                s = music21.converter.parse(file_name)
                # s = music21.converter.parse(files[i][:-12] + '_remi.mid')

                p = music21.analysis.discrete.KrumhanslSchmuckler()
                p1 = music21.analysis.discrete.TemperleyKostkaPayne()
                p2 = music21.analysis.discrete.BellmanBudge()
                key1 = p.getSolution(s).name
                key2 = p1.getSolution(s).name
                key3 = p2.getSolution(s).name

                key1_name = key1.split()[0].upper()
                key1_mode = key1.split()[1]

                key2_name = key2.split()[0].upper()
                key2_mode = key2.split()[1]

                key3_name = key3.split()[0].upper()
                key3_mode = key3.split()[1]

                if key1_mode == 'major':
                    if key1_name in major_enharmonics:
                        result_list.append(
                            major_enharmonics[key1_name] + ' ' + key1_mode)
                    else:
                        result_list.append(key1_name + ' ' + key1_mode)
                else:
                    if key1_name in minor_enharmonics:
                        result_list.append(
                            minor_enharmonics[key1_name] + ' ' + key1_mode)
                    else:
                        result_list.append(key1_name + ' ' + key1_mode)

                if key2_mode == 'major':
                    if key2_name in major_enharmonics:
                        result_list.append(
                            major_enharmonics[key2_name] + ' ' + key2_mode)
                    else:
                        result_list.append(key2_name + ' ' + key2_mode)
                else:
                    if key2_name in minor_enharmonics:
                        result_list.append(
                            minor_enharmonics[key2_name] + ' ' + key2_mode)
                    else:
                        result_list.append(key2_name + ' ' + key2_mode)

                if key3_mode == 'major':
                    if key3_name in major_enharmonics:
                        result_list.append(
                            major_enharmonics[key3_name] + ' ' + key3_mode)
                    else:
                        result_list.append(key3_name + ' ' + key3_mode)
                else:
                    if key3_name in minor_enharmonics:
                        result_list.append(
                            minor_enharmonics[key3_name] + ' ' + key3_mode)
                    else:
                        result_list.append(key3_name + ' ' + key3_mode)

                count_result = Counter(result_list)
                result_key = sorted(
                    count_result, key=count_result.get, reverse=True)[0]

                retvals = tc.cal_tension(
                    file_name, piano_roll, sixteenth_time, beat_time, beat_indices, down_beat_time, down_beat_indices, pm, input_folder, output_folder, window_size, [result_key], end_ratio, key_changed)

                total_tension, diameters, centroid_diff, key_name, key_change_time, key_change_bar, key_change_name, new_output_folder, times = retvals

            #print(f'file name {file_name}, calculated key name {key_name}')
            #print(f'if the calculated key name is not correct, you can set the key name by -n parameter')

            if np.count_nonzero(total_tension) == 0:
                print(f"tensile 0 skip {file_name}")

                continue

            if np.count_nonzero(diameters) == 0:
                print(f"diameters 0, skip {file_name}")

                continue

        except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError) as e:
            exception_str = 'Unexpected error in ' + \
                file_name + ':\n', e, sys.exc_info()[0]
            print(exception_str)

        if key_name is not None:
            files_result[new_output_folder + '/' + base_name] = []
            files_result[new_output_folder + '/' + base_name].append(key_name)
            files_result[new_output_folder + '/' +
                            base_name].append(int(key_change_time))
            files_result[new_output_folder + '/' +
                            base_name].append(int(key_change_bar))
            files_result[new_output_folder + '/' +
                            base_name].append(key_change_name)

        else:
            print(f'cannot find the key of song {file_name}, skip this file')

#    print(len(files_result))
#    with open(os.path.join(output_folder, 'files_result.json'), 'w') as fp:
#        json.dump(files_result, fp)

    return retvals


def draw_tension(time, values):
    fig = plt.figure(figsize=(20, 10))
    plt.rcParams['xtick.labelsize'] = 14
    plt.plot(time,values,marker='o')
    plt.tight_layout()
    plt.show()

def analyzeTonalTension(fileName, outputDir, windowSize, endRatio = .5, keyChanged=False, keyName='', trackNum=0):
    # trackNum = 0 default means use all tracks
    result = getTonalTension(fileName, outputDir, verticalStep, trackNum, windowSize, keyName, keyChanged, endRatio)
    total_tension, diameters, centroid_diff, key_name, key_change_time, key_change_bar, key_change_name, new_output_folder, times = result
    #draw_tension(times[:len(total_tension)],total_tension)
    return total_tension, times