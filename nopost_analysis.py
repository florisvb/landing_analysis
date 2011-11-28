import flydra_analysis_dataset as fad
import copy
import numpy as np

import trajectory_analysis_specific as tas

def shift_no_post_dataset(dataset, shift_range=0.05):
    dataset_shifted = copy.copy(dataset)
    for k, trajec in dataset_shifted.trajecs.iteritems():
        trajec.positions[:, 0] += np.random.random()*shift_range - shift_range*2
    return dataset_shifted
    
def shift_datasets(dataset, nshifts=2):
    shifted_dataset_list = []
    for i in range(nshifts):
        shifted_dataset = shift_no_post_dataset(dataset, shift_range=0.05)
        shifted_dataset_list.append(shifted_dataset)

    dataset_merged = fad.merge_datasets(shifted_dataset_list)
    #fad.save(dataset_merged, 'shifted_dataset')
    return dataset_merged

def classify_false_post(trajec):
    
    if np.min(trajec.xy_distance_to_post) < 0.005:
        trajec.behavior = 'landing'
    else:
        trajec.behavior = 'flyby'
        
def calc_frame_of_landing(trajec):    
    
    if trajec.behavior == 'landing':
        frames = np.arange(trajec.framerange[0], trajec.frame_nearest_to_post+1)
        tmp_frames_of_landing = tas.get_frame_at_distance(trajec, 0.005, singleframe=False, frames=frames)
        trajec.frame_of_landing = tmp_frames_of_landing[0]
    
    elif trajec.behavior == 'flyby':
        trajec.frame_of_landing = trajec.length
        
