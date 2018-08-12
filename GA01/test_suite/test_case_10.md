## Test Case 10
#### Objective
- Test functionality of Wind speed in mph, teperature in USCS measures on March 3, 2001 at 6:10 PM for one day, one month and one year

#### Command being tested
- The time-offset and metric functionality ```--time-offset=03/03/2001:18:10 WS WS-M WS-D WS-Y T T-D T-M T-Y```.

#### Input
``` $ python AmesWeather.py --time-offset=03/03/2001:18:10 WS WS-M WS-D WS-Y T T-D T-M T-Y```


#### Expected output
- 10.9, 13.2, 6.9, 3.0, 26.6, 33.1, 24.4, 43.8

#### Observed output
- 10.9, 13.2, 6.9, 3.0, 26.6, 33.1, 24.4, 43.8

#### Version and pass date
- Pass: 2/20/2017
- Version: ```80f967a4c6ce8e71aaa6f03929a86b79572a9746```
