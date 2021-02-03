import json


class ExperimentManager:
    # TODO: parameters
    # TODO: logic for well-based, parameter-based, or copy
    def __init__(
        self,
        numberOfCombinations=96,
        numberOfSamples=1,
        parameterList=None,
    ):
        self.setNumberOfCombinations(numberOfCombinations)
        self.setNumberOfSamples(numberOfSamples)

    def setNumberOfCombinations(self, numberOfCombinations):
        if not isinstance(numberOfCombinations, int):
            raise TypeError
        else:
            self.numberOfCombinations = numberOfCombinations
            if self.numberOfSamples != None:
                self.calculateNumberOfWells()

    def setNumberOfSamples(self, numberOfSamples):
        if not isinstance(numberOfSamples, int):
            raise TypeError
        else:
            self.numberOfSamples = numberOfSamples
            if self.numberOfCombinations != None:
                self.calculateNumberOfWells()

    def calculateNumberOfWells(self):
        self.numberOfWells = self.numberOfSamples * self.numberOfCombinations

    # TODO: buildout
    def addExperimentParameter(self):
        pass

    # TODO: buildout
    def deleteExperimentParameter(self):
        pass

    # TODO: buildout
    def calculateParameterSpaceSubdivision(self):
        pass

    # TODO: buildout
    def calculateWellsFromParameterSpace(self):
        pass

    # TODO: buildout
    def generateSoloSoftPipeline(self):
        pass

    # TODO: buildout
    def generateInstructions(self):
        pass

    # TODO: buildout
    def generateSoftLinx(self):
        pass
