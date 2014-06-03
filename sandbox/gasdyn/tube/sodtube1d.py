#!/usr/bin/python
#
# 1D Sod Tube Test
#

class PlotManager():
    """
    Manage how to show the data generated by SodTube.
    Roughly speaking, it is a wrapper of matplotlib
    """
    def __init__(self):
        pass

    def plotMesh(self, mesh):
        pass

    def plotSolution(self, solution):
        pass

class DataManager(PlotManager):
    """
    Manage how to get extended information by input data.
    """
    def __init__(self):
        pass

    def getErrorNorm(self, solution_A, solution_B):
        return solution_errornorm

    def getL2Norm(self, solution_A, solution_B):
        return solution_errornorm

class SodTube():
    """
    The core to generate the 1D Sod tube test
    """
    def __init__(self):
        # initial condition
        # [(xl, rhol, ul, pl), (xr, rhor, ur, pr)]
        #
        # Sod's initial condition
        self.initcondition_sod = [(1.0, 0.0, 1.0), (0.125, 0.0, 1.0)]
        # initial condition for a shock tube problem
        # default is Sod's initial condition
        # users could change this initial conditions
        self.initcondition = self.initcondition_sod
        # a mesh, which has this format:
        # [point0, point1, point2, point3, ......, pointn]
        self.mesh = []
        # solution has this format:
        # [(x0, rho0, u0, p0),
        #  (x1, rho1, u1, p1),
        #  ......,
        #  (xn, rhon, un, pn)]
        self.solution = []
        self.ceseparameters = []

    def getInitcondition(self):
        return self.initcondition

    def setInitcondition(self, initcondition):
        self.initcondition = initcondition

    def getMesh(self):
        return self.mesh

    def getAnalyticSolution(self):
        return self.calAnalyticSolution()

    def calAnalyticSolution(self, initcondition=self.initcondition):
        # where implementing the code to get the analytic solution
        # by users' input condition
        # default is the Sod's condition
        solution = []
        return solution

    def getCESESolution(self):
        return self.solution

    def calCESESolution(self, initcondition, mesh, ceseparameters):
        return self.solution

