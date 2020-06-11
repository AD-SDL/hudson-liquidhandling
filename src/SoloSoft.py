import json

STEP_DELIMITER = "!@#$"
SPEC_VERSION = "0.0.1"


class SoloSoft:
    def __init__(self, filename=None, plateList=None, pipeline=None):
        self.file = None
        self.plateList = []
        self.pipeline = []

        # *Open protocol file for editing
        try:
            if filename != None:
                self.setFile(filename)
        except:
            print("Error creating SoloSoft protocol with filename %s" % filename)
            return
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
            return
        # *Set pipeline, if we're expanding on an existing pipeline
        try:
            if pipeline != None:
                self.setPipeline(pipeline)
            else:
                self.initializePipeline()
        except:
            print("Error setting pipeline")

    def setFile(self, filename):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string.")
        else:
            self.file = filename

    def setPlates(self, plateList):
        if not isinstance(plateList, list):
            raise TypeError("plateList must be a list of strings.")
        else:
            self.plateList = plateList

    def setPipeline(self, pipeline):
        if not isinstance(pipeline, list):
            raise TypeError("pipeline should be a list")
        else:
            self.pipeline = pipeline

    def initializePipeline(self):
        self.setPipeline([])

    def removeStep(self, position=-1):
        try:
            self.pipeline.remove(position)
        except:
            print("Error removing step at position %i in pipeline" % position)

    def savePipeline(self, file=None):
        if file == None:
            if self.file != None:
                file = self.file
            else:
                raise BaseException("Need to specify a file to save pipeline")

        with open(file, "w"):
            for plate in self.plateList:
                file.write(str(plate))
                file.write("\n")
            for step in self.pipeline:
                for item in step:
                    if isinstance(item, list):
                        if len(item) > 0 and isinstance(item[0], list):
                            for line in item:
                                for number in line[:-1]:
                                    file.write(str(number))
                                    file.write(",")
                                file.write(str(line[-1]))
                                file.write("\n")
                        else:
                            for number in item:
                                file.write(str(number))
                                file.write("\n")
                    else:
                        file.write(str(item))
                        file.write("\n")

    def pipelineToJSON(self, json_file, pipeline=None, plateList=None):
        if pipeline != None:
            if not isinstance(pipeline, list):
                raise TypeError("pipeline should be a list")
        else:
            pipeline = self.pipeline
        if plateList != None:
            if not isinstance(plateList, list):
                raise TypeError("platelist should be a list")
        else:
            plateList = self.plateList

        json_data = json.dumps({})
        json_data["metadata"] = {"spec_version": SPEC_VERSION}
        json_data["pipeline_type"] = "SoloSoft"
        json_data["platelist"] = plateList
        steps = []
        for step in pipeline:
            step_extraction_function = self.jsonify[step[0]]
            step_data = {}
            step_data["step_definition"] = step_extraction_function(step)
            steps.append(step_data)
        json_data["steps"] = steps
        return json_data

    def jsonToPipeline(self, json_file, pipeline=None):
        print("blah")

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
        properties_list = ["GetTip", position, disposal, num_tips]
        if auto_tip_selection:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend([0, count_tips_from_last_channel, STEP_DELIMITER])
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyGetTips(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "GetTips"
        json_data["position"] = step[1]
        json_data["disposal"] = step[2]
        json_data["num_tips"] = step[3]
        json_data["count_tips_from_last_channel"] = step[5]
        return json_data

    def shuckTips(self, disposal="TipDisposal", index=None):
        properties_list = ["ShuckTip", disposal, STEP_DELIMITER]
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyShuckTips(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "ShuckTips"
        json_data["disposal"] = step[1]
        return json_data

    def startLoop(self, iterations=-1, index=None):
        properties_list = ["Loop", iterations, STEP_DELIMITER]
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyStartLoop(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "StartLoop"
        json_data["iterations"] = step[1]
        return json_data

    def endLoop(self, index=None):
        properties_list = ["EndLoop", STEP_DELIMITER]
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyEndLoop(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "EndLoop"
        return json_data

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
        delay_after_dispense=0,
        aspirate_volumes=None,
        dwell_after_aspirate=0,
        find_bottom_of_vessel=False,
        reverse_order=False,
        post_aspirate=0,
        move_while_pipetting=False,
        move_distance=[0, 0, 0],
        index=None,
    ):
        properties_list = [
            "Aspirate",
            position,
            aspirate_volume_single,
            2,
            syringe_speed,
        ]
        if start_by_emptying_syringe:
            properties_list.append(1)
        else:
            properties_list.append(0)
        if aspirate_volume_to_named_point:
            properties_list.extend(["False", "True"])
        else:
            properties_list.extend(["True", "False"])
        if increment_column_order:
            properties_list.extend(["False", "True"])
        else:
            properties_list.extend(["True", "False"])
        properties_list.extend([aspirate_point, aspirate_shift])
        if do_tip_touch:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend(
            [tip_touch_shift, file_data_path, multiple_wells, backlash, pre_aspirate]
        )
        if mix_at_start:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend(
            [mix_cycles, mix_volume, "a", 0, 0, dispense_height, delay_after_dispense]
        )
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
        properties_list.extend([move_distance, STEP_DELIMITER])
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyAspirate(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "Aspirate"
        json_data["position"] = step[1]
        json_data["aspirate_volume_single"] = step[2]
        json_data["syringe_speed"] = step[4]
        json_data["start_by_emptying_syringe"] = step[5]
        json_data["aspirate_volume_to_named_point"] = step[7]
        json_data["increment_column_order"] = step[9]
        json_data["aspirate_point"] = step[10]
        json_data["aspirate_shift"] = step[11]
        json_data["do_tip_touch"] = step[12]
        json_data["tip_touch_shift"] = step[13]
        json_data["file_data_path"] = step[14]
        json_data["multiple_wells"] = step[15]
        json_data["backlash"] = step[16]
        json_data["pre_aspirate"] = step[17]
        json_data["mix_at_start"] = step[18]
        json_data["mix_cycles"] = step[19]
        json_data["mix_volume"] = step[20]
        json_data["dispense_height"] = step[24]
        json_data["delay_after_dispense"] = step[25]
        json_data["aspirate_volumes"] = step[26]
        json_data["dwell_after_aspirate"] = step[27]
        json_data["find_bottom_of_vessel"] = step[28]
        json_data["reverse_order"] = step[30]
        json_data["post_aspirate"] = step[31]
        json_data["move_while_pipetting"] = step[32]
        json_data["move_distance"] = step[33]
        return json_data

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
        dwell_after_dispense=0,
        blowoff=0,
        mix_at_finish=False,
        mix_cycles=0,
        mix_volume=0,
        dispense_height=0,
        delay_after_aspirate=0,
        dispense_volumes=None,
        reverse_order=False,
        move_while_pipetting=False,
        move_distance=[0, 0, 0],
        index=None,
    ):
        properties_list = [
            "Dispense",
            position,
            dispense_volume_single,
            2,
            syringe_speed,
            backlash,
        ]
        if dispense_volume_to_named_point:
            properties_list.extend(["False", "True"])
        else:
            properties_list.extend(["True", "False"])
        if increment_column_order:
            properties_list.extend(["False", "True"])
        else:
            properties_list.extend(["True", "False"])
        properties_list.extend([dispense_point, dispense_shift])
        if do_tip_touch:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend(
            [
                tip_touch_shift,
                file_data_path,
                multiple_wells,
                dwell_after_dispense,
                blowoff,
            ]
        )
        if mix_at_finish:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend(
            [mix_cycles, mix_volume, "a", dispense_height, delay_after_aspirate]
        )
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
        properties_list.extend([move_distance, STEP_DELIMITER])
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyDispense(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "Dispense"
        json_data["position"] = step[1]
        json_data["dispense_volume_single"] = step[2]
        json_data["syringe_speed"] = step[4]
        json_data["backlash"] = step[5]
        json_data["dispense_volume_to_named_point"] = step[7]
        json_data["increment_column_order"] = step[9]
        json_data["dispense_point"] = step[10]
        json_data["dispense_shift"] = step[11]
        json_data["do_tip_touch"] = step[12]
        json_data["tip_touch_shift"] = step[13]
        json_data["file_data_path"] = step[14]
        json_data["multiple_wells"] = step[15]
        json_data["dwell_after_aspirate"] = step[16]
        json_data["blowoff"] = step[17]
        json_data["mix_at_finish"] = step[18]
        json_data["mix_cycles"] = step[19]
        json_data["mix_volume"] = step[20]
        json_data["dispense_height"] = step[22]
        json_data["delay_after_dispense"] = step[23]
        json_data["dispense_volumes"] = step[24]
        json_data["reverse_order"] = step[25]
        json_data["move_while_pipetting"] = step[26]
        json_data["move_distance"] = step[27]
        return json_data

    def prime(
        self,
        position="Position1",
        syringe_speed=100,
        fill_syringe=False,
        empty_syringe=True,
        aspirate_volume=False,
        dispense_volume=False,
        volume=0,
        index=None,
    ):
        properties_list = [
            "Prime",
            syringe_speed,
            True,  # ? Unclear what this is
            False,  # ? Unclear what this is
            False,  # ? Unclear what this is
            0,  # ? Unclear what this is
            "a",  # ? Unclear what this is
            2,  # ? Unclear what this is
            True,  # ? Unclear what this is
            1,  # ? Unclear what this is
            "*",  # ? Unclear what this is
            volume,
            fill_syringe,
            empty_syringe,
            aspirate_volume,
            dispense_volume,
            "*",
            "*",
            STEP_DELIMITER,
        ]
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyPrime(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "Prime"
        json_data["syringe_speed"] = step[1]
        json_data["volume"] = step[11]
        json_data["fill_syringe"] = step[12]
        json_data["empty_syringe"] = step[13]
        json_data["aspirate_volume"] = step[14]
        json_data["dispense_volume"] = step[15]
        return json_data

    def pause(
        self,
        pause_message="",
        allow_end_run=False,
        auto_continue_after=False,
        wait_seconds=0,
        index=None,
    ):
        properties_list = ["Pause", pause_message]
        if allow_end_run or auto_continue_after:
            properties_list.append(1)
        else:
            properties_list.append(0)
        if auto_continue_after:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.extend([wait_seconds, STEP_DELIMITER])
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyPause(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "Pause"
        json_data["pause_message"] = step[1]
        json_data["allow_end_run"] = step[2]
        json_data["auto_continue_after"] = step[3]
        json_data["wait_seconds"] = step[4]
        return json_data

    def getBottom(
        self,
        position="Position1",
        increment_row_order=True,
        increment_column_order=False,
        output_file_path="",
        wells_per_pass=1,  # * -1 for all
        search_start_distance=0,
        well_list=None,
        index=None,
    ):
        properties_list = [
            "GetBottom",
            position,
            increment_row_order,
            increment_column_order,
            output_file_path,
            wells_per_pass,
            search_start_distance,
            5,  # ? Unclear what this is
            5,  # ? Unclear what this is
            "*",  # ? Unclear what this is
            "*",  # ? Unclear what this is
        ]
        if well_list != None:
            properties_list.append(well_list)
        else:
            properties_list.append(
                [
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                    [
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                    ],
                ]
            )
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyGetBottom(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "GetBottom"
        json_data["position"] = step[1]
        json_data["increment_row_order"] = step[2]
        json_data["increment_column_order"] = step[3]
        json_data["output_file_path"] = step[4]
        json_data["wells_per_pass"] = step[5]
        json_data["search_start_distance"] = step[6]
        json_data["well_list"] = step[11]
        return json_data

    def setSpeed(self, xyz_speed=100, index=None):
        properties_list = ["SetSpeed", xyz_speed, STEP_DELIMITER]
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifySetSpeed(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "GetBottom"
        json_data["xyz_speed"] = step[1]
        return json_data

    def moveArm(
        self, destination="TipDisposal", xyz_speed=100, move_z_at_start=True, index=None
    ):
        properties_list = ["MoveArm", destination, xyz_speed]
        if move_z_at_start:
            properties_list.append(1)
        else:
            properties_list.append(0)
        properties_list.append(STEP_DELIMITER)
        if index != None:
            self.pipeline.insert(index, properties_list)
        else:
            self.pipeline.append(properties_list)
        return properties_list

    def jsonifyMoveArm(self, step):
        json_data = json.dumps({})
        json_data["step_type"] = "GetBottom"
        json_data["destination"] = step[1]
        json_data["xyz_speed"] = step[2]
        json_data["move_z_at_start"] = step[3]
        return json_data

    jsonify = {
        "GetTips": jsonifyGetTips,
        "ShuckTips": jsonifyShuckTips,
        "StartLoop": jsonifyStartLoop,
        "EndLoop": jsonifyEndLoop,
        "Aspirate": jsonifyAspirate,
        "Dispense": jsonifyDispense,
        "GetBottom": jsonifyGetBottom,
        "Prime": jsonifyPrime,
        "SetSpeed": jsonifySetSpeed,
    }
