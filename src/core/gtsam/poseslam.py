import gtsam

'''
This module provides a class for optimizing an SE(2) PoseSLAM problem using GTSAM.
It uses a nonlinear factor graph and Levenberg-Marquardt optimization.
for better real-time performance, it uses the ISAM2 algorithm for incremental optimization.
'''
class PoseSLAMOptimizer:
    def __init__(self):
        """
        Initialize the PoseSLAMOptimizer with a factor graph and an initial estimate.

        :param graph: gtsam.NonlinearFactorGraph, the factor graph to optimize
        :param initial_estimate: gtsam.Values, the initial estimate of the variables
        """
        self.isamParams = gtsam.ISAM2Params()
        self.isam = gtsam.ISAM2(self.isamParams)
        self.graph = gtsam.NonlinearFactorGraph()
        self.initial_estimate = gtsam.Values()
    
        
