class SoloSoft:

    file = None
    plateList = []
    pipeline = []

    def __init__(self, filename=None, plateList=None, pipeline=None):
        # *Open protocol file for editing
        try:
            if filename != None:
                self.setFile(open(filename, "x"))
        except:
            print("Error creating SoloSoft protocol with filename %s" % filename)
        # *Set plate list
        try:
            if plateList != None:
                self.setPlates(plateList)
            else:
                self.setPlates(
                    [
                        "Empty",
                        "Empty",
                        "Empty",
                        "Empty",
                        "Empty",
                        "Empty",
                        "Empty",
                        "Empty",
                    ]
                )
        except:
            print("Error setting Plate List")
        # *Set pipeline, if we're expanding on an existing pipeline
        try:
            if pipeline != None:
                self.setPipeline(pipeline)
        except:
            print("Error setting pipeline")

    def setFile(self, filename):
        self.file = open(filename, "x")

    def setPlates(self, plateList):
        if not isinstance(plateList, list):
            raise TypeError("plateList must be a list of strings.")
        else:
            for plate in plateList:
                if not isinstance(plate, str):
                    raise TypeError("plate must be a string.")

    def setPipeline(self, pipeline):
        if not isinstance(pipeline, list):
            raise TypeError("pipeline should be a list")
        else:
            self.pipeline = pipeline

    def insertStepDelimiter(self):
        self.pipeline.append("!@#$")

    def initializePipeline(self):
        self.setPipeline([self.plateList])

    def removeStep(self, position=None):
        if position != None:
            self.pipeline.remove(position)
        else:
            self.pipeline.pop()

    def getTips(
        self, position="Position1", disposal="TipDisposal", number=8
    ):  # TODO Need to figure out rest of parameters
        properties_list = ["GetTip"]
        properties_list.append(position)
        properties_list.append(disposal)
        properties_list.append(number)
        properties_list.append(1)  # TODO
        properties_list.append(0)  # TODO
        properties_list.append("False")  # TODO
        self.pipeline.append(properties_list)
        self.insertStepDelimiter()

    def startLoop(self, iterations = 1):
        properties_list = ["Loop"]
        properties_list.append(iterations)
        self.pipeline.append(properties_list)
        self.insertStepDelimiter()

    def endLoop(self, iterations = 1):
        properties_list = ["EndLoop"]
        self.pipeline.append(properties_list)
        self.insertStepDelimiter()