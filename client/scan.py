import configparser
import argparse
import requests
import sys

from prettytable import PrettyTable

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']

def pretty(d):
   for key, value in d.items():
      if isinstance(value, dict):
         pretty(value)
      elif isinstance(value, list):
          for v in value:
              print("* "+str(v))
      else:
         print("* "+str(value))


def process_result(result):
    status = result["status"]
    output = "\n\n----------------------------------------------------------\n\n"
    output += "* Status: %s\n" % status
    output += "* Created: %s\n" % result["created"]

    if status == "FAILURE":
        output += "* Traceback: %s" % result["traceback"]
    elif status == "SUCCESS":
        output += "* Number of Amplifiers: %s\n" % len(result["amplifiers"])

        table = PrettyTable()
        table.field_names = ["Amplifier", "Response Size", "Amplification Factor"]

        for ip, details in result["amplifiers"].items():
            table.add_row([ip, details["response_size"], details["amplification_factor"]])

        table.sortby = "Amplification Factor"
        # sort in descending order
        table.reversesort = True

        output += table.get_string()
    return output

parser = argparse.ArgumentParser()

parser.add_argument("type",
                    choices=("create",
                             "delete",
                             "list",
                             "info",
                             "result"))

parser.add_argument("--name",
                    help="set name of scan",)

parser.add_argument("--target-port",
                    help="port number to scan",)

parser.add_argument("--target-hosts",
                    help="Space separated list of target address ranges in CIDR notaion",
                    nargs='+',)

parser.add_argument("--request-payload",
                    help="HEX encoded request payload",)

parser.add_argument("--minute",
                    help="Minute field for Cron",
                    default="*")

parser.add_argument("--hour",
                    help="Hour field for Cron",
                    default="*")

parser.add_argument("--day-of-week",
                    help="Day of the week field for Cron",
                    default="*")

parser.add_argument("--day-of-month",
                    help="Day of the month field for Cron",
                    default="*")

parser.add_argument("--month-of-year",
                    help="Month of the year field for Cron",
                    default="*")

parser.add_argument("--latest",
                    help="Get n number of recent scan results")

args = parser.parse_args()

if args.type == "create":
    if not args.name:
        parser.error("scan create requires --name argument")

    if not args.target_port:
        parser.error("scan create requires --target-port argument")

    if not args.target_hosts:
        parser.error("scan create requires --target-hosts argument")

    if not args.request_payload:
        parser.error("scab create requires --request-payload argument")

    try:
        url = "http://%s:%s/api/v1/scan" % (HOST, PORT)
        params = dict()
        params['name'] = args.name

        params['scan_args'] = dict()
        params['scan_args']['address_range'] = ','.join(args.target_hosts)
        params['scan_args']['target_port'] = args.target_port
        params['scan_args']['request_hexdump'] = args.request_payload

        params['crontab'] = dict()
        params['crontab']['minute'] = args.minute
        params['crontab']['hour'] = args.hour
        params['crontab']['day_of_week'] = args.day_of_week
        params['crontab']['day_of_month'] = args.day_of_month
        params['crontab']['month_of_year'] = args.month_of_year


        res = requests.post(url, json=params)

        if res.status_code == 201:
            print("Scan '%s' created successfully" % args.name)
        else:
            print("Failed to create Scan '%s'\n" % args.name)
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "delete":
    if not args.name:
        parser.error("scan delete requires --name arguemt")

    try:
        url = "http://%s:%s/api/v1/scan/%s" % (HOST, PORT, args.name)
        res = requests.delete(url)
        if res.status_code == 204:
            print("Scan '%s' deleted successfully" % args.name)
        else:
            print("Failed to delete Scan '%s'\n" % args.name)
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "list":

    try:
        url = "http://%s:%s/api/v1/scan" % (HOST, PORT)
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            scan_names = ["* %s" % elem['name'] for elem in data]
            print("Scans List:\n")
            print("\n".join(scan_names))
        else:
            print("Failed to list scans\n")
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "info":
    if not args.name:
        parser.error("scan info requires --name arguemt")

    try:
        url = "http://%s:%s/api/v1/scan/%s" % (HOST, PORT, args.name)
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            print(data["enabled"])
            print("Details for scan '%s'\n" % args.name)
            output = ("""
            * Enabled: {0}
            * Total run count: {1}
            * Last run at: {2}
            * Target addresses: {3}
            * Target port: {4}
            * Request Hexdump: {5}
            * Cron: {6}
            """).format(data["enabled"],
                       data["total_run_count"],
                       data["last_run_at"],
                       data["scan_args_data"]["address_range"],
                       data["scan_args_data"]["target_port"],
                       data["scan_args_data"]["request_hexdump"],
                       data["scan_args_data"]["cron_str"])

            print(output)
        else:
            print("Failed to get info for scan '%s'\n" % args.name)
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "result":
    if not args.name:
        parser.error("scan result requires --name arguemt")

    try:
        url = "http://%s:%s/api/v1/scan/%s/result" % (HOST, PORT, args.name)
        if args.latest:
            url += "?latest=%s" % args.latest

        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if len(data) == 0:
                print("No results found for scan %s" % args.name)
            else:
                output = ""
                if isinstance(data, list):
                    for result in data:
                        output += process_result(result)
                else:
                    output += process_result(data)
                print(output)
        else:
            print("Failed to get result for scan '%s'\n" % args.name)
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
