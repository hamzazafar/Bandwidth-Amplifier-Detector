## Client usage examples:

### Print help:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py -h
usage: scan.py [-h] [--name NAME] [--target-port TARGET_PORT]
               [--target-hosts TARGET_HOSTS [TARGET_HOSTS ...]]
               [--request-payload REQUEST_PAYLOAD] [--minute MINUTE]
               [--hour HOUR] [--day-of-week DAY_OF_WEEK]
               [--day-of-month DAY_OF_MONTH] [--month-of-year MONTH_OF_YEAR]
               [--latest LATEST]
               {create,delete,list,info,result}

positional arguments:
  {create,delete,list,info,result}

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           set name of scan
  --target-port TARGET_PORT
                        port number to scan
  --target-hosts TARGET_HOSTS [TARGET_HOSTS ...]
                        Space separated list of target address ranges in CIDR
                        notaion
  --request-payload REQUEST_PAYLOAD
                        HEX encoded request payload
  --minute MINUTE       Minute field for Cron
  --hour HOUR           Hour field for Cron
  --day-of-week DAY_OF_WEEK
                        Day of the week field for Cron
  --day-of-month DAY_OF_MONTH
                        Day of the month field for Cron
  --month-of-year MONTH_OF_YEAR
                        Month of the year field for Cron
  --latest LATEST       Get n number of recent scan results
```

### Create Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py  create --name scan_two \
                                                                    --target-port 12 \
                                                                    --target-hosts 10.10.0.0/16 192.168.0.0/16 \
                                                                    --request-payload abcabcabc \
                                                                    --minute */2
Scan 'scan_two' created successfully
```

### Get Scan Info:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py info --name scan_two
Details for scan 'scan_two'


            * Enabled: True
            * Total run count: 4
            * Last run at: 2019-01-22T11:04:00.005508Z
            * Target addresses: ['10.10.0.0/16', '192.168.0.0/16']
            * Target port: 12
            * Request Hexdump: abcabcabc
            * Cron: */2 * * * *
```

### Get Scans List:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py list
Scans List:

* celery.backend_cleanup
* scan_two
* scan_one
```

### Get Latest Scanning Results:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py result --name scan_two


* Status: SUCCESS
* Created: 2019-01-22T11:04:00.042167Z
* Number of Amplifiers: 7
+-----------------+---------------+----------------------+
|    Amplifier    | Response Size | Amplification Factor |
+-----------------+---------------+----------------------+
| 101.219.150.253 |      9039     |        192.32        |
|  180.247.179.41 |      6797     |        144.62        |
| 169.185.199.145 |      6632     |        141.11        |
| 202.244.176.129 |      4757     |        101.21        |
|   40.40.33.148  |      1797     |        38.23         |
| 191.189.151.112 |      1772     |         37.7         |
|  144.120.175.80 |      553      |        11.77         |
+-----------------+---------------+----------------------+

```

### Get N Latest Scanning Results:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py result --name scan_two --latest=2


* Status: SUCCESS
* Created: 2019-01-22T11:02:00.037994Z
* Number of Amplifiers: 9
+-----------------+---------------+----------------------+
|    Amplifier    | Response Size | Amplification Factor |
+-----------------+---------------+----------------------+
|  203.14.54.182  |      9968     |        284.8         |
|  255.55.231.124 |      9398     |        268.51        |
|  68.67.115.198  |      7467     |        213.34        |
| 174.236.148.107 |      6260     |        178.86        |
|  196.225.90.223 |      5443     |        155.51        |
|  78.160.155.40  |      2087     |        59.63         |
|  209.114.63.203 |      1723     |        49.23         |
|  24.107.132.55  |      680      |        19.43         |
| 160.160.110.122 |      162      |         4.63         |
+-----------------+---------------+----------------------+
* Status: SUCCESS
* Created: 2019-01-22T11:04:00.042167Z
* Number of Amplifiers: 7
+-----------------+---------------+----------------------+
|    Amplifier    | Response Size | Amplification Factor |
+-----------------+---------------+----------------------+
| 101.219.150.253 |      9039     |        192.32        |
|  180.247.179.41 |      6797     |        144.62        |
| 169.185.199.145 |      6632     |        141.11        |
| 202.244.176.129 |      4757     |        101.21        |
|   40.40.33.148  |      1797     |        38.23         |
| 191.189.151.112 |      1772     |         37.7         |
|  144.120.175.80 |      553      |        11.77         |
+-----------------+---------------+----------------------+

```

### Delete Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py delete --name scan_two
Scan 'scan_two' deleted successfully
```

### Enable/Disable Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py info --name scan_one
Details for scan 'scan_one'


            * Enabled: True
            * Total run count: 35
            * Last run at: None
            * Target addresses: ['10.10.0.0/16', '192.168.0.0/16']
            * Target port: 12
            * Request Hexdump: abcabcabc
            * Cron: * * * * *
            
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py disable --name scan_one
Scan 'scan_one' disabled successfully
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py info --name scan_one
Details for scan 'scan_one'


            * Enabled: False
            * Total run count: 35
            * Last run at: None
            * Target addresses: ['10.10.0.0/16', '192.168.0.0/16']
            * Target port: 12
            * Request Hexdump: abcabcabc
            * Cron: * * * * *
            
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py enable --name scan_one
Scan 'scan_one' enabled successfully
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py info --name scan_one
Details for scan 'scan_one'


            * Enabled: True
            * Total run count: 35
            * Last run at: None
            * Target addresses: ['10.10.0.0/16', '192.168.0.0/16']
            * Target port: 12
            * Request Hexdump: abcabcabc
            * Cron: * * * * *
            
```
