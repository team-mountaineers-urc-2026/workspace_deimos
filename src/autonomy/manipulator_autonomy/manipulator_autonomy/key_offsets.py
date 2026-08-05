#!/usr/bin/env python3

column_dist = 0.02 # meters
row_dist = 0.02
first_row_offset = 0.011
second_row_offset = 0.015

key_offsets = {
    "Q" : (0,0),
    "W" : (0,1),
    "E" : (0,2),
    "R" : (0,3),
    "T" : (0,4),
    "Y" : (0,5),
    "U" : (0,6),
    "I" : (0,7),
    "O" : (0,8),
    "P" : (0,9),
    "A" : (1,0),
    "S" : (1,1),
    "D" : (1,2),
    "F" : (1,3),
    "G" : (1,4),
    "H" : (1,5),
    "J" : (1,6),
    "K" : (1,7),
    "L" : (1,8),
    "Z" : (2,0),
    "X" : (2,1),
    "C" : (2,2),
    "V" : (2,3),
    "B" : (2,4),
    "N" : (2,5),
    "M" : (2,6),
}

# Outputs cartesian relative distance from the Q key
def dist_out(key : str):
    row, col = key_offsets.get(key)
    delta_x = col * column_dist # horizontal distance
    delta_z = -row * row_dist # vertical distance
    if row == 1:
        delta_x = delta_x + first_row_offset
    elif row == 2:
        delta_x = delta_x + second_row_offset
    return delta_x, delta_z


