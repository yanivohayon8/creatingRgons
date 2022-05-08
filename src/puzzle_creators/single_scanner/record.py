from secrets import choice
from src.puzzle_creators.single_scanner.puzzle_obj import Piece


class Snapshot():
    def __init__(self,kernel_point,puzzle,options) -> None:
        self._kernel_point = kernel_point
        self._puzzle = puzzle
        self._options = options
    
    @property
    def kernel_point(self):
        return self._kernel_point
    
    @property
    def puzzle(self):
        return self._puzzle#[repr(junction)]

    @property
    def options(self):
        return self._options
    
    def __repr__(self) -> str:
        return repr(self.kernel_point) + ";" +  repr(self.puzzle)

    def is_tried_all_paths(self,next_choice_index):
        return next_choice_index >= len(self.options)

class HistoryManager():
    def __init__(self):
        self.choices_history_at_snap = {}

    def is_recorded(self,snap_repr):
        return snap_repr in self.choices_history_at_snap.keys()

    def head_availiable(self,snap_repr):
        if not self.is_recorded(snap_repr):
            self.choices_history_at_snap[snap_repr] = 0
        return self.choices_history_at_snap[snap_repr]

    def next_availiable(self,snap_repr):
        choice = self.head_availiable(snap_repr)
        self.choices_history_at_snap[snap_repr] +=1
        return choice

class Choice():
    def __init__(self,val,is_single=False) -> None:
        if isinstance(val,Piece): # This should be list of pieces
            self.name = val.name
            if is_single:
                self.name = "s"
            self.val = val
        if isinstance(val,str):
            self.name = "p"
            self.val = None
        