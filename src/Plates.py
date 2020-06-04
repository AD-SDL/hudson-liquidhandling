class Plate96Well:
    def __init__(self, plate=None):
        self.plate = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        try:
            if plate != None:
                self.plate == plate
        except:
            print("Error setting plate definition.")
            return

    def setRow(self, row="A", value=0):
        alpha_vals = ["A", "B", "C", "D", "E", "F", "G", "H"]
        if str.upper(row) in alpha_vals:
            index = alpha_vals.index(str.upper(row))
            if float(value) >= 0:
                for i in range(12):
                    self.plate[index][i] = value
            else:
                print("value must be a non-negative number")
                return
        elif row in range(1, 9):
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
        if column in range(1, 13):
            if float(value) >= 0:
                for row in range(8):
                    self.plate[row][column - 1] = value
            else:
                print("value must be a non-negative number")
                return
        else:
            print("column must be a number in the range 1-13")
            return
        return self.plate

    def setAll(self, value=0):
        if float(value) >= 0:
            for row in range(8):
                for column in range(12):
                    self.plate[row][column] = value
        else:
            print("value must be a non-negative number")
            return
        return self.plate
