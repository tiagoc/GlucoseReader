# coding=utf-8

__author__ = 'ei09044@fe.up.pt'


# Variables ---------------------------------
sensor_data = []
parsed_sensor_data = []
glucose_blood_levels = []  # g
glucose_variation = []  # dg
variation_glucose_variation = []  # ddg
decisions = []

max_glucose = 6.0
min_glucose = 3.9
max_variation = 2.0
last_ic = 0.0
max_acceptable_reading = 5.0
min_acceptable_reading = 1.0

glucose_rising = False
max_fails = 20
# -------------------------------------------


# Returns True if the input is a float
def validate_input(reading):
    try:
        float(reading)
    except ValueError:
        return False
    return True


# This function connects everything. It reads and parses the file, deciding what to do accordingly
def parse_and_decide(filename):
    last_input_a = 0.0
    last_input_b = 0.0
    fails = 0
    last_good_value_a = 0.0
    last_good_value_b = 0.0
    global glucose_rising
    global last_ic

    with open(filename) as fileobject:
        for line in fileobject:
            try:
                sensor_data.append([float(n) for n in line.strip().split(' ', 2)])
            except ValueError:
                sensor_data.append([n for n in line.strip().split(' ', 2)])
        if fails < max_fails:
            for pair in sensor_data:
                x, y = pair[0], pair[1]
                # print(x)
                # print(y)

                fail_a = False
                fail_b = False

                # Checks input errors
                if validate_input(x) and validate_input(y):
                    fail_a = False
                    fail_b = False
                elif validate_input(x) and not validate_input(y):
                    fail_a = False
                    fail_b = True
                    print("S2_FAILURE")
                elif not validate_input(x) and validate_input(y):
                    fail_a = True
                    fail_b = False
                    print("S1_FAILURE")
                elif not validate_input(x) and not validate_input(y):
                    fail_a = True
                    fail_b = True

                if not fail_a:
                    if float(x) < min_acceptable_reading or float(x) > max_acceptable_reading:
                        fail_a = True
                        print("S1_OUT_OF_RANGE")
                    if x == last_input_a:
                        fail_a = True
                        print("S1_STUCKAT")
                    if abs(float(x) - float(last_good_value_a) > float(max_variation)) and last_input_a != 0.0:
                        fail_a = True
                        print("S1_RANDOMVALUES")

                if not fail_b:
                    if float(y) < min_acceptable_reading or float(y) > max_acceptable_reading:
                        fail_b = True
                        print("S2_OUT_OF_RANGE")

                    if y == last_input_b:
                        fail_b = True
                        print("S2_STUCKAT")

                    if abs(float(y) - float(last_good_value_b) > float(max_variation)) and last_input_b != 0.0:
                        fail_b = True
                        print("S2_RANDOMVALUES")

                if not fail_a and not fail_b:
                    parsed_sensor_data.append(statistics.mean([x, y]))
                    last_input_a = x
                    last_input_b = y
                    last_good_value_a = last_input_a
                    last_good_value_b = last_input_b

                if not fail_a and fail_b:
                    print("S2_FAILURE")
                    parsed_sensor_data.append(float(x))
                    last_input_a = x
                    # last_input_b = y
                    last_good_value_a = last_input_a
                    last_good_value_b = last_input_b

                if not fail_b and fail_a:
                    print("S1_FAILURE")
                    parsed_sensor_data.append(float(y))
                    # last_input_a = x
                    last_good_value_a = last_input_a
                    last_good_value_b = last_input_b
                    last_input_b = y

                if fail_a and fail_b:
                    fails += 1
                # -----------------------------------------------------

                glucose_rising = False

                if len(parsed_sensor_data) < 3:
                    print("WAIT")
                elif 3 <= len(parsed_sensor_data) < 30 and len(parsed_sensor_data) % 3 == 0 and (not fail_a or not fail_b):
                    glucose_blood_levels.append(convert_sensor_data_to_mmoll(statistics.mean(parsed_sensor_data)))
                    glucose_variation.append(calculate_variation(parsed_sensor_data))
                    if len(glucose_variation) >= 3:
                        variation_glucose_variation.append(calculate_variation_of_variation(glucose_variation))
                    if glucose_variation[-1] < -0.4:
                        glucose_rising = True
                    # print(glucose_blood_levels)
                    print("WAIT")
                    decisions.append("WAIT")
                elif len(parsed_sensor_data) >= 30 and len(parsed_sensor_data) % 3 == 0 and (not fail_a or not fail_b):
                    g = convert_sensor_data_to_mmoll(statistics.mean(parsed_sensor_data[-30:]))
                    glucose_blood_levels.append(g)
                    dg = calculate_variation(parsed_sensor_data[-3:])
                    glucose_variation.append(dg)
                    ddg = calculate_variation_of_variation(glucose_variation[-3:])
                    variation_glucose_variation.append(ddg)

                    if glucose_variation[-1] < -0.4:
                        glucose_rising = True
                    if decide_insulin_injection(g):
                        dosage = round(calculate_insulin_dosage(g, dg, ddg, last_ic))
                        if dosage == -1.0:
                            dosage = 0
                        decisions.append(dosage)
                        last_ic = calculate_insulin_level(dosage, last_ic)
                    else:
                        decisions.append(decide_insulin_injection(g))
                    # print(decide_insulin_injection(convert_sensor_data_to_mmoll(statistics.mean(parsed_sensor_data[-30:]))))

            # Debugging prints:
            # print(sensor_data)
            # print(parsed_sensor_data)
            # print(glucose_blood_levels)
            # print(decisions)
            # print(fails)
        else:
            print("FAIL")
            decisions.append("FAIL")

        string_to_send = []

        with open("decisions.txt", 'w') as file:
            for item in decisions:
                file.write("{}\n".format(item))
                string_to_send.append(str(item)
                                      )
        string_to_send = "\n".join(string_to_send)
        data_ = {"data": string_to_send}
        # print(string_to_send)
        requests.post('http://localhost:8080/scri', data=data_)


# Converts the sensor data to readable mmol/l values, used to measure blood glucose levels
def convert_sensor_data_to_mmoll(value):
    g = -3.4 + 1.354 * value + 1.545 * math.tan(math.pow(value, (1.0 / 4.0)))
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
    oldest = values[len(values) - 3]
    old = values[len(values) - 2]
    new = values[len(values) - 1]

    x = old - oldest
    y = new - old
    return (x + y) / 2


# Returns the variation of the variation of glucose blood levels using the last 3 values of dg
def calculate_variation_of_variation(values):
    oldest = values[len(values) - 3]
    old = values[len(values) - 2]
    new = values[len(values) - 1]

    x = old - oldest
    y = new - old
    return (y - x) / 2


# Insulin should only be administered if the glucose blood levels are above the maximum and tending to rise
def decide_insulin_injection(glucose_levels):
    if glucose_levels > max_glucose and glucose_rising:
        return True
    else:
        return 0


def main(args):
    try:
        input_data_file = args[0]
    except IndexError:
        print("Please specify the input file. Trying to load the default sensor_data.txt...")
        input_data_file = "sensor_data.txt"
        print("Default file loaded.")

    parse_and_decide(input_data_file)


if __name__ == '__main__':
    import sys
    import math
    import statistics
    import requests

    main(sys.argv[1:])  # Execute 'main' with all the command line arguments (excluding sys.argv[0], the program name).
