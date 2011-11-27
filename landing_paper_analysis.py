import flydra_analysis_dataset as fad
import flydra_analysis_plot as fap
import trajectory_analysis_core as tac
import numpy as np



def example_analysis(filename, raw_dataset_name = 'example_raw_dataset'):
    # filename should be a .h5 file
    info = {'post_type': 'black', 'post_position': np.zeros([3]), 'post_radius': 0.009565}
    dataset = fad.Dataset()
    dataset.load_data(filename, kalman_smoothing=True, save_covariance=False, info=info)
    print 'saving dataset...'
    fad.save(dataset, raw_dataset_name)
    
    
def set_minimum_distance_to_post(dataset):
    # cull based on trajectory length
    keys_to_remove = []
    for k, trajec in dataset.trajecs.iteritems():
        remove = False
        d = np.min(trajec.xy_distance_to_post)
        if d > 0.2:
            remove = True
        if remove is True:
            keys_to_remove.append(k)
    for k in keys_to_remove:   
        dataset.del_trajec(k)
    
    
def example_process_dataset(dataset, processed_dataset_name = 'example_processed_dataset'):
    
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
        tac.calc_heading(trajec)
        tac.calc_saccades(trajec, threshold_lo=300.)
        
    fad.save(dataset, processed_dataset_name)
