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
                print("value must be a non-negative number")
                return
        elif row in range(1, self.rows + 1):
            if float(value) >= 0:
                for i in range(12):
                    self.plate[row][i] = value
            else:
                print("value must be a non-negative number")
                return
        else:
            print("row must be a character in the range A-H, or a number 1-8")
            return
        return self.plate

    def setColumn(self, column=1, value=0):
        if column in range(1, self.columns + 1):
            if float(value) >= 0:
                for row in range(self.rows):
                    self.plate[row][column - 1] = value
            else:
                print("value must be a non-negative number")
                return
        else:
            print("column must be a number in the range 1-12 inclusive")
            return
        return self.plate

    def setAll(self, value=0):
        if float(value) >= 0:
            for row in range(self.rows):
                for column in range(self.columns):
                    self.plate[row][column] = value
        else:
            print("value must be a non-negative number")
            return
        return self.plate


class GenericPlate96Well:
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


class NinetySixPlateOneVBottom:
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


class ZAgilentReservoir_1row:
    def __new__(cls, plate=None):
        return PlateDefinition(
            "Z Agilent Reservoir - 1 row", plate, 44.5, 42.3, 8, 12, 0, 0, 9, 9, ""
        )


class NinetySixDeepWell:
    def __new__(cls, plate=None):
        return PlateDefinition("96 Deep Well", plate, 42.0, 38.0, 8, 12, 0, 0, 9, 9, "")
