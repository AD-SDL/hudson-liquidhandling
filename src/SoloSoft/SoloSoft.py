STEP_DELIMITER = "!@#$"

class SoloSoft:

    file = None
    plateList = []
    pipeline = []

    def __init__(self, filename=None, plateList=None, pipeline=None):
        # *Open protocol file for editing
        try:
            if filename != None:
                self.setFile(filename)
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
            else:
                self.initialize_pipeline()
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

    def initializePipeline(self):
        self.setPipeline([self.plateList])

    def removeStep(self, position=-1):
        try:
            self.pipeline.remove(position)
        except:
            print("Error removing step at position %i in pipeline" % position)


    # * SOLOSoft Pipeline Functions

    def getTips(
        self,
        position="Position1",
        disposal="TipDisposal",
        num_tips=8,
        auto_tip_selection=True,
        count_tips_from_last_channel=False,
        index=None,
    ):
        properties_list = ["GetTip"]
        properties_list.append(position)
        properties_list.append(disposal)
        properties_list.append(num_tips)
        if auto_tip_selection:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(
            0
        )  # ? Likely unused, but we'll keep it in for consistency
        properties_list.append(count_tips_from_last_channel)
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)

    def startLoop(self, iterations=-1, index=None):
        properties_list = ["Loop"]
        properties_list.append(iterations) # -1 for continuous loop
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)

    def endLoop(self, index=None):
        properties_list = ["EndLoop"]
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)

    def aspirate(
        self,
        position="Position1",
        aspirate_volume_to_named_point=False,
        aspirate_volume_single=0,
        syringe_speed=100,
        start_by_emptying_syringe=True,
        increment_column_order=False,
        aspirate_point="Position1",
        aspirate_shift=[0, 0, 0],
        do_tip_touch=False,
        tip_touch_shift=[0, 0, 0],
        file_data_path="",
        multiple_wells=1,
        backlash=0,
        pre_aspirate=0,
        mix_at_start=False,
        mix_cycles=0,
        mix_volume=0,
        dispense_height=0,
        delay_after_dispense=0.0,
        aspirate_volumes=None,
        dwell_after_aspirate=0.0,
        find_bottom_of_vessel=False,
        reverse_order=False,
        post_aspirate=0,
        move_while_pipetting=False,
        move_distance=[0, 0, 0],
        index=None
    ):
        properties_list = ["Aspirate"]
        properties_list.append(position)
        properties_list.append(aspirate_volume_single)
        properties_list.append(2)  # ? Mysterious integer value - maybe syringe?
        properties_list.append(syringe_speed)
        if start_by_emptying_syringe:
            properties_list.append(1)
        else:
            properties_list.append(0)
        if aspirate_volume_to_named_point:
            properties_list.append("True")
            properties_list.append("False")
        else:
            properties_list.append("False")
            properties_list.append("True")
        if increment_column_order:
            properties_list.append("True")
            properties_list.append("False")
        else:
            properties_list.append("False")
            properties_list.append("True")
        properties_list.append(aspirate_point)
        properties_list.append(aspirate_shift)
        if do_tip_touch:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(tip_touch_shift)
        properties_list.append(file_data_path)
        properties_list.append(multiple_wells)
        properties_list.append(backlash)
        properties_list.append(pre_aspirate)
        if mix_at_start:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(mix_cycles)
        properties_list.append(mix_volume)
        properties_list.append("a")  # ? Mysterious letter 'a'
        properties_list.append(0)  # ? Mysterious 0/1 integer
        properties_list.append(0)  # ? Mysterious arbitrary integer
        properties_list.append(dispense_height)
        properties_list.append(delay_after_dispense)
        if aspirate_volumes != None:
            properties_list.append(aspirate_volumes)
        else:
            properties_list.append(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            )
        properties_list.append(dwell_after_aspirate)
        if find_bottom_of_vessel:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(5)  # ? Myterious 1 or 2 digit integer
        if reverse_order:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(post_aspirate)
        if move_while_pipetting:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(move_distance)
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)

    def dispense(
        self,
        position="Position1",
        dispense_volume_single=0,
        syringe_speed=100,
        backlash=0,
        dispense_volume_to_named_point=False,
        increment_column_order=False,
        dispense_point="Position1",
        dispense_shift=[0, 0, 0],
        do_tip_touch=False,
        tip_touch_shift=[0, 0, 0],
        file_data_path="",
        multiple_wells=1,
        dwell_after_dispense=0.0,
        blowoff=0,
        mix_at_finish=False,
        mix_cycles=0,
        mix_volume=0,
        aspirate_height=0.0,
        delay_after_aspirate=0.0,
        dispense_volumes=None,
        reverse_order=False,
        move_while_pipetting=False,
        move_distance=[0, 0, 0],
        index=None
    ):
        properties_list = ["Dispense"]
        properties_list.append(position)
        properties_list.append(dispense_volume_single)
        properties_list.append(2)  # ? Mysterious integer value - maybe syringe?
        properties_list.append(syringe_speed)
        properties_list.append(backlash)
        if dispense_volume_to_named_point:
            properties_list.append("True")
            properties_list.append("False")
        else:
            properties_list.append("False")
            properties_list.append("True")
        if increment_column_order:
            properties_list.append("True")
            properties_list.append("False")
        else:
            properties_list.append("False")
            properties_list.append("True")
        properties_list.append(dispense_point)
        properties_list.append(dispense_shift)
        if do_tip_touch:
            properties_list.append(1)
        else:
                properties_list.append(0)
        properties_list.append(tip_touch_shift)
        properties_list.append(file_data_path)
        properties_list.append(multiple_wells)
        properties_list.append(dwell_after_dispense)
        properties_list.append(blowoff)
        if mix_at_finish:
            properties_list.append(1)
        else:
                properties_list.append(0)
        properties_list.append(mix_cycles)
        properties_list.append(mix_volume)
        properties_list.append(
            "a"
        )  # ? Something to do with the uneditable setting 'Valve Port'
        properties_list.append(aspirate_height)
        properties_list.append(delay_after_aspirate)
        if dispense_volumes != None:
            properties_list.append(dispense_volumes)
        else:
            properties_list.append(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            )
        if reverse_order:
            properties_list.append(1)
        else:
                properties_list.append(0)
        if move_while_pipetting:
            properties_list.append(1)
        else:
                properties_list.append(0)
        properties_list.append(move_distance)
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)

    # TODO
    def hitPicking(self):
        return

    # TODO
    def operateAccessory(self):
        return

    # TODO
    def pause(self):
        return

    # TODO
    def getBottom(self):
        return

    # TODO
    def setSpeed(self):
        return

    def moveArm(self, destination='TipDisposal', xyz_speed=100, move_z_at_start=True, index=None):
        properties_list = ["MoveArm"]
        properties_list.append(destination)
        properties_list.append(xyz_speed)
        properties_list.append(move_z_at_start)
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
