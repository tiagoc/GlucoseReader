__author__ = 'ei09044@fe.up.pt'

import math


def read_sensor_input(filename):
    with open(filename, "r") as fileobject:
        for line in fileobject:
            pass


def convert_sensor_data_to_mmoll(value):
    g = -3.4 + 1.354 * value + 1.545 * math.tan(math.pow(1.0 / 3.0, value))
    return g


# (glucose concentration, glucose variation, glucose variation min^2, insulin value)
def calculate_insulin_dosage(g, dg, ddg, ic):
    d = 0.8 * g + 0.2 * dg + 0.5 * ddg - ic
    return d


def calculate_insulin_level(d, last_ic):
    ic = d + 0.9 * last_ic
    return ic


def main(args):
    try:
        src_name = args[0]
    except IndexError:
        raise SystemExit('An input file is required.')

    read_sensor_input(src_name)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])  # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).