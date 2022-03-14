import pandas as pd
from src.data_structures import Point

class PuzzleCreator():
    def __init__(self):
        self.interior_points = []
        self.border_points = []
        self.frame_points = []
    
    def load_sampled_points(self,file_path):
        role_points = {
            "interior":self.interior_points,
            "border":self.border_points,
            "frame":self.frame_points
        }
        df = pd.read_csv(file_path,index_col=False)

        for row in df.to_numpy():
            point = Point(row[0],row[1])
            role_points[row[2]].append(point)

