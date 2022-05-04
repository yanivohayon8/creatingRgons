
# from data_structures.shapes import Polygon
from functools import reduce
from random import random
from src.data_structures.shapes import Polygon
from src.puzzle_creators.power_group import HistoryManager,Snapshot
from src.puzzle_creators import Junction
from src.puzzle_creators.skeleton import PuzzleCreator
from matplotlib import pyplot as plt
import os
import logging
from src import setup_logger

import random

# log_handler = setup_logger.get_file_handler(setup_logger.get_debug_log_file())
# logger = logging.getLogger("logger.power_group")
# logger.addHandler(log_handler)

# import time

class PowerGroupCreator(PuzzleCreator):
    
    def __init__(self,output_dir,is_debug=False):
        super().__init__(is_debug=is_debug)
        self.snapshot_queue = [] #[]
        self.output_dir = output_dir
        self.history_manager = HistoryManager()
        self.puzzles = []
        self.puzzles_hashes = []
        self.puzzles_size = []
        self.is_passed_at = {}
        self.number_duplicates = 0
        self.puzzle_name = ""
    
    def _create_rgon(self, possible_rgons):

        if len(possible_rgons) == 0:
            self.logger.debug("It seems no rgon is availiable")

            _key = f"from {self.scan_direction.name} at "+str(self.last_kernel_point)
            if not self.is_passed_at[_key]:
                self.logger.debug("Choose to pass rgon creation at this point")
                return "pass_option"

            self.logger.debug(f"No option availiable for creating rgon at n_iter: {self.n_iter}")
            return None

        next_poly = possible_rgons[0] #random.choice(possible_rgons)
        
        return next_poly

    def prepare_to_create(self,kernel_point):
        self.logger.info(f"n_iter: {str(self.n_iter)}. Next point potential to origin a polygon is {str(kernel_point)}")
        
        # snap = self.get_fit_snapshot(kernel_point)

        _key = f"from {self.scan_direction.name} at "+str(kernel_point)
        # _key = 
        # is_exist_snap = any(_key == repr(snap.junction) for snap in self.snapshot_queue)
        # if is_exist_snap:
        #     self.logger.info(f"The junction {_key} already has snapshot")
        #     pass

        if _key not in self.last_possible_rgons.keys(): 
            self.logger.info("No prior surface scanning at this point and direction, searching for possible polygons.")
            self.last_possible_rgons[_key] = self._find_first_possible_rgons(kernel_point,self.n_iter)
            self.is_passed_at[_key] = False

            if len(self.last_possible_rgons[_key]) > 1:
                snapshot = Snapshot(Junction(kernel_point,self.scan_direction),dict(self.last_possible_rgons),
                                    self.pieces.copy(),self.pieces_area,dict(self.is_passed_at),self.puzzle_name)
                self.logger.info(f"Take a snapshot (id:{str(snapshot.id)}) of the board")
                
                if self.is_debug:
                    fig,axs = plt.subplots(1,2,sharey=True)
                    self.plot_puzzle(fig,axs[0],snapshot.pieces)
                    axs[0].set_title("Puzzle")
                    self.plot_puzzle(fig,axs[1],self.last_possible_rgons[_key])
                    axs[1].set_title("Possibilities")
                    fig.suptitle(f'Snapshot {repr(snapshot)}, n_puzzle to create: {str(self.n_puzzle)}')
                    fig.savefig(self.output_dir+f"/snapshots/{str(snapshot.id)}.png")
                    plt.close(fig)
                self.snapshot_queue.append(snapshot)
            
            return self.last_possible_rgons[_key]        
        else:
            self.logger.info("Prior surface scanning at this point and direction Found, filter possible rgons with the surface current status")
            self.last_possible_rgons[_key] =  self._filter_poss_rgons(self.last_possible_rgons[_key])
            return self.last_possible_rgons[_key]
            # if len(self.last_possible_rgons[_key]) > 0:
            #     return self.last_possible_rgons[_key]

            # else:
            #     exist_snap_id = None
            #     for snap in self.snapshot_queue[::-1]:
            #         if _key == repr(snap.junction):
            #             exist_snap_id = repr(snap)
            #             break
                
            #     # made a floop from the creation of the snapshot till itself - maybe we had to choose 
            #     # more than one at on of the creation so restore from it
            #     if exist_snap_id is not None:
            #         self.logger.info(f"{_key} we need to create polygon again and all the possiblities are done. restore from history(maybe we had to choose more than one at creation point)")
            #         history = [poly for poly in self.history_manager.get_history(exist_snap_id) if isinstance(poly,Polygon)]
            #         return self._filter_poss_rgons(history)
            #     else:
            #         self.logger.error("I can't believe I am here")
            #         return []


    def after_rgon_creation(self, polygon):
        super().after_rgon_creation(polygon)
        if isinstance(polygon,Polygon) or isinstance(polygon,str):
            
            junction = Junction(self.last_kernel_point, self.scan_direction)
            self.history_manager.add(junction,self.snapshot_queue,polygon)
            postfix = ""
            if isinstance(polygon,str):
                choise_name = "p"
            else:
                choise_name = "s"
                postfix = ""
                for index in range(len(self.snapshot_queue) - 1,-1,-1):      
                    snap_id = repr(self.snapshot_queue[index])
                    # Find the corresponding latest snapshot at queue
                    if repr(junction) in repr(snap_id):
                        poss_rgon_at_create = self.snapshot_queue[index].possible_rgon_at[repr(junction)]            
                        if isinstance(polygon,Polygon):
                            poly_index = poss_rgon_at_create.index(polygon)
                            choise_name = f"{poly_index+1}"
                        
                        postfix = f"-{len(poss_rgon_at_create)}"
                    
                        break
            
            self.puzzle_name = self.puzzle_name + f"{choise_name}{postfix}_"


            # self.num_iter_no_new_piece+=1
            self.num_iter_no_new_piece = 0

            if self.is_debug:
                # fig,ax = plt.subplots()
                fig,ax = self.fig,self.ax
                ax.cla()
                self.plot_puzzle(fig,ax)

                extra_str = ""
                if isinstance(polygon,str):
                    extra_str = " passed creation"
                    self.is_passed_at[repr(junction)] = True

                
                fig.suptitle(f'At {str(self.last_kernel_point)}-from {str(self.scan_direction.name)}' + extra_str)
                fig.savefig(self.output_dir+f"/last_creation/{self.n_puzzle}_{self.n_iter}.png") 
                fig.suptitle("")
                # plt.close(fig)
        else:
            self.num_iter_no_new_piece+=1



    def create_puzzles(self):
        self.n_puzzle = 1
        
        while True:
            try:
                
                super().create()
                self.logger.info("Finish to assemble puzzle - check if it is equal to previous puzzle (recursive algo duplicates)")
                
                is_duplicated = False
                curr_puzzle_hash = reduce(lambda acc,rgon_hash: acc+rgon_hash,[hash(piece) for piece in self.pieces])
                count_pieces = len(self.pieces)

                for exist_puzzle,(puzzle_size,puzzle_hash) in zip(self.puzzles,zip(self.puzzles_size,self.puzzles_hashes)):
                    if puzzle_size != count_pieces:
                        continue

                    # if puzzle_hash==curr_puzzle_hash:
                    if all(any(curr_puzzle_piece.equals(exist_puzz_piece) for curr_puzzle_piece in self.pieces) for exist_puzz_piece in exist_puzzle):
                        is_duplicated = True
                        break
                
                

                # if not any(all(any(curr_puzzle_piece.equals(exist_puzz_piece) for curr_puzzle_piece in self.pieces) for exist_puzz_piece in exist_puzzle) for exist_puzzle in self.puzzles):
                if not is_duplicated:
                    new_puzzle = []
                    for piece in self.pieces:
                        deep_copy_poly = Polygon(piece.exterior.coords)
                        new_puzzle.append(deep_copy_poly)

                    self.puzzles.append(new_puzzle)
                    self.logger.info("Finish to assemble a puzzle number:" + str(self.n_puzzle) +". save to file")
                    self.write_results(self.output_dir+f"/results/{str(self.puzzle_name)}.csv")
                    self.plot_results(self.output_dir+f"/results/{str(self.puzzle_name)}.png")
                    self.puzzles_hashes.append(curr_puzzle_hash)
                    self.puzzles_size.append(count_pieces)
                    
                # else:
                    # self.number_duplicates +=1
                    # self.logger.info(f"already created this puzlle. Number of duplicate so far is {self.number_duplicates}")
            except StopIteration as err:
                pass
                # identifier = random.randint(0,1000)
                # self.logger.error(f"Failed to create a puzzle. identifier: {identifier}. Started {repr(self.snapshot_queue[-1])}")
                # self.plot_results(self.output_dir+f"/failure/{str(self.n_puzzle)}_identifier_{identifier}.png")
                ## curr_snapshot = self.snapshot_queue[-1]
                ## self.last_possible_rgons[repr(curr_snapshot.junction)] = self.history_manager.snap_poss_sub_history(curr_snapshot)
            self.n_puzzle+=1

            while len(self.snapshot_queue) > 0:
                last_snap = self.snapshot_queue[-1]
                choices_history = self.history_manager.choices_history_at_snap[repr(last_snap)]

                if not last_snap.is_tried_all_paths(choices_history) and not last_snap in self.history_manager.passed_snapshots:
                    self.logger.info(f"Did not traversed on all snapshot possibilities at {repr(last_snap)} - preparing to try different rgon options")
                    break

                self.snapshot_queue.pop()

            if len(self.snapshot_queue) == 0:
                self.logger.info("Finish to create all puzzles")
                break
        
            self.revert(last_snap)
            
            if self.is_debug:
                self.logger.info("Plot the current state of the puzzle, and the previous choices hatched")
                fig_path = self.output_dir+f"/last_decision_junction/After puzzle {str(self.n_puzzle-1)} creation.png"
                fig1,axs = plt.subplots(1,3,sharey=True)
                self.plot_puzzle(fig1,axs[0])
                axs[0].set_title("The Puzzle")
                self.plot_puzzle(fig1,axs[1],self.history_manager.choices_history_at_snap[repr(last_snap)],hatch='\\/...')
                axs[1].set_title("Choises History")
                self.plot_puzzle(fig1,axs[2],self.last_possible_rgons[repr(last_snap.junction)])
                axs[2].set_title("Possiblities, passing is optional: " + str(last_snap in self.history_manager.passed_snapshots))

                fig1.suptitle(f'Snapshot at {str(last_snap.junction.kernel_point)}-from {str(last_snap.junction.from_direction)}')
                fig1.autofmt_xdate()
                fig1.savefig(fig_path)
                # plt.close("all")    
                # sleep_sec = 6
                # self.logger.info(f"Sleep for {str(sleep_sec)} seconds, waiting for figures to close")
                # plt.pause(4)
                plt.pause(2)
                plt.close(fig1)
                self.logger.info(f"Let's go back to work")

            # for file in os.scandir(os.path.join(self.output_dir,"last_creation")):
            #     os.remove(file.path) 
        

    def revert(self,snapshot:Snapshot):
        self.logger.debug(f"Revert to decision junction where direction is from {snapshot.junction.from_direction.name}, kernel_point is {str(snapshot.junction.kernel_point)}")
        self._set_direction_scan(snapshot.junction.from_direction.value)
        kernel_index = self.space_points.index(snapshot.junction.kernel_point)
        self.space_points = self.space_points[kernel_index:]
        self.scan_direction = snapshot.junction.from_direction
        self.last_possible_rgons = {} #snapshot.possible_rgon_at.copy()
        # updated_junc_pieces = []
        # junction_history = self.history_manager.choices_history_at_snap[repr(snapshot)]
        # for rgon in snapshot.possible_rgon_at[repr(snapshot.junction)]:
        #     if not any(rgon.equals(piece) for piece in junction_history):
        #         updated_junc_pieces.append(rgon)
        # self.last_possible_rgons[repr(snapshot.junction)] = updated_junc_pieces
        self.last_possible_rgons[repr(snapshot.junction)] = self.history_manager.snap_poss_sub_history(snapshot)
        
        self.pieces = list(snapshot.pieces)
        self.pieces_area = snapshot.pieces_area
        self.is_passed_at = snapshot.is_passed_at
        self.puzzle_name = snapshot.puzzle_name


    def _get_surface(self, kernel_point, scan_direction, n_iter=-1):
        return super()._get_surface(kernel_point, scan_direction, n_iter, fig_prefix=f"{str(self.n_puzzle)}_")




