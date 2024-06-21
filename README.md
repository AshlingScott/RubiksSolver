# RubiksSolver
Program for Solving a randomized Rubik's Cube

A program for solving Rubiks Cubes, created by Ashling Scott and Hunter Jones of Kent State University.  This program takes a randomized cube and tries to solve it by first creating a database of states from 3 distinct cubie groups (2 consisting of edge cubies and 1 of corner cubies).  These databases record how many moves away from solved many configurations of cubie groups are, and uses this number as a heuristic to guide the randomized cube toward a solved states.  For states that are not within the limits of the database, an alternative heuristic is used which counts how many cubies are in the correct spot and correct orientation, and gives an estimate of how close this state is to completed.

Databases must first be generated using the provided function before the program can efficiently solve a randomized cube state.
