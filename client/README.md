## Client usage examples:

Make sure the virtual environment is activated before accessing the client.

### Print help:
```
usage: scan.py [-h] [--name NAME] [--rate RATE] [--target-port TARGET_PORT]
               [--target-hosts TARGET_HOSTS [TARGET_HOSTS ...]]
               [--target-hosts-file TARGET_HOSTS_FILE]
               [--request-payload REQUEST_PAYLOAD] [--minute MINUTE]
               [--hour HOUR] [--day-of-week DAY_OF_WEEK]
               [--day-of-month DAY_OF_MONTH] [--month-of-year MONTH_OF_YEAR]
               [--latest LATEST] [--task-id TASK_ID] [--raw]
               {create,delete,update,list,info,result,disable,enable,list-running,kill}

positional arguments:
  {create,delete,update,list,info,result,disable,enable,list-running,kill}

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           set name of scan
  --rate RATE           Set send rate in packets/sec
  --target-port TARGET_PORT
                        port number to scan
  --target-hosts TARGET_HOSTS [TARGET_HOSTS ...]
                        Space separated list of target address ranges in CIDR
                        notaion
  --target-hosts-file TARGET_HOSTS_FILE
                        path to file containing address ranges, one on every
                        line
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
  --latest LATEST       Get n number of latest scan results
  --task-id TASK_ID     Task ID of the scan job
  --raw                 print raw json data
```

### Create Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py  create --name scan_two \
                                                                    --target-port 12 \
                                                                    --target-hosts 10.10.0.0/16 192.168.0.0/16 \
                                                                    --request-payload abcabcabc \
                                                                    --minute "*/2"
								    --rate 1024
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
	    * Rate: 1024
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


### Get RAW JSON data
```
(git)-[master] # python scan.py result --name scan_dns_any_query --latest=2 --raw

[
    {
        "active_amplifiers_count": 1,
        "amplifiers": {
            "129.187.88.248": {
                "amplification_factor": 12.56,
                "destination_address": "138.246.253.7",
                "private_address": false,
                "responses": [
                    {
                        "response_dport": 59357,
                        "response_hex_data": "17ea83800001000e0000000106676f6f676c6503636f6d0000ff0001c00c00010001000001000004acd9108ec00c00020001000000010006036e7334c00cc00c00020001000000010006036e7333c00cc00c00020001000000010006036e7332c00cc00c00020001000000010006036e7331c00cc00c000f00010000004a0011001e04616c7432056173706d78016cc00cc00c000f00010000004a0009001404616c7431c087c00c000f00010000004a0009003204616c7434c087c00c000f00010000004a0009002804616c7433c087c00c000f00010000004a0004000ac087c00c00100001000000a7004140676c6f62616c7369676e2d736d696d652d64763d434459582b584648557732776d6c362f4762382b353942734833314b7a55723663316c32425076714b58383dc00c00100001000000a7003c3b66616365626f6f6b2d646f6d61696e2d766572696669636174696f6e3d3232726d3535316375346b3061623062787377353336746c647334683935c00c00100001000000a7002e2d646f63757369676e3d30353935383438382d343735322d346566322d393565622d616137626138613362643065c00c00100001000000a7002423763d7370663120696e636c7564653a5f7370662e676f6f676c652e636f6d207e616c6c0000290fa0000000000000",
                        "response_ipid": 25040,
                        "response_size": 490,
                        "response_sport": 53,
                        "response_ttl": 125
                    }
                ],
                "total_response_size": 490,
                "unsolicited_response": false
            }
        },
        "created": "2019-03-05T13:16:59.793180Z",
        "scan_name": "scan_dns_any_query",
        "status": "SUCCESS",
        "traceback": null
    },
    {
        "active_amplifiers_count": 1,
        "amplifiers": {
            "129.187.88.248": {
                "amplification_factor": 12.56,
                "destination_address": "138.246.253.7",
                "private_address": false,
                "responses": [
                    {
                        "response_dport": 53619,
                        "response_hex_data": "17ea83800001000e0000000106676f6f676c6503636f6d0000ff0001c00c00010001000000f80004acd9108ec00c00020001000000380006036e7334c00cc00c00020001000000380006036e7331c00cc00c00020001000000380006036e7333c00cc00c00020001000000380006036e7332c00cc00c000f00010000019a0011001404616c7431056173706d78016cc00cc00c000f00010000019a0009003204616c7434c087c00c000f00010000019a0004000ac087c00c000f00010000019a0009002804616c7433c087c00c000f00010000019a0009001e04616c7432c087c00c001000010000009c004140676c6f62616c7369676e2d736d696d652d64763d434459582b584648557732776d6c362f4762382b353942734833314b7a55723663316c32425076714b58383dc00c001000010000009c002e2d646f63757369676e3d30353935383438382d343735322d346566322d393565622d616137626138613362643065c00c001000010000009c002423763d7370663120696e636c7564653a5f7370662e676f6f676c652e636f6d207e616c6cc00c001000010000009c003c3b66616365626f6f6b2d646f6d61696e2d766572696669636174696f6e3d3232726d3535316375346b3061623062787377353336746c6473346839350000290fa0000000000000",
                        "response_ipid": 25041,
                        "response_size": 490,
                        "response_sport": 53,
                        "response_ttl": 125
                    }
                ],
                "total_response_size": 490,
                "unsolicited_response": false
            }
        },
        "created": "2019-03-06T01:16:59.788859Z",
        "scan_name": "scan_dns_any_query",
        "status": "SUCCESS",
        "traceback": null
    }
]
```

### Delete Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py delete --name scan_two
Scan 'scan_two' deleted successfully
```

### Updating a Scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py update --name scan_one --target-hosts 10.0.0.0/16 \
										   --target-port 54 \
                                                                                   --request-payload aaaaa \
                                                                                   --minute "*/3"
										   --rate 123
Scan 'scan_one' updated successfully
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
	    * Rate: 123
            
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
	    * Rate: 123
            
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
	    * Rate: 123
         
```



### Killing a running scan:
```
(thesis) hamza@hamza:~/master-thesis/client$ python scan.py list-running

Task ID: e6bde8ae-1ba2-4313-b766-a0bcb1dbc225
Scan Args: {'scan_name': 'scan_two', 'address_range': ['10.10.0.0/24', '10.0.0.0/8'], 'target_port': 23, 'request_hexdump': 'sdfksopdkf', 'cron_str': '* * * * *', 'version': 4}

(thesis) hamza@hamza:~/master-thesis/client$ python scan.py kill --task-id e6bde8ae-1ba2-4313-b766-a0bcb1dbc225
Task 'e6bde8ae-1ba2-4313-b766-a0bcb1dbc225' is killed successfully
```
Caveat: Run the command ```python scan.py list-running``` 3-4 times, you will see an exception at first but eventually get the result in 3rd or 4th try. 
