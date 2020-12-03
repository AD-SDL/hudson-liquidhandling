class VolumeManager:
    def __init__(self, managed_plate, well_depth, well_width_x, well_width_y):
        self.set_managed_plate(managed_plate)
        self.set_well_volume(well_depth, well_width_x, well_width_y)

    def set_well_depth(self, value):
        if value > 0 and (type(value) == int or type(value) == float):
            self.well_depth = value
        else:
            raise ValueError("Well Height must be an integer or float greater than 0.")

    def set_well_width_x(self, value):
        if value > 0 and (type(value) == int or type(value) == float):
            self.well_width_x = value
        else:
            raise ValueError("Well Width must be an integer or float greater than 0.")

    def set_well_width_y(self, value):
        if value > 0 and (type(value) == int or type(value) == float):
            self.well_width_y = value
        else:
            raise ValueError("Well Depth must be an integer or float greater than 0.")

    def set_managed_plate(self, plate_description):
        if isinstance(plate_description, object):
            self.managed_plate = plate_description
        else:
            raise ValueError(
                "The Managed Plate should be an instance from the Plates.py definitions."
            )

    def set_well_volume(self, well_width_x, well_depth, well_width_y):
        self.set_well_depth(well_depth)
        self.set_well_width_x(well_width_x)
        self.set_well_width_y(well_width_y)

        self.well_volume = self.well_width_y * self.well_width_x * self.well_depth

    def get_top_of_liquid(self, row, column):
        used_volume = self.managed_plate.plate[row][column]
        return (used_volume - self.well_volume) / self.well_depth

    def get_position_for_aspirate(self, row, column, aspirate_volume, offset):
        used_volume = self.managed_plate.plate[row][column]
        position = (
            (used_volume - aspirate_volume) - self.well_volume
        ) / self.well_depth - offset
        if position > 0:
            return position
        else:
            return 0

    def change_volume_well(self, value, row, column):
        if isinstance(value, float) or isinstance(value, int):
            self.managed_plate.plate[row][column] = (
                self.managed_plate.plate[row][column] + value
            )

    def change_volume_row(self, value, row):
        if row in range(1, 9):
            for i in range(len(self.managed_plate.plate[0])):
                self.change_volume_well(value, row, i)
        else:
            print("row must be a number in range 1 to <row number>")

    def change_volume_column(self, value, column):
        if column in range(1, len(self.managed_plate.plate)):
            for i in range(len(self.managed_plate.plate)):
                self.change_volume_well(value, i, column)
        else:
            print("row must be a number in range 1 to <column number>")

    def change_volume_all(self, value):
        for row in range(len(self.managed_plate.plate)):
            for column in range(len(self.managed_plate.plate[0])):
                self.change_volume_well(value, row, column)
