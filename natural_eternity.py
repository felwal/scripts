import math
import numpy as np
from numpy import log as ln

# get a number of date-times, with the time in between
# increasing faster and faster by -ln(-x). this results
# in a sequence of [min, ..., max, inf]. useful for when
# all of time passes infinitely fast past a specific date.
# for instance when the universe ends.

# define a custom calendar
sec_per_min = 60
min_per_hour = 100
hours_per_day = 24
days_per_month = 40
days_per_year = 365

sec_per_hour = sec_per_min * min_per_hour
sec_per_day = sec_per_hour * hours_per_day
sec_per_month = sec_per_day * days_per_month
sec_per_year = sec_per_day * days_per_year

def print_date(secs):
    year = secs // sec_per_year + 1
    month = secs % sec_per_year // sec_per_month + 1
    day = secs % sec_per_year % sec_per_month // sec_per_day + 1
    hour = secs % sec_per_year % sec_per_month % sec_per_day // sec_per_hour
    min = secs % sec_per_hour // sec_per_min
    sec = secs % sec_per_min

    #print(f"{Y}-{M:02}-{d:02}, {h:02}:{m:02}:{s:02}")
    print(f"{hour:02}:{min:02}, {day:02} {month:02}, {year}")

def natural_eternity(min, max, num):
    """
    return [min, ..., max, inf], increasing naturally with -ln(-x)
    """

    interval = np.linspace(min, max, num)
    out = []
    for k in interval:
        if k == max: value = math.inf
        else: value = int(max * ln(1 - k / max) / ln(1 - interval[-2] / max))
        out.append(value)
    return out

#

def main():
    start = 3 * sec_per_month + 33 * sec_per_day + 11 * sec_per_hour + 90 * sec_per_min
    end = 3 * sec_per_year

    s_list = natural_eternity(0, end - start, 19)
    for i in range(len(s_list)):
        s_list[i] += start

    np.vectorize(print_date)(s_list)

    print()

if __name__ == "__main__":
    main()
