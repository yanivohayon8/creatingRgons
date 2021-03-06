from src.puzzle_creators import rgon_1988_wrap as Rgon1988
from shapely.geometry import LineString
from src.puzzle_creators import Direction
from src.data_structures.graph import Edge
from src.data_structures.shapes import Polygon
from src.data_structures import Point
from src.puzzle_creators.single_scanner import puzzle_obj


def get_accessible_points(kernel_point,pieces,space):
        visible_points = []
        ker_to_p_lines = [LineString([kernel_point,point])for point in space]

        for point,curr_ker_to_p_line in zip(space,ker_to_p_lines):

            # If the kernel, current point and other point forms a line, 
            # the far distant point is not visible
            if any(curr_ker_to_p_line.contains(line) and not line.equals(curr_ker_to_p_line)\
                for line in ker_to_p_lines):
                continue
            
            # if other piece is blocking view to point
            if any((curr_ker_to_p_line.crosses(piece) and not curr_ker_to_p_line.touches(piece) or curr_ker_to_p_line.within(piece))\
                for piece in pieces):
                continue
            
            # If it does visible
            visible_points.append(point)
            x, y = curr_ker_to_p_line.xy

        return visible_points

def get_stared_shaped_polygon(kernel_point,points_to_connect,scan_direction=Direction.left):
    return Rgon1988.get_stared_shape_polygon(kernel_point,points_to_connect,scan_direction)

def _get_surface(kernel_point,pieces,points_to_connect,scan_direction=Direction.left,fig_prefix=""):
        # observe surface data
        # points_to_connect = self._get_points_ahead(kernel_point,direction=scan_direction.value)            
        # points_to_connect = get_accessible_points(kernel_point,pieces,potential_points)            

        if len(points_to_connect) < 2:
            raise ValueError(f"Not enough points to connect ({len(points_to_connect)} < 2)")
        
        stared_polygon = Rgon1988.get_stared_shape_polygon(kernel_point,points_to_connect,scan_direction)
        visual_graph_polygon = Rgon1988.get_visualization_graph(kernel_point,stared_polygon,scan_direction)
        

        # if self.is_debug:
        #     # fig,ax = plt.subplots()
        #     fig,ax = self.fig,self.ax
        #     ax.cla()
        #     self.plot_puzzle(fig,ax)
        #     [Edge(kernel_point,p).plot(ax,color='black', linestyle='dotted') for p in list(visual_graph_polygon.get_verticies())]
        #     visual_graph_polygon.plot_directed(ax) # way to plot the graph
        #     fig.savefig(self.debug_dir + f"/visibility-graph-before-filter/{fig_prefix}{str(self.n_iter)}.png")
        #     # plt.close(fig)

        # Remove edges that are covered by polygons - do it more elegant less naive
        vs_grph_edges = list(visual_graph_polygon.get_edges()).copy()
        lines =  [LineString([edge.src_point,edge.dst_point]) for edge in vs_grph_edges]

        for edge,line in zip(vs_grph_edges,lines):
            for piece in pieces:
                
                if line.crosses(piece) and not line.touches(piece):
                    visual_graph_polygon.remove_edge(edge)
                    break

                if line.within(piece):
                    visual_graph_polygon.remove_edge(edge)
                    break
        
        # if self.is_debug:
        #     # fig,ax = plt.subplots()
        #     fig,ax = self.fig,self.ax
        #     ax.cla()
        #     self.plot_puzzle(fig,ax)
        #     [Edge(kernel_point,p).plot(ax,color='black', linestyle='dotted') for p in list(visual_graph_polygon.get_verticies())]
        #     visual_graph_polygon.plot_directed(ax) # way to plot the graph
        #     fig.savefig(self.debug_dir + f"/visibility-graph-filtered/{fig_prefix}{str(self.n_iter)}.png")
        #     # plt.close(fig)

        if len(list(visual_graph_polygon.get_edges())) == 0:
            raise ValueError("Not enough edge to iterate on the visibility graph")

        return Rgon1988.get_convex_chain_connectivity(visual_graph_polygon,scan_direction)



def _find_rgons_comb(kernel_point,continuity_edges,puzzle):
    rgons = []

    for edge_str in list(continuity_edges.keys()):
        traverses = [list(dict.fromkeys(tr)) for tr in _get_traverse(Edge(edge_str),continuity_edges)]
        # find all sequential sub combinations:
        for trav in traverses:
            for index_start in range(len(trav)):
                for index_end in range(index_start+1,len(trav)):
                    sub_trav = trav[index_start:index_end+1]
                    sub_trav.insert(0,str(kernel_point))
                    poly = Polygon([Point(eval(point_str)) for point_str in sub_trav])

                    try:
                        puzzle.check_sanity_polygon(poly)
                        rgons.append(poly)
                    except puzzle_obj.PuzzleErr as err:
                        pass
    
    # Remove duplicates
    final_rgons = []
    for rgon in rgons:
        if all(not rgon.equals(poly) for poly in final_rgons):
                final_rgons.append(rgon)
        
    # sorting by the most left point of the polygon without kernel (ease on debug)
    def left_most_point_x(poly):
        xs,ys = poly.exterior.coords.xy
        return min(xs[1:-1])

    final_rgons.sort(key = left_most_point_x )
    
    return final_rgons

def _get_traverse(origin_edge,continuity_edges):
    if len(continuity_edges[str(origin_edge)]) == 0:
        return [[str(origin_edge.src_point),str(origin_edge.dst_point)]]

    travs = []
    available_edges = continuity_edges[str(origin_edge)]
    for next_edge in available_edges:
        cont_travs = _get_traverse(next_edge,continuity_edges)

        if isinstance(cont_travs[0],list):
            flat_travs = [item for sublist in cont_travs for item in sublist]
            flat_travs.insert(0,str(origin_edge.dst_point))
            flat_travs.insert(0,str(origin_edge.src_point))

        travs.append(flat_travs)
    
    return travs


def find_possible_rgons(kernel_point,puzzle,points_to_connect,scan_direction=Direction.left):
        polygons = puzzle.polygons
        try:
            continuity_edges = _get_surface(kernel_point,polygons,points_to_connect,scan_direction)
        except ValueError as err:
            return []

        possible_rgons = _find_rgons_comb(kernel_point,continuity_edges,puzzle)
        possible_rgons = list(filter(lambda pc:all(pc.disjoint(pc2) or pc.touches(pc2) for pc2 in polygons),possible_rgons))

        # n = len(possible_rgons)
        # pieces = [puzzle_obj.Piece(poly,f"{index+1}-{n}") for index,poly in enumerate(possible_rgons)]
        # pieces = [puzzle_obj.Piece(poly,repr(poly)) for index,poly in enumerate(possible_rgons)]
        return possible_rgons