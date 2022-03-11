import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import src.data_structures as ds
import matplotlib.pyplot as plt
import pandas as pd
# from  algorithms.sweep_line.sweep_line import SweepLine
from src.algorithms.sweep_line.sweep_line import SweepLine
import unittest
from src.data_types import XmlWrapper
from src.data_structures.lines import Segment 

class TestSweepLine(unittest.TestCase):
    def test_simple_example(self):
        # load the examples
        df = pd.read_csv('data/algo_test/sweep_line/002.csv',index_col=False)
        segments = []
        df_list = df.values.tolist()

        for seg_row in df_list:
            start_point = ds.Point(seg_row[0],seg_row[1])
            end_point = ds.Point(seg_row[2],seg_row[3])
            segments.append(ds.Edge(start_point,end_point)) 

        fig,axs = plt.subplots()

        # for segment in segments:
        #     segment.plot(axs)
        # plt.show()

        sweep_line = SweepLine()
        sweep_line.preprocess(segments)

        print("Starting point:")
        sweep_line.line_status.print()
        sweep_line.event_queue.print()

        for event_point in sweep_line.run_algo():
            print(f"Handled Event point: {event_point}")
            sl_xml = sweep_line.line_status.convert_to_lxml(sweep_line.line_status.root)
            sl_xml.print()
            sweep_line.line_status.print()
            sweep_line.event_queue.print()
            print("\n",end="\n\n")
            self.assertTrue(sweep_line.line_status.check_sanity())

        # The expected results 
        seg_1 = Segment(ds.Point(5,10),ds.Point(5.5,2.5))
        seg_2 = Segment(ds.Point(6,6),ds.Point(5,2))
        inter_point = seg_1.find_intersection_point(seg_2)
        expected_intersections = [{
            "point": inter_point,
            "segments":[seg_2,seg_1]
        }]
        
        #self.assertEqual(expected_intersections,sweep_line.intersections)

    def test_line_status_insert_delete(self):
        df = pd.read_csv('data/algo_test/sweep_line/002.csv',index_col=False)
        segments = []
        df_list = df.values.tolist()
        xml_root = XmlWrapper()

        for seg_row in df_list:
            start_point = ds.Point(seg_row[0],seg_row[1])
            end_point = ds.Point(seg_row[2],seg_row[3])
            segments.append(ds.Edge(start_point,end_point)) 
        
        sweep_line = SweepLine()
        sweep_line.preprocess(segments)
        event_queue = sweep_line.event_queue

        upper_endpoint_segments_0 = sweep_line.upper_endpoint_segments[str(event_queue[0])] 
        sweep_line.insert_to_status(upper_endpoint_segments_0[0])

        upper_endpoint_segments_1 = sweep_line.upper_endpoint_segments[str(event_queue[1])] 
        sweep_line.insert_to_status(upper_endpoint_segments_1[0])


        sl_xml = sweep_line.line_status.convert_to_lxml(sweep_line.line_status.root)
        sl_xml.print()

        segment_on_line = sweep_line.line_status.get_segment_on_line()

        is_equal = xml_root.element == sl_xml.element

        sweep_line.line_status.delete_segment(upper_endpoint_segments_1[0])
        sl_xml = sweep_line.line_status.convert_to_lxml(sweep_line.line_status.root)
        sl_xml.print()
        


if __name__ == "__main__":
    unittest.main()
    # TestSweepLine.test_line_status_insert()
    pass
    