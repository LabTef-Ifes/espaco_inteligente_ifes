from collections import defaultdict, OrderedDict

from is_msgs.image_pb2 import ObjectAnnotations
from is_msgs.image_pb2 import HumanKeypoints as HKP
from google.protobuf.json_format import ParseDict
from itertools import permutations
import numpy as np

class SkeletonsCoord:
    def joint_coord(skeletons, coord):
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        for skeleton in skeletons_pb.objects:
            parts = ()
            for part in skeleton.keypoints:
                if part.id == coord:
                    parts = (part.position.x, part.position.y, part.position.z)
            if parts:
                return parts
            else:
                message = "Joint {} not found".format(coord)
                return None
            break
    
    def avg_height_ankle(skeletons):
        right_ankle, left_ankle, ankle_height = None, None, None

        skeletons_pb = ParseDict( skeletons, ObjectAnnotations())
        for skeletons in skeletons_pb.objects:
            parts = {}
            for part in skeletons.keypoints:
                parts[part.id]=(part.position.x,part.position.y,part.position.z)
                if part.id == 12:
                    right_ankle = parts[12]
                if part.id == 15:
                    left_ankle = parts[15]

            if right_ankle and left_ankle:
                ankle_height = (left_ankle[2]+right_ankle[2])/2
                return ankle_height
            else:
                ankle_height = None
                return ankle_height
            break
    
    def avg_mid_hip(skeletons):
        right_hip = None
        left_hip = None
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        for skeleton in skeletons_pb.objects:
            parts = {}
            for part in skeleton.keypoints:
                parts[part.id] = (part.position.x, part.position.y, part.position.z)
                if part.id == 10:
                    right_hip = parts[10]
                if part.id == 13:
                    left_hip = parts[13]

            if right_hip and left_hip:
                mid_hip = ((right_hip[0] + left_hip[0]) / 2, (right_hip[1] + left_hip[1]) / 2, (right_hip[2] + left_hip[2]) / 2) 
                return mid_hip
            else:
                mid_hip = None
                return mid_hip
            break
        
    def avg_limb_length(skeletons, links):
        right_femur, right_shin, left_femur, left_shin = None, None, None, None
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        for skeleton in skeletons_pb.objects:
            parts = {}
            for part in skeleton.keypoints:
                parts[part.id] = (part.position.x, part.position.y, part.position.z)
            for link_parts in links:
                begin, end = link_parts
                if begin in parts and end in parts:
                    x_pair = [parts[begin][0], parts[end][0]]
                    y_pair = [parts[begin][1], parts[end][1]]
                    z_pair = [parts[begin][2], parts[end][2]]
                    if begin == 10 and end == 11:
                        right_femur = np.sqrt((x_pair[1] - x_pair[0])**2 + (y_pair[1] - y_pair[0])**2 + (z_pair[1] - z_pair[0])**2)
                    if begin == 11 and end == 12:
                        right_shin = np.sqrt((x_pair[1] - x_pair[0])**2 + (y_pair[1] - y_pair[0])**2 + (z_pair[1] - z_pair[0])**2)
                    if begin == 13 and end == 14:
                        left_femur = np.sqrt((x_pair[1] - x_pair[0])**2 + (y_pair[1] - y_pair[0])**2 + (z_pair[1] - z_pair[0])**2)
                    if begin == 14 and end == 15:
                        left_shin = np.sqrt((x_pair[1] - x_pair[0])**2 + (y_pair[1] - y_pair[0])**2 + (z_pair[1] - z_pair[0])**2)
                
            if right_femur and right_shin:
                right_leg = right_shin + right_femur
            else:
                right_leg = None
            if left_femur and left_shin:
                left_leg = left_shin + left_femur
            else:
                left_leg = None
            
            if right_leg and left_leg:
                avg_leg_size = (right_leg + left_leg) / 2
                return avg_leg_size
            else:
                return None
            break

    
