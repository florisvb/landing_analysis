import numpy as np
import floris_math

###
def calc_post_dynamics_for_flydra_trajectory(trajec):
    
    pos = trajec.positions[:,0:2]
    ori = trajec.velocities[:,0:2]    
    trajec.angle_to_post = np.zeros_like(trajec.speed)
    trajec.angle_subtended_by_post = np.zeros_like(trajec.speed)
    for i in range(len(ori)):
        ori[i,:] /= np.linalg.norm(ori[i,:])
        worldangle, signed_angletopost, angle_subtended_by_post = get_angle_to_nearest_edge(pos[i], ori[i], np.array([0,0]), trajec.info['post_radius'])
        trajec.angle_to_post[i] = signed_angletopost
        trajec.angle_subtended_by_post[i] = angle_subtended_by_post
        
###
def get_angle_to_nearest_edge(obj_pos, obj_ori, post_pos, post_radius):
    
    vec_to_post = post_pos - obj_pos
    dist_pos_to_post = np.linalg.norm(vec_to_post)
    obj_ori /= np.linalg.norm(obj_ori)    
    
    worldangle = np.arctan2(obj_ori[1], obj_ori[0]) # want angle between 0 and 360 deg
    if worldangle < 0:
        worldangle = np.pi*2+worldangle
    # remove angular rollover?    
    
    obj_ori_3vec = np.hstack( ( obj_ori, 0) ) 
    vec_to_post_3vec = np.hstack( (vec_to_post, 0 ) ) 
    
    signed_angle_to_post = np.sum(np.cross( vec_to_post_3vec, obj_ori_3vec ) )
    sin_signed_angle_to_post = signed_angle_to_post / (dist_pos_to_post)
    sign_of_angle_to_post = np.sign(np.arcsin(sin_signed_angle_to_post))
    
    cosangletopost = np.dot(vec_to_post, obj_ori) / dist_pos_to_post 
    angletopost = np.arccos(cosangletopost)
     
    signed_angletopost = -1*angletopost*sign_of_angle_to_post
    
    angle_subtended_by_post = 2*np.arcsin( post_radius / (dist_pos_to_post) )
    # need to remove NAN's.. 
    if np.isnan(angle_subtended_by_post): angle_subtended_by_post = np.pi
    angle_to_edge = np.abs(signed_angletopost)-np.abs(angle_subtended_by_post)/2.
    
    return worldangle, signed_angletopost, angle_subtended_by_post 
    


def calc_frame_nearest_to_post(trajec):
    trajec.frame_nearest_to_post = np.argmin(trajec.xy_distance_to_post)
    
    
def get_frame_at_distance(trajec, distance, singleframe=True, frames=None):
    if frames is None:
        frames = np.arange(0, trajec.frame_nearest_to_post).tolist()
    dist_to_post = trajec.xy_distance_to_post[frames]
    #print trajec.key, 'frames: ', frames
    
    try:
        dist_crossovers = np.where( floris_math.diffa(np.sign(dist_to_post - distance)) != 0 )[0]
    except:
        #print 'could not find dist_crossovers!'
        return None
        
        
    if len(dist_crossovers) > 0:
        if singleframe:
            return dist_crossovers[-1]+frames[0]
        else:
            return dist_crossovers+frames[0]
    else:
        return None
