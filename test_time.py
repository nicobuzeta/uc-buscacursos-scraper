from datetime import datetime, timedelta
from copy import deepcopy


def times():
    times_reajuste_1 = []
    time_between = timedelta(hours=1, minutes=30)

    for day_extra in range(0, 2):
        time_base = datetime(2021, 8, 10 + day_extra, 8, 00, 00)
        for banner in range(1, 9):
            time = deepcopy(time_base)

            start_time = time + time_between * (banner - 1)
            end_time = time + time_between * banner - timedelta(minutes=10)
            times_reajuste_1.extend([start_time, end_time])

    times_reajuste_2 = []
    time_base = datetime(2021, 8, 13, 8, 00, 00)

    for banner in range(1, 9):

        time = deepcopy(time_base)

        start_time = time + time_between * (banner - 1)
        end_time = time + time_between * banner - timedelta(minutes=10)
        times_reajuste_2.extend([start_time, end_time])

    return times_reajuste_1 + times_reajuste_2
