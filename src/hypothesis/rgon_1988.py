from asyncio.windows_events import NULL
from urllib.parse import ParseResultBytes
from ..hypothesis import HypothesisAlgo
import numpy as np
from ..data_structure import Polygon,Point,Edge,Graph
import random

def calc_angle_around_point(center_point,peripheral_point,epsilon = 0.00001):
    '''         |    p
                | 
        ------- c ------
                |
        calculate the angle between cp to the horizontal axis through c
    '''
    return np.degrees(np.arctan((peripheral_point.y-center_point.y)/abs(center_point.x-peripheral_point.x + epsilon)))

def sort_points_clockwise(center_point,subspace_points):
    pos_angles = []
    pos_angle_points = []
    neg_angles = []
    neg_angle_points = []
    # epsilon = 0.00001
    for point in subspace_points: 
        angle = calc_angle_around_point(center_point,point) #np.degrees(np.arctan((point.y- center_point.y)/abs(center_point.x-point.x + epsilon)))

        if angle >0:
            pos_angles.append(angle)
            pos_angle_points.append(point.get_as_tuple())
        else:
            neg_angles.append(-angle)
            neg_angle_points.append(point.get_as_tuple())

    pos_angle_points = [Point(point[0],point[1]) for _,point in sorted(zip(pos_angles,pos_angle_points),reverse=True)]
    neg_angle_points = [Point(point[0],point[1]) for _,point in sorted(zip(neg_angles,neg_angle_points))]
    return pos_angle_points + neg_angle_points

def get_stared_shape_polygon(kernel_point,subspace_points):
    polygon = Polygon()
    polygon.add_vertex(kernel_point)
    [polygon.add_vertex(Point(point.x,point.y)) for point in sort_points_clockwise(kernel_point,
                                                                                    subspace_points)]

    return polygon

def get_points_horizontal_ahead(src_point,space_points,direction="left"):
    '''
        Returns the points that if the source point look at that direction - left/right
        it return the list of point that ahead of it
    '''
    filter_condition = lambda item: item.x>=src_point.x and item!=src_point    
    if direction == "right":
        filter_condition = lambda item: item.x<=src_point.x and item!=src_point    
    
    return list(filter(filter_condition,space_points))



def get_visualization_graph(kernel_point,stared_polygon):
    '''
        This method implement the "Visibility" procedure in the rgon paper

    '''
    copy_polygon = stared_polygon.make_copy()
    copy_polygon.reverse_direction() # This is under the assumption it came from came stared polygon function above
    copy_polygon.remove_vertex(kernel_point)
    points_queues = [[]] * len(copy_polygon.vertcies)
    grph = Graph()

    for index in range(len(copy_polygon.vertcies[:-1])):
        grph,points_queues = get_visualization_graph_proceed(index,index+1,stared_polygon,points_queues,grph)
    
    return grph
    
def turn(_i,_j,_k):
    '''
        The turn method described in the paper:
        Determines wheter point k is in the right or the left of the vector i ot j
    '''
    i_to_j  = _j -_i 
    i_to_k = _k - _i
    determinant = i_to_j.x*i_to_k.y - i_to_k.x*i_to_j.y
    return np.sign(determinant)
    
def get_visualization_graph_proceed(i_index,j_index,stared_polygon,points_queues,grph):
    '''
        This method implement the proceed method in  "Visibility" procedure in the rgon paper
    '''
    

    while len(points_queues[i_index])>0:
        k_index = points_queues[i_index][0]
        _i = stared_polygon.vertcies[i_index]
        _j = stared_polygon.vertcies[j_index]
        _k = stared_polygon.vertcies[k_index]

        if turn(_i,_j,_k) > 0:
            grph,points_queues = get_visualization_graph_proceed(k_index,j_index,
                                                        stared_polygon,points_queues,grph)
            points_queues[i_index].pop(0)
        else:
            break

    grph.insert_edge(Edge(stared_polygon.vertcies[i_index],stared_polygon.vertcies[j_index]))
    points_queues[j_index] =  points_queues[j_index] + [i_index]

    return grph,points_queues


def get_convex_chain_connectivity(visual_graph):
    '''
        This method implements the idea of finding the longest convex chain for an edge

        Assumption - we get the visualizatin graph from the visualizatin method above 
        and the vertecies are sorted clockwise as demanded
    '''
    continuity_edges = {}

    for edge in visual_graph.edges:
        # chain_lengths[str(vertex)] = 0
        continuity_edges[str(edge)] = []
    
    for vertex in visual_graph.vertecies:
        continuity_edges = get_convex_chain_connectivity_treat(vertex,visual_graph,continuity_edges)

    return continuity_edges


def get_convex_chain_connectivity_treat(junction_vertex,visual_graph,continuity_edges):
    '''
        This method implements the treat procedure described in the paper
    '''
    input_edges = visual_graph.get_input_edges(junction_vertex)
    input_edges_vertcies = [edge.src_point for edge in input_edges]
    output_edges = visual_graph.get_output_edges(junction_vertex)
    output_edge_vertcies = [edge.dst_point for edge in output_edges]

    input_edges_vertcies  = sort_points_clockwise(junction_vertex,input_edges_vertcies)
    output_edge_vertcies  = sort_points_clockwise(junction_vertex,output_edge_vertcies)

    for input_vertex in input_edges_vertcies:
        for out_vertex_index in range(len(output_edge_vertcies)-1,-1,-1):

            out_vert = output_edge_vertcies[out_vertex_index] 
            if turn(input_vertex,junction_vertex,out_vert) > 0: # >=0
                src_edge = Edge(junction_vertex,out_vert)
                dst_edge = Edge(input_vertex,junction_vertex)                    
                continuity_edges[str(dst_edge)].append(src_edge)
                    
    return continuity_edges


def get_edges_max_chain_length(visual_graph,continuity_edges):
    '''
        This method implements the procedure for finding the longest convex chain for an edge L_e
    '''
    edges_max_chain_length = {}

    for edge in visual_graph.edges:
        edges_max_chain_length[str(edge)] = 0


    for vertex in visual_graph.vertecies:
        input_edges = visual_graph.get_input_edges(vertex)

        for input_edge in input_edges:
            max_length = max([0] + [edges_max_chain_length[str(out_e)] for out_e in continuity_edges[str(input_edge)]])
            edges_max_chain_length[str(input_edge)] = max_length + 1
    
    return edges_max_chain_length

def create_rgon(kernel_point,r,edges_max_chain_length,continuity_edges):
    rgon = Polygon()
    rgon.add_vertex(kernel_point)
    r = r - 2

    potential_start_edges = list(filter(lambda e: edges_max_chain_length[e] >=r ,edges_max_chain_length.keys()))

    if len(potential_start_edges)==0:
        raise ("Can't create polygon sized " +str(r) + " from point " + str(kernel_point))
    
    next_edge = Edge(random.choice(potential_start_edges))

    while True:
        rgon.add_vertex(next_edge.src_point)
        rgon.add_vertex(next_edge.dst_point)
        r-=1

        if r <= 0:
            break
        
        potential_start_edges = list(filter(lambda e: edges_max_chain_length[str(e)] >=r ,
                                            continuity_edges[str(next_edge)]))
        next_edge = random.choice(potential_start_edges)

    return rgon