# lsttp = [("Unga", 100), ("Bread", 120), ("Milk", 56)]
# for i in lsttp:
#     t = i[0]
#     u = i[1]
#     print(t, u)


# An extra day is added to the calendar almost every four years as February 29, and the day is called a leap day. It corrects the calendar for the fact that our planet takes approximately 365.25 days to orbit the sun. A leap year contains a leap day.
# In the Gregorian calendar, three conditions are used to identify leap years:

# The year can be evenly divided by 4, is a leap year, unless:
# The year can be evenly divided by 100, it is NOT a leap year, unless:
# The year is also evenly divisible by 400. Then it is a leap year.

# def is_leap(year):
#     leap = False

#     # Write your logic here

#     return leap


# year = int(input())
# print(is_leap(year))

year = 2008
if year & 4 == 0:
    print("ok")
elif year & 100 == 0:
    print("not ok")
