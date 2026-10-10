I am trying to reverse engineer the functionality of a 3-socket smart power strip. The application has a "Scheduled Cycle" feature.
The tested options values use the following format: "socket_num - activation - start_time-end_time - repeat - open_time - close_time".
I have performed some tests and recorded the corresponding payload.

```
payload             | Valeur
AQADygR+AAEAAQ== | 1 - activate - 16:10-19:10 - once - 1min - 1min
AAADygR+AAEAAQ== | 1 - deactivate - 16:10-19:10 - once - 1min - 1min
AQAACgVwAAEAAQ== | 1 - activate - 00:10-23:12 - once - 1min - 1min
AAAACgVwAAEAAQ== | 1 - deactivate - 00:10-23:12 - once - 1min - 1min
AwADygR+AAEAAQ== | 2 - activate - 16:10-19:10 - once - 1min - 1min
AgADygR+AAEAAQ== | 2 - deactivate - 16:10-19:10 - once - 1min - 1min
AwAACgVwAAEAAQ== | 2 - activate - 00:10-23:12 - once - 1min - 1min
AgAACgVwAAEAAQ== | 2 - deactivate - 00:10-23:12 - once - 1min - 1min
BQADygR+AAEAAQ== | 3 - activate - 16:10-19:10 - once - 1min - 1min
BQADzwSDAAEAAQ== | 3 - activate - 18:15-22:15 - once - 1min - 1min
BQADygU3AAEAAQ== | 3 - activate - 16:10-22:15 - once - 1min - 1min
BQAFnQWfAAEAAQ== | 3 - activate - 23:57-23:59 - once - 1min - 1min
BQAFnwABAAEAAQ== | 3 - activate - 23:59-00:01 - once - 1min - 1min
BQADygR+AAIAAg== | 3 - activate - 16:10-19:10 - once -  2min - 2min
BQAEZQAAADwAPA== | 3 - activate - 18:45-00:00 - once - 1h - 1h
BQAE3QVkADwAPA== | 3 - activate - 20:45-23:00 - once - 1h - 1h
BQAEvwWRADwAPA== | 3 - activate - 20:15-23:45 - once - 1h - 1h
BQADGwWRAIcAtA== | 3 - activate - 13:15-23:45 - once - 2h15 - 3h
BQADFgPWAAoACg== | 3 - activate - 13:10-16:22 - once - 10m - 10m
BAADFgPWAAoACg== | 3 - deactivate - 13:10-16:22 - once - 10min - 10min
BQADkwRWAAoACg== | 3 - activate - 15:15-18:30 - once - 10min - 10min
BAADkwRWAAoACg== | 3 - deactivate - 15:15-18:30 - once - 10min - 10min
BQADSAPPADwAPA== | 3 - activate - 14:00-16:15 - once - 1h - 1h
BAADSAPPADwAPA== | 3 - deactivate - 14:00-16:15 - once - 1h - 1h
BQADUgPPADwAPA== | 3 - activate - 14:10-16:15 - once - 1h - 1h
BAADUgPPADwAPA== | 3 - deactivate - 14:10-16:15 - once - 1h - 1h
BQMCYgPPADwAPA== | 3 - activate - 14:10-16:15 - Sunday,Monday - 1h - 1h
BQYCYgVkADwAPA== | 3 - activate - 10:10-23:00 - Monday,Tuesday - 1h - 1h
BQwCYgVkADwAPA== | 3 - activate - 10:10-23:00 - Tuesday,Wednesday - 1h - 1h
BQgA9gFIAAoACg== | 3 - activate - 04:06-05:28 - Wednesday - 10min - 10min
BRgA9gFIAAoACg== | 3 - activate - 04:06-05:28 - Wednesday,Thursday - 10min - 10min
BSAA9gFIAAoACg== | 3 - activate - 04:06-05:28 - Friday - 10min - 10min
BWAA9gFIAAoACg== | 3 - activate - 04:06-05:28 - Friday,Saturday - 10min - 10min
BQEA9gFIAAoACg== | 3 - activate - 04:06-05:28 - Sunday - 10min - 10min
BQAA9gFIAAoACg== | 3 - activate - 04:06-05:28 - once - 10min - 10min
BQ8DUgPPADwAPA== | 3 - activate - 14:10-16:15 - Sunday,Monday,Tuesday,Wednesday - 1h - 1h
BX8DUgPPADwAPA== | 3 - activate - 14:10-16:15 - Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday - 1h - 1h
BH8DUgPPADwAPA== | 3 - deactivate - 14:10-16:15 - Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday - 1h - 1h
```

I then set the same cycle on 2 different sockets
```
1 - activate - 23:30-00:30 - once - 1min - 1min
2 - activate - 23:30-00:30 - once - 1min - 1min
```
and I got the following payload `AwAFggW+AAEAAQEABYIFvgABAAE=`

Finally, I set 3 cycles on 2 different sockets
```
1 - activate - 23:30-00:30 - once - 1min - 1min
2 - activate - 23:30-00:30 - once - 1min - 1min
2 - activate - 16:40-12:30 - once - 1min - 1min
```
This gave me the following payload `AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB`
