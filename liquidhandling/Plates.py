import string


class PlateDefinition:
    def __init__(
        self,
        name="Custom Defined Plate",
        plate=None,
        plate_height=0,
        well_depth=0,
        rows=8,
        columns=12,
        x_offset=0,
        y_offset=0,
        row_spacing=9,
        column_spacing=9,
        comments="",
    ):
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError("Plate name must be a string.")
        if isinstance(plate_height, (int, float)) and plate_height >= 0:
            self.plate_height = plate_height
        else:
            raise ValueError("Plate Height must be a positive numeric value.")
        if isinstance(well_depth, (int, float)) and well_depth >= 0:
            self.well_depth = well_depth
        else:
            raise ValueError("Well depth must be a positive numeric value.")
        if isinstance(rows, int) and rows > 0:
            self.rows = rows
        else:
            raise ValueError("Rows must be a positive integer.")
        if isinstance(columns, int) and columns > 0:
            self.columns = columns
        else:
            raise ValueError("Columns must be a positive integer.")
        if isinstance(x_offset, (int, float)):
            self.x_offset = x_offset
        else:
            raise ValueError("X_offset must be a numeric value")
        if isinstance(y_offset, (int, float)):
            self.y_offset = y_offset
        else:
            raise ValueError("Y_offset must be a numeric value")
        if isinstance(row_spacing, (int, float)) and row_spacing > 0:
            self.row_spacing = row_spacing
        else:
            raise ValueError("Row Spacing must be a positive numeric value")
        if isinstance(column_spacing, (int, float)) and column_spacing > 0:
            self.column_spacing = column_spacing
        else:
            raise ValueError("Column Spacing must be a positive numeric value")
        if plate == None:
            self.plate = [[0 for j in range(self.columns)] for i in range(self.rows)]
        else:
            self.plate == plate
        self.comments = comments

    def setRow(self, row="A", value=0):
        alpha_vals = list(string.ascii_uppercase)
        if str.upper(row) in alpha_vals[0 : self.rows]:
            index = alpha_vals.index(str.upper(row))
            if float(value) >= 0:
                for i in range(self.columns):
                    self.plate[index][i] = value
            else:
                raise ValueError(
                    "value must be a non-negative number, not " + str(value)
                )
        elif row in range(1, self.rows + 1):
            if float(value) >= 0:
                for i in range(self.columns):
                    self.plate[row - 1][i] = value
            else:
                raise ValueError(
                    "value must be a non-negative number, not " + str(value)
                )
        else:
            raise ValueError(
                "row must be a character in the range A-H, or a number 1-8, not "
                + str(row)
            )
        return self.plate

    def setColumn(self, column=1, value=0):
        if column in range(1, self.columns + 1):
            if float(value) >= 0:
                for row in range(self.rows):
                    self.plate[row][column - 1] = value
            else:
                raise ValueError(
                    "value must be a non-negative number, not " + str(value)
                )
        else:
            raise ValueError(
                "column must be a number in the range 1-12 inclusive, not "
                + str(column)
            )
        return self.plate

    def setAll(self, value=0):
        if float(value) >= 0:
            for row in range(self.rows):
                for column in range(self.columns):
                    self.plate[row][column] = value
        else:
            raise ValueError("value must be a non-negative number, not " + str(value))
            return
        return self.plate

    def setCell(self, row="A", column=1, value=0):
        alpha_vals = list(string.ascii_uppercase)
        if not (column in range(1, self.columns + 1)):
            raise ValueError(
                "column must be a number in the range 1-12 inclusive, not "
                + str(column)
            )
        if str.upper(row) in alpha_vals[0 : self.rows]:
            index = alpha_vals.index(str.upper(row))
            if float(value) >= 0:
                self.plate[index][column - 1] = value
            else:
                raise ValueError(
                    "value must be a non-negative number, not " + str(value)
                )
        elif row in range(1, self.rows + 1):
            if float(value) >= 0:
                self.plate[row - 1][column - 1] = value
            else:
                raise ValueError("value must be a non-negative number")
        else:
            raise ValueError(
                "row must be a character in the range A-H, or a number 1-8"
            )
        return self.plate

    def setColumnAlternating(self, column=1, value=0, offset=0):
        if not (offset == 0 or offset == 1):
            raise ValueError("Offset must be either 0 or 1")
        if column in range(1, self.columns + 1):
            if float(value) >= 0:
                for row in range(self.rows, step=2):
                    self.plate[row + offset][column - 1] = value
            else:
                raise ValueError("value must be a non-negative number")
        else:
            raise ValueError("column must be a number in the range 1-12 inclusive")
        return self.plate

    def setRowAlternating(self, row="A", value=0, offset=0):
        if not (offset == 0 or offset == 1):
            raise ValueError("Offset must be either 0 or 1")
        alpha_vals = list(string.ascii_uppercase)
        if str.upper(row) in alpha_vals[0 : self.rows]:
            index = alpha_vals.index(str.upper(row))
            if float(value) >= 0:
                for i in range(self.columns, step=2):
                    self.plate[index][i + offset] = value
            else:
                raise ValueError("value must be a non-negative number")
        elif row in range(1, self.rows + 1):
            if float(value) >= 0:
                for i in range(self.columns, step=2):
                    self.plate[row - 1][i + offset] = value
            else:
                raise ValueError("value must be a non-negative number")
        else:
            raise ValueError(
                "row must be a character in the range A-H, or a number 1-8"
            )
        return self.plate


