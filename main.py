# coding=utf-8

__author__ = 'ei09044@fe.up.pt'


# Variables
sensor_data = []
parsed_sensor_data = []
max_glucose = 6.0
min_glucose = 3.9
glucose_rising = False


# Returns True if the input is a float
def validate_input(reading):
    try:
        float(reading)
    except ValueError:
            return False
    return True

# Reads and parses the input file with the sensor data
def read_sensor_input(filename):
    with open(filename) as fileobject:
        for line in fileobject:
            try:
                sensor_data.append([float(n) for n in line.strip().split(' ', 2)])
            except ValueError:
                sensor_data.append([n for n in line.strip().split(' ', 2)])
        for pair in sensor_data:
            x, y = pair[0], pair[1]
            if validate_input(x) and validate_input(y):
                parsed_sensor_data.append(statistics.mean([x, y]))
            elif validate_input(x) and not(validate_input(y)):
                parsed_sensor_data.append(x)
            elif validate_input(y) and not(validate_input(x)):
                parsed_sensor_data.append(y)
        # Debugging prints:
        # print(sensor_data)
        # print(parsed_sensor_data)


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


# Returns the variation using the last 3 readings
def calculate_variation(values):
    oldest = values[values.lenght-3]
    old = values[values.lenght-2]
    new = values[values.lenght-1]

    x = old - oldest
    y = new - old
    return (x + y) / 2


# Returns the variation of the variation of glucose blood levels using the last 3 values of dg
def calculate_variation_of_variation(values):
    oldest = values[values.lenght-3]
    old = values[values.lenght-2]
    new = values[values.lenght-1]

    x = old - oldest
    y = new - old
    return (y - x) / 2


# Calculates the mean glucose blood level value with the last 30 readings
# TODO get the 30 values, account for errors
def get_glucose_level(values):
    return statistics.mean(values)


# Insulin should only be administered if the glucose blood levels are above the maximum and tending to rise
def decide_insulin_injection(values):
    if get_glucose_level(values) > max_glucose and glucose_rising:
        return True
    else:
        return False


def main(args):
    try:
        input_data_file = args[0]
    except IndexError:
        raise SystemExit('An input file is required.')

    read_sensor_input(input_data_file)


if __name__ == '__main__':
    import sys
    import math
    import statistics

    main(sys.argv[1:])  # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).
