import pprint
import random
import io


def strip_curlies(variable_to_strip):
    variable_to_strip = variable_to_strip.replace("{", "")
    variable_to_strip = variable_to_strip.replace("}", "")
    return variable_to_strip


def strip_newlines(variable_to_strip):
    variable_to_strip = variable_to_strip.replace("\n", "")
    return variable_to_strip


def load_seatmap(input_string):

    input_string = input_string + "\n"

    with io.StringIO(input_string) as file:

        list_of_rows = file.readlines()

        # The first line is the key, so read that first
        key_row = list_of_rows[0]
        key_row = key_row[3:]
        key_row = strip_curlies(key_row)

        column_names = ["X"]
        for character in key_row:
            column_names.append(character)

        output_list = []

        # Now iterate through the rest of the lines
        row_counter = 1
        for row in list_of_rows[1:]:

            y = row_counter
            row_name = row[0:2]

            row_content = row[3:-2]

            character_counter = 1
            for character in row_content:
                x = character_counter

                if character == " ":
                    seat_number = None
                else:
                    seat_number = row_name + column_names[character_counter]

                new_seat = {
                    'x': x,
                    'y': y,
                    'seat_type': character,
                    'seat_number': seat_number
                }

                output_list.append(new_seat)
                character_counter = character_counter + 1

            row_counter = row_counter + 1

    seatmap_object = output_list
    return seatmap_object


def get_seats_by_type(seatmap_object, desired_seat_type, random_order=False):

    relevant_seat_list = []

    for seat in seatmap_object:
        if seat["seat_type"] == desired_seat_type:
            relevant_seat_list.append(seat)

    if random_order:
        random.shuffle(relevant_seat_list)

    return relevant_seat_list


def count_seats (seatmap_object, desired_seat_type=None):
    count_to_return = 0

    for seat in seatmap_object:
        if desired_seat_type == None:
            if seat["seat_type"] != " ":
                count_to_return = count_to_return + 1
        else:
            if seat["seat_type"] == desired_seat_type:
                count_to_return = count_to_return + 1

    return count_to_return


def get_size (seatmap_object):

    highest_x = 0
    highest_y = 0

    for seat in seatmap_object:
        if seat['x'] > highest_x:
            highest_x = seat['x']

        if seat['y'] > highest_y:
            highest_y = seat['y']

    return highest_x, highest_y
