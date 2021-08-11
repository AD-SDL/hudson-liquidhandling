import copy
from .Plates import PlateDefinition
from .SoloSoft import SoloSoft


# TODO: Test and bugbash
class CherryPicking:
    def __init__(
        self,
        pickList=None,
        plateList=None,
        filename_prefix=None,
        source_plate_position="Position1",
        source_plate_type=PlateDefinition,
        destination_plate_position="Position2",
        destination_plate_type=PlateDefinition,
    ):
        self.filename_prefix = None
        self.plateList = []
        self.pickList = {}
        self.solosofts = []

        # * Set Filename_prefix
        if filename_prefix != None:
            self.setFilenamePrefix(filename_prefix)
        else:
            self.filename_prefix = "cherryPick_"
        # * Set Plate List
        if plateList != None:
            self.setPlateList(plateList)
        # * Set Pick List
        if pickList != None:
            self.setPickList(pickList)
        self.setSourcePlate(source_plate_position, source_plate_type)
        self.setDestinationPlate(destination_plate_position, destination_plate_type)

    def setFilenamePrefix(self, filename_prefix):
        if isinstance(filename_prefix, str):
            self.filename_prefix = filename_prefix
        else:
            raise TypeError("filename_prefix must be of type str")

    def setPlateList(self, plateList):
        if isinstance(plateList, list):
            if all(isinstance(plate, str) for plate in plateList):
                self.plateList = plateList
                return
        raise TypeError(
            "plateList must be a list of strings corresponding to plate names."
        )

    def setPickList(self, pickList):
        if isinstance(pickList, list):
            # * Is the format [("A1", ("B1", 10)), ("A1", (B2, 5))...]?
            if all(isinstance(pick, tuple) for pick in pickList):
                if all(
                    (
                        self.checkCellFormat(pickTuple[0])
                        and isinstance(pickTuple[1], tuple)
                    )
                    for pickTuple in pickList
                ):
                    if all(
                        (
                            self.checkCellFormat(pickTuple[1][0])
                            and isinstance(pickTuple[1][1], [float, int])
                        )
                        for pickTuple in pickList
                    ):
                        self.pickList = {}
                        for pickTuple in pickList:
                            if pickTuple[0] in self.pickList:
                                self.pickList[pickTuple[0]].append(pickTuple[1])
                            else:
                                self.pickList[pickTuple[0]] = [pickTuple[1]]
                        return
            # * Is the format [["A1", "B1", 10], ["A1", "B2", 5]...]?
            if all(isinstance(pick, list) for pick in pickList):
                if all(
                    (
                        self.checkCellFormat(pick3ple[0])
                        and self.checkCellFormat(pick3ple[1])
                        and isinstance(pick3ple[2], [float, int])
                    )
                    for pick3ple in pickList
                ):
                    self.pickList = {}
                    for pick3ple in pickList:
                        if pick3ple[0] in self.pickList:
                            self.pickList[pick3ple[0]].append(
                                (pick3ple[1], pick3ple[2])
                            )
                        else:
                            self.pickList[pick3ple[0]] = [(pick3ple[1], pick3ple[2])]
                    return
        # * Is the format {"A1": [("B1", 10), ("B2", 5),...],...}?
        elif isinstance(pickList, dict):
            if all(
                self.checkCellFormat(key) and isinstance(pickList[key], list)
                for key in pickList
            ):
                if (
                    all(isinstance(picktuple, tuple) for picktuple in pickList[key])
                    for key in pickList
                ):
                    if all(
                        all(
                            self.checkCellFormat(cell[0])
                            and isinstance(cell[1], (float, int))
                            for cell in pickList[key]
                        )
                        for key in pickList
                    ):
                        self.pickList = pickList
                        return
        return TypeError(
            "pickList must be \n"
            + "1.) a list of tuples of the form [(A1, (B1, 10)), (A1, (B2, 5))...], or\n"
            + "2.) a list of lists of the form [[A1, B1, 10], [A1, B2, 5]...], or\n"
            + '3.) a dictionary mapping source cells to destination cells, of the form {"A1": [(B1, 10), (B2, 5),...],...}.\n'
            + "Where A1 and A2 are source wells, B1 and B2 are destination wells, and 10 and 5 are dispense volumes."
        )

    def setSourcePlate(self, source_plate_position, source_plate_type):
        if isinstance(source_plate_position, str):
            if isinstance(source_plate_type, PlateDefinition) or issubclass(
                source_plate_type, PlateDefinition
            ):
                self.source_plate_position = source_plate_position
                self.source_plate = source_plate_type()
                self.source_plate_type = source_plate_type
                return
        raise TypeError(
            "source_plate_position must be a string corresponding to a named point in SoloSoft, and source_plate_type must be a class inherited from PlateDefinition."
        )

    def setDestinationPlate(self, destination_plate_position, destination_plate_type):
        if isinstance(destination_plate_position, str):
            if isinstance(destination_plate_type, PlateDefinition) or issubclass(
                destination_plate_type, PlateDefinition
            ):
                self.destination_plate_position = destination_plate_position
                self.destination_plate = destination_plate_type()
                self.destination_plate_type = destination_plate_type
                return
        raise TypeError(
            "destination_plate_position must be a string corresponding to a named point in SoloSoft, and destination_plate_type must be a class inherited from PlateDefinition."
        )

    def checkCellFormat(self, cell):
        if isinstance(cell, str):
            if str(cell[0]).isalpha():
                if cell[1:].isdigit():
                    return True
        return False

    def newSolo(self, plateList):
        new_solo = SoloSoft(
            filename=self.filename_prefix + str(len(self.solosofts)) + ".hso",
            plateList=plateList,
            pipeline=[],
        )
        self.solosofts.append(new_solo)
        return new_solo

    def addCherryPickDispense(self, dispense_volumes, current_dispense, dest_tuple):
        dest_well = dest_tuple[0]
        dispense_value = dest_tuple[1]
        dispense_volumes.setCell(dest_well[0], int(dest_well[1:]), dispense_value)
        current_dispense += dispense_value
        return dispense_volumes, current_dispense

    def generateCherryPicking(
        self,
        pickList=None,
        plateList=None,
        tipbox_position="Position1",
        get_tips_between_sources=False,
        max_aspirate=100,
        aspirate_options={},
        dispense_options={},
    ):
        if pickList == None:
            pickList = copy.deepcopy(self.pickList)
        if plateList == None:
            plateList = self.plateList
        if plateList == None or pickList == None:
            raise ValueError(
                "plateList and pickList must be provided before generating the Cherry Picking plan"
            )

        step_count = 0
        self.solosofts = []
        current_solo = self.newSolo(plateList)
        current_solo.getTip(position=tipbox_position, num_tips=1)
        step_count += 1
        for source_well in pickList:
            dest_list = pickList[source_well]
            total_dispense = sum([dest_tuple[1] for dest_tuple in dest_list])
            aspirate_value = 0
            if total_dispense > max_aspirate:
                aspirate_value = max_aspirate
            else:
                aspirate_value = total_dispense
            current_dispense = 0
            current_solo.aspirate(
                position=self.source_plate_position,
                aspirate_volumes=PlateDefinition().setCell(
                    source_well[0], int(source_well[1:]), aspirate_value
                ),
                **aspirate_options
            )
            step_count += 1
            current_aspirate = aspirate_value
            while len(dest_list) > 0:
                if step_count > 60:
                    current_solo = self.newSolo(plateList)
                dispense_volumes = self.destination_plate
                dispense_volumes, current_dispense = self.addCherryPickDispense(
                    dispense_volumes, current_dispense, dest_list.pop(0)
                )
                while (
                    len(dest_list) > 0
                    and dest_list[0][1] + current_dispense < current_aspirate
                ):
                    dispense_volumes, current_dispense = self.addCherryPickDispense(
                        dispense_volumes, current_dispense, dest_list.pop(0)
                    )
                current_solo.dispense(
                    position=self.destination_plate_position,
                    dispense_volumes=dispense_volumes.plate,
                    **dispense_options
                )
                step_count += 1
                if len(dest_list) > 0:
                    if total_dispense - current_dispense > max_aspirate:
                        aspirate_value = max_aspirate - (
                            current_aspirate - current_dispense
                        )
                    else:
                        aspirate_value = total_dispense - current_dispense
                    current_solo.aspirate(
                        position=self.source_plate_position,
                        aspirate_volumes=PlateDefinition().setCell(
                            source_well[0], int(source_well[1:]), aspirate_value
                        ),
                        **aspirate_options
                    )
                    step_count += 1
                    current_aspirate += aspirate_value
            if get_tips_between_sources:
                current_solo.shuckTip()
                current_solo.getTip(position=tipbox_position, num_tips=1)
                step_count += 2
        return self.solosofts
