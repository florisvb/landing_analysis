import flydra_analysis_dataset as fad
import flydra_analysis_plot as fap
import trajectory_analysis_core as tac
import trajectory_analysis_specific as tas
import numpy as np

import trajectory_analysis_specific as tas
import nopost_analysis as npa

def load_raw_nopost_data(filename, raw_dataset_name = 'dataset_nopost_raw'):
    # filename should be a .h5 file
    info = {'post_type': 'none', 'post_position': np.zeros([3]), 'post_radius': 0.009565}
    dataset = fad.Dataset()
    dataset.load_data(filename, kalman_smoothing=True, save_covariance=False, info=info)
    print 'saving dataset...'
    fad.save(dataset, raw_dataset_name)
    return dataset
    
    
def set_minimum_distance_to_post(dataset):
    # cull based on trajectory length
    keys_to_remove = []
    for k, trajec in dataset.trajecs.iteritems():
        remove = False
            
            
        if trajec.frame_nearest_to_post == 0:
            remove = True
        
        # check that before coming close to post, there is a frame where fly is 20cm away from the post
        frames = np.arange(0, trajec.frame_nearest_to_post)
        frame_before_nearest = tas.get_frame_at_distance(trajec, 0.2, singleframe=False, frames=frames)
        
        if frame_before_nearest is None:
            remove = True
        
        # check that after coming close to post, there is a frame where fly is 20cm away from post
        # should be for FLYBY's only
        frames = np.arange(trajec.frame_nearest_to_post, trajec.length)
        frame_after_nearest = tas.get_frame_at_distance(trajec, 0.2, singleframe=False, frames=frames)

        if frame_after_nearest is None:
            remove = True

        if remove is True:
            keys_to_remove.append(k)
        else:
            trajec.framerange = [frame_before_nearest[-1], frame_after_nearest[0]]        
                    
    for k in keys_to_remove:   
        dataset.del_trajec(k)
    
    
def process_nopost_dataset(dataset, processed_dataset_name = 'dataset_nopost_processed'):
    
    def batch_1(dataset):
        # cull based on trajectory length
        keys_to_remove = []
        for k, trajec in dataset.trajecs.iteritems():
            remove = False
            if trajec.length < 25:
                remove = True
            if np.max(trajec.speed) < 0.05:
                remove = True
            if remove is True:
                keys_to_remove.append(k)
        for k in keys_to_remove:   
            dataset.del_trajec(k)
        
        # post dimensions
        top_center = [0,0,0]
        xy_point = top_center[0:2]
        z_point = top_center[2]
        radius = 0.009565

        # calculate useful states
        for k, trajec in dataset.trajecs.iteritems():
            print 'processing: ', k
            tac.calc_xy_distance_to_point(trajec, xy_point)
            tac.calc_z_distance_to_point(trajec, z_point)
            tac.calc_xy_distance_to_post(trajec, top_center, radius)
        
    def batch_2(dataset):
        for k, trajec in dataset.trajecs.iteritems():
            tas.calc_frame_nearest_to_post(trajec)
        
    def batch_3(dataset):
        # more culling
        set_minimum_distance_to_post(dataset)
        
    def batch_4(dataset):
        # calculate more useful states
        for k, trajec in dataset.trajecs.iteritems():
            print 'batch_4: ', k
            tac.calc_heading(trajec)
            tas.calc_post_dynamics_for_flydra_trajectory(trajec)
            tac.calc_saccades(trajec, threshold_lo=300.)
            
    def batch_5(dataset):
        # classify
        for k, trajec in dataset.trajecs.iteritems():   
            npa.classify_false_post(trajec)
            npa.calc_frame_of_landing(trajec)
       
    #batch_1(dataset) 
    #batch_2(dataset)
    #batch_3(dataset)
    #batch_4(dataset)
    batch_5(dataset)
            
    #fad.save(dataset, processed_dataset_name)
    
    
    
    
    
    
    
    
    
    