class GenericPlate96Well(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Generic 96-well Plate",
            plate,
            14.5,
            10.7,
            8,
            12,
            0,
            0,
            9,
            9,
            "Based on 96 PlateOne V-Bottom",
        )


class NinetySixPlateOneVBottom(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "96 Plate One V Bottom",
            plate,
            14.5,
            10.7,
            8,
            12,
            0,
            0,
            9,
            9,
            "Based on 96 PlateOne V-Bottom",
        )


class ZAgilentReservoir_1row(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Z Agilent Reservoir - 1 row", plate, 44.5, 42.3, 8, 12, 0, 0, 9, 9, ""
        )


class NinetySixDeepWell(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition("96 Deep Well", plate, 42.0, 38.0, 8, 12, 0, 0, 9, 9, "")


class Reservoir_12col_Agilent_201256_100_BATSgroup(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Reservoir.12col.Agilent-201256-100.BATSgroup",
            plate,
            44.0,
            39.0,
            8,
            12,
            0,
            0,
            9,
            9,
            "12 column reservoir - 21 mL/well (JLJ",
        )


class Plate_96_Corning_3635_ClearUVAssay(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Plate.96.Corning-3635.ClearUVAssay",
            plate,
            14.2,
            10.6,
            8,
            12,
            0,
            0,
            9,
            9,
            "UV/Vis Transparent",
        )


class DeepBlock_96VWR_75870_792_sterile(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "DeepBlock.96VWR-75870-792.sterile",
            plate,
            44.2,
            99.7,
            8,
            12,
            0,
            0,
            9,
            9,
            "sterile deep well block (JLJ)",
        )


class Plate_96_Agilent_5043_9310_RoundBottomStorage(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Plate.96.Agilent-5043-9310.RoundBottomStorage",
            plate,
            14.6,
            10.2,
            8,
            12,
            0,
            0,
            9,
            9,
            "Falcon 96-well round bottom (bacteria)",
        )


class Plate_96_PlateOne_1833_9600_ConicalBottomStorage(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Plate.96.PlateOne-1833-9600.ConicalBottomStorage",
            plate,
            14.5,
            10.7,
            8,
            12,
            0,
            0,
            9,
            9,
            "MCULE",
        )


class AgarPlate_40mL_OmniTray_242811_ColonyPicker(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "AgarPlate.40mLOmniTray-242811.ColonyPicker",
            plate,
            15.0,
            6.9,
            8,
            12,
            0,
            0,
            9,
            9,
            "Omni Tray with 40ml agar",
        )


class Plate_384_Corning_3540_BlackwClearBottomAssay(PlateDefinition):
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Plate.384.Corning-3540.BlackwClearBottomAssay",
            plate,
            11.0,
            5.5,
            16,
            24,
            -2.25,
            -2.25,
            4.5,
            4.5,
            "Black w/clear 384 well (JLJ) 50uL",
        )
