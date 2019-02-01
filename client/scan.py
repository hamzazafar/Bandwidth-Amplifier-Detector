import configparser
import argparse
import requests
import sys
import json

from prettytable import PrettyTable

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']

def pretty(d):
   if not isinstance(d, dict):
       return

   for key, value in d.items():
      if isinstance(value, dict):
         pretty(value)
      elif isinstance(value, list):
          for v in value:
              print("* %s: %s" % (str(key),str(v)))
      else:
         print("* "+str(value))


def process_result(result):
    status = result["status"]
    output = "\n* Status: %s\n" % status
    output += "* Created: %s\n" % result["created"]

    if status == "FAILURE":
        output += "* Traceback: %s" % result["traceback"]
    elif status == "SUCCESS":
        output += "* Number of Amplifiers: %s\n" % len(result["amplifiers"])

        table = PrettyTable()
        table.field_names = ["Amplifier", "Response Size", "Amplification Factor"]

        for ip, details in result["amplifiers"].items():
            table.add_row([ip, details["total_response_size"], details["amplification_factor"]])

        table.sortby = "Amplification Factor"
        # sort in descending order
        table.reversesort = True

        output += table.get_string()
        output += "\n"
    return output

parser = argparse.ArgumentParser()

parser.add_argument("type",
                    choices=("create",
                             "delete",
                             "update",
                             "list",
                             "info",
                             "result",
                             "disable",
                             "enable",
                             "list-running",
                             "kill"))

parser.add_argument("--name",
                    help="set name of scan",)


parser.add_argument("--rate",
                    help="Set send rate in packets/sec",)

parser.add_argument("--target-port",
                    help="port number to scan",)

parser.add_argument("--target-hosts",
                    help="Space separated list of target address ranges in CIDR notaion",
                    nargs='+',)

parser.add_argument("--target-hosts-file",
                    help="path to file containing address ranges, one on every line")

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
                    help="Get n number of latest scan results")

parser.add_argument("--task-id",
                    help="Task ID of the scan job")

args = parser.parse_args()

if args.type == "create":
    errors = ""
    if not args.name:
        errors += "scan create requires --name argument\n"

    if not args.target_port:
        errors += "scan create requires --target-port argument\n"

    if not (args.target_hosts or args.target_hosts_file):
        errors += "scan create requires --target-hosts or target-hosts-file argument\n"

    if args.target_hosts_file and args.target_hosts:
        parser.error("pass one of target-hosts-file or target-hosts argument but not both")

    if not args.request_payload:
        errors += "scan create requires --request-payload argument\n"

    if errors:
        parser.error(errors)

    try:
        url = "http://%s:%s/api/v1/scan" % (HOST, PORT)
        params = dict()
        params['name'] = args.name

        params['scan_args'] = dict()
        target_hosts_list = []
        if args.target_hosts_file:
            with open(args.target_hosts_file) as f:
                target_hosts_list = [line.rstrip('\n') for line in f]
        else:
            target_hosts_list = args.target_hosts

        params['scan_args']['address_range'] = ','.join(target_hosts_list)
        params['scan_args']['target_port'] = args.target_port
        params['scan_args']['request_hexdump'] = args.request_payload

        if args.rate:
            params['scan_args']['packets_per_second'] = args.rate

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
            print("Details for scan '%s'\n" % args.name)
            output = "* Enabled: {0}\n" \
                     "* Total run count: {1}\n" \
                     "* Last run at: {2}\n" \
                     "* Target addresses: {3}\n" \
                     "* Target port: {4}\n" \
                     "* Request Hexdump: {5}\n" \
                     "* Cron: {6}\n" \
                     "* Rate: {7}\n" \
                     .format(data["enabled"],
                             data["total_run_count"],
                             data["last_run_at"],
                             data["scan_args_data"]["address_range"],
                             data["scan_args_data"]["target_port"],
                             data["scan_args_data"]["request_hexdump"],
                             data["scan_args_data"]["cron_str"],
                             data["scan_args_data"]["packets_per_second"])

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
                output = "\n"
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

elif args.type == "disable" or args.type == "enable":
    if not args.name:
        parser.error("scan %s requires --name arguemt" % args.type)

    try:
        url = "http://%s:%s/api/v1/scan/%s" % (HOST, PORT, args.name)

        data = dict()
        data["enabled"] = False if args.type == "disable" else True
        res = requests.put(url, json=data)
        if res.status_code == 200:
            print("Scan '%s' %sd successfully" % (args.name, args.type))
        else:
            print("Failed to %s scan '%s'\n" % (args.type, args.name))
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "update":
    if not args.name:
        parser.error("scan update requires --name argument")

    if args.target_hosts_file and args.target_hosts:
        parser.error("pass one of target-hosts-file or target-hosts argument but not both")

    try:
        url = "http://%s:%s/api/v1/scan/%s" % (HOST, PORT, args.name)
        params = dict()
        params['scan_args'] = dict()

        target_hosts_list = []
        if args.target_hosts_file:
            with open(args.target_hosts_file) as f:
                target_hosts_list = [line.rstrip('\n') for line in f]
        else:
            target_hosts_list = args.target_hosts

        params['scan_args']['address_range'] = ','.join(target_hosts_list)

        if args.target_port:
            params['scan_args']['target_port'] = args.target_port

        if args.request_payload:
            params['scan_args']['request_hexdump'] = args.request_payload

        if args.rate:
            params['scan_args']['packets_per_second'] = args.rate

        params['crontab'] = dict()

        if args.minute:
            params['crontab']['minute'] = args.minute

        if args.hour:
            params['crontab']['hour'] = args.hour

        if args.day_of_week:
            params['crontab']['day_of_week'] = args.day_of_week

        if args.day_of_month:
            params['crontab']['day_of_month'] = args.day_of_month

        if args.month_of_year:
            params['crontab']['month_of_year'] = args.month_of_year

        res = requests.put(url, json=params)

        if res.status_code == 200:
            print("Scan '%s' updated successfully" % args.name)
        else:
            print("Failed to update Scan '%s'\n" % args.name)
            print("Errors:")
            pretty(res.json())
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "list-running":

    try:
        url = "http://%s:%s/api/v1/scan/running" % (HOST, PORT)
        res = requests.get(url)
        data = res.json()

        if len(data) == 0:
            print("No running scans found")
        else:
            for obj in data:
                print("\nTask ID: %s\nScan Args: %s\n" %(obj["id"], obj["kwargs"]))

    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

elif args.type == "kill":
    if not args.task_id:
        parser.error("scan kill requires --task-id argument")

    try:
        url = "http://%s:%s/api/v1/scan/revoke/%s" % (HOST, PORT, args.task_id)
        res = requests.get(url)
        if res.status_code == 200:
            print("Task '%s' is killed successfully" % args.task_id)
        else:
            print("Failed to kill task '%s'\n" % args.task_id)
            print("Errors:")
            pretty(res.json())

    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

