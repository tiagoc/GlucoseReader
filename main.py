# coding=utf-8
__author__ = 'ei09044@fe.up.pt'


parsed_sensor_data = []


# Reads and parses the input file with the sensor data
# TODO: Make the parsing more robust, has to handle bad inputs and still go on
def read_sensor_input(filename):
    with open(filename) as fileobject:
        for line in fileobject:
            parsed_sensor_data.append([float(n) for n in line.strip().split(' ', 2)])
        for pair in parsed_sensor_data:
            try:
                x, y = pair[0], pair[1]
                # TODO: check if x, y are valid? irrelevant because of previous check? do something else here?
            except IndexError:
                print("A line is missing entries.")
        print(parsed_sensor_data)  # debug parser


# Converts the sensor data to readable mmol/l values, used to measure blood glucose levels
def convert_sensor_data_to_mmoll(value):
    g = -3.4 + 1.354 * value + 1.545 * math.tan(math.pow(1.0 / 3.0, value))
    return g


# Calculates the insulin dosage required
# calculate_insulin_dosage(glucose concentration, glucose variation, glucose variation min^2, current insulin)
def calculate_insulin_dosage(g, dg, ddg, ic):
    d = 0.8 * g + 0.2 * dg + 0.5 * ddg - ic
    return d


# Returns the current insulin level in the subject
# calculate_insulin_level(dosage applied, previous insulin value):
def calculate_insulin_level(d, last_ic):
    ic = d + 0.9 * last_ic
    return ic


def main(args):
    try:
        input_data_file = args[0]
    except IndexError:
        raise SystemExit('An input file is required.')

    read_sensor_input(input_data_file)


if __name__ == '__main__':
    import sys
    import math

    main(sys.argv[1:])  # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).
