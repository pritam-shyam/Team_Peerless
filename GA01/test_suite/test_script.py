from subprocess import check_output
from re import sub

print(" ")
print("Test Case Scripts")
print(" ")

print("-----Case 1-----")
print("Current Pressure")
case1 = check_output(["python3", "../AmesWeather.py", "P"])
print(sub("[b']", "", str(case1)[:len(case1)]))

print(" ")
print("-----Case 2-----")
print("Current Temperature")
case2 = check_output(["python3", "../AmesWeather.py", "T"])
print(sub("[b']", "", str(case2)[:len(case2)]))

print(" ")
print("-----Case 3-----")
print("Current Wind Speed")
case3 = check_output(["python3", "../AmesWeather.py", "WS"])
print(sub("[b']", "", str(case3)[:len(case3)]))

print(" ")
print("-----Case 4-----")
print("Current Wind Direction")
case4 = check_output(["python3", "../AmesWeather.py", "WD"])
print(sub("[b']", "", str(case4)[:len(case4)]))

print(" ")
print("-----Case 5-----")
print("Temperature on March 3, 2001 at 10:00 AM")
case5 = check_output(["python3", "../AmesWeather.py", "--time-offset=2/18/2017:10:00", "T"])
print(sub("[b']", "", str(case5)[:len(case5)]))

print(" ")
print("-----Case 6-----")
print("Current Temperature and Pressure in Metric Units")
case6 = check_output(["python3", "../AmesWeather.py", "--metric", "T", "P"])
print(sub("[b']", "", str(case6)[:len(case6)]))

print(" ")
print("-----Case 7-----")
print("Wind Speed and Temperature on June 10, 2012 at 11:00 AM")
case7 = check_output(["python3", "../AmesWeather.py", "--time-offset=6/10/2012:11:00", "WS", "T"])
print(sub("[b']", "", str(case7)[:len(case7)]))

print(" ")
print("-----Case 8-----")
print("Wind Speed and Temperature on June 10, 2012 at 11:00 AM in Metric")
case8 = check_output(["python3", "../AmesWeather.py", "--time-offset=6/10/2012:11:00", "--metric", "WS", "T"])
print(sub("[b']", "", str(case8)[:len(case8)]))

print(" ")
print("-----Case 9-----")
print("Yesterday Temp, Last Week Temp, Last Year Temp")
case9 = check_output(["python3", "../AmesWeather.py", "T-D", "T-W", "T-Y"])
print(sub("[b']", "", str(case9)[:len(case9)]))

print(" ")
print("-----Case 10-----")
print("Wind Speed (MPH) and Temperature (USCS) on March 3, 2001 at 6:10 PM for a day, month, and year")
case10 = check_output(["python3", "../AmesWeather.py", "--time-offset=03/03/2001:18:10", "WS", "WS-M", "WS-D", "WS-Y", "T", "T-M", "T-D", "T-Y"])
print(sub("[b']", "", str(case10)[:len(case10)]))
