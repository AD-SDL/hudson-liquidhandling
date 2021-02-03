import sys
import os
import pytest
from liquidhandling import SoloSoft


class TestSoloSoft:

    example_pipeline = [
        ["GetTip", "Position1", "TipDisposal", 8, 1, 0, False, "!@#$"],
        ["Loop", 1, "!@#$"],
        [
            "Aspirate",
            "Position1",
            0,
            2,
            100,
            1,
            True,
            False,
            True,
            False,
            "Position1",
            [0, 0, 0],
            0,
            [0, 0, 0],
            "",
            1,
            0,
            0,
            0,
            0,
            0,
            "a",
            0,
            0,
            0,
            0,
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            0,
            0,
            5,
            0,
            0,
            0,
            [0, 0, 0],
            "!@#$",
        ],
        [
            "Dispense",
            "Position1",
            0,
            2,
            100,
            0,
            True,
            False,
            True,
            False,
            "Position1",
            [0, 0, 0],
            0,
            [0, 0, 0],
            "",
            1,
            0,
            0,
            0,
            0,
            0,
            "a",
            0,
            0,
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            0,
            0,
            [0, 0, 0],
            "!@#$",
        ],
        ["EndLoop", "!@#$"],
        ["MoveArm", "TipDisposal", 100, 1, "!@#$"],
    ]

    example_platelist = [
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
    ]

    def test_empty(self):
        soloSoft = SoloSoft.SoloSoft()
        assert soloSoft.filename == None
        assert soloSoft.pipeline == []
        assert soloSoft.plateList == [
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
        ]

    def test_filename(self):
        soloSoft = SoloSoft.SoloSoft("example_filename.hso")
        assert soloSoft.filename == "example_filename.hso"
        soloSoft.setFile("new_filename.hso")
        assert soloSoft.filename == "new_filename.hso"
        with pytest.raises(TypeError):
            soloSoft.setFile(1)
        soloSoft.filename = "once_more.hso"
        assert soloSoft.filename == "once_more.hso"

    def test_pipeline(self):
        soloSoft = SoloSoft.SoloSoft(pipeline=self.example_pipeline)
        assert soloSoft.pipeline == self.example_pipeline
        soloSoft.setPipeline([])
        assert soloSoft.pipeline == []
        soloSoft.setPipeline(self.example_pipeline)
        assert soloSoft.pipeline == self.example_pipeline
        soloSoft.pipeline = []
        assert soloSoft.pipeline == []
        soloSoft.pipeline = self.example_pipeline
        assert soloSoft.pipeline == self.example_pipeline
        with pytest.raises(TypeError):
            soloSoft.setPipeline(3)

    def test_plates(self):
        soloSoft = SoloSoft.SoloSoft(plateList=self.example_platelist)
        assert soloSoft.plateList == self.example_platelist
        soloSoft.setPlates([])
        assert soloSoft.plateList == []
        soloSoft.setPlates(self.example_platelist)
        assert soloSoft.plateList == self.example_platelist
        soloSoft.plateList = []
        assert soloSoft.plateList == []
        soloSoft.plateList = self.example_platelist
        assert soloSoft.plateList == self.example_platelist
        with pytest.raises(TypeError):
            soloSoft.setPlates(3)
