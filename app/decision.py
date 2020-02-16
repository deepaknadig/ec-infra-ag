#!/usr/bin/env python
import statistics as st
from enum import Enum
import json

# Field dimensions -- grid of cells each cells contains a sensor
n = 2
m = 2


# decision enum type:
class Decision(Enum):
    NO_SPRAYING = 1
    FLAG = 2
    SPRAY_MORE = 3
    SPRAY_LESS = 4
    UNDEF = 5


# Compute the average for every 4 (square) cells
def avg_nutrients(nutrient):
    avg = [[0 for i in range(m / 2)] for j in range(n / 2)]
    for i in range(0, n, 2):
        for j in range(0, m, 2):
            avg[i / 2][j / 2] = st.mean(nutrient[i][j:j + 2] + nutrient[i + 1][j:j + 2])
    return avg


# Generate decision based on data points
def fertilizer_decision(N, P, K, NDVI, wind_speed, timestamp):
    # source https://www.researchgate.net/post/what_are_the_ideal_levels_of_NPK_in_soil_in_ppm
    # https://www.canr.msu.edu/foodsystems/uploads/files/soil_test_interpretation.pdf
    # in ppm
    avg_N = 50
    # in ppm
    avg_P = 5
    # in ppm
    avg_K = 180
    # NDVI (no unit)
    # source https://blog.onesoil.ai/en/what-is-ndvi
    low_ndvi = (0.15, 0.2)  # flag
    avg_ndvi = (0.2, 0.3)  # increase fertilizer 20-15%
    high_ndvi = (0.3, 0.5)  # decrease 10-30%
    # in mph if < x, no spraying
    max_wind_speed = 10.0

    # ndvi = NDVI[0][0]
    decision = Decision.UNDEF
    if wind_speed > max_wind_speed + 2:
        decision = Decision.NO_SPRAYING
    elif NDVI < 0.2:
        decision = Decision.FLAG
    else:
        n_val = st.mean(N)  # avg_nutrients(N)
        p_val = st.mean(P)  # avg_nutrients(P)
        k_val = st.mean(K)  # avg_nutrients(K)
        # if N_val[0][0]<avg_N or P_val[0][0]<avg_P or K_val[0][0]<avg_K:
        if n_val < avg_N or p_val < avg_P or k_val < avg_K:
            if 0.3 > NDVI >= 0.2:
                decision = Decision.SPRAY_MORE
            elif 0.51 > NDVI >= 0.3:
                decision = Decision.SPRAY_LESS
        else:
            decision = Decision.NO_SPRAYING
    return json.dumps({"decision": decision.name, "timestamp": timestamp})
