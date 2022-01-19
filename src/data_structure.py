class Point():
    def __init__(self,x,y):
        self.x = x 
        self.y = y

    def get_as_tuple(self):
        return (self.x,self.y)

    @staticmethod
    def scatter_points(ax,points):
        xs = [point.x for point in points]
        ys = [point.y for point in points]

        ax.scatter(xs,ys)

    def __sub__(self,p):
        if isinstance(p, Point):
            return Point(self.x-p.x,self.y-p.y)

class Edge():
    def __init__(self,src_point,dst_point):
        self.src_point = src_point
        self.dst_point = dst_point
    
    def plot(self,ax):
        ax.plot([self.src_point.x,self.dst_point.x], [self.src_point.y,self.dst_point.y],"o-")

    def plot_directed(self,ax):
        dx = self.dst_point.x - self.src_point.x
        dy = self.dst_point.y - self.src_point.y
        ax.arrow(self.src_point.x,self.src_point.y,dx,dy,head_width=0.2)

class Graph():
    def __init__(self):
        self.edges = set()
        self.vertecies = set()
    
    def insert_vertex(self,vertex):
        self.vertecies.add(vertex)

    def insert_edge(self,edge):
        self.insert_vertex(edge.src_point)
        self.insert_vertex(edge.dst_point)
        self.edges.add(edge)

    def plot_undirected(self,ax):
        for e in self.edges:
            e.plot(ax)
        Point.scatter_points(ax,self.vertecies)

    def plot_directed(self,ax):
        for e in self.edges:
            e.plot_directed(ax)
        Point.scatter_points(ax,self.vertecies)


class Polygon():
    def __init__(self,*args):
        if len(args) == 1:
            self.vertcies = args[0]
        else:
            self.vertcies = []

    def add_vertex(self,point):
        self.vertcies.append(point)

    def plot(self,fig,ax):
        verts = self.vertcies + [self.vertcies[0]]
        ax.plot([p.x for p in verts], [p.y for p in verts])

    def remove_vertex(self,point):
        self.vertcies = list(filter(lambda p: not (p.x==point.x and p.y==point.y),self.vertcies))

    def make_copy(self):
        return Polygon(self.vertcies)
    
    def reverse_direction(self):
        self.vertcies.reverse()