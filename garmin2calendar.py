#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import argparse
import datetime
import os
import re
import time


os.environ['TZ'] = 'Europe/Warsaw'
time.tzset()

from datetime import date, timedelta


def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="be verbose")
    parser.add_argument("-d", "--debug",
                        action="store_true", help="be verbose")
    parser.add_argument("--calendar", help="Send event to this Apple Calendar",
                        default="Clocking life")

    parser.add_argument("file", help="", nargs='+')
    return parser


def insert_event(calendar, project, task, start, end):
    """Insert an event into calendar using Apple tell"""
    # you can use also activate, to move Calendar to the top
    cmd = """
    tell application \"Calendar\"
	tell calendar \"%s\"
        set theCurrentDate to (date "%s")
        set EndDate to (date "%s")
        make new event at end with properties {description:"%s", summary:"%s", start date:theCurrentDate, end date:EndDate}
	end tell
	reload calendars
    end tell""" % (calendar, start, end, '', task + ' (' + project + ')')
    #  summary:"[#A] Diet box <2018-09-28 Fri>(#health & #look :@health:)",
    # now the format is <task> (<project>)

    print(cmd)
    with open("/tmp/garmin2calendar.scpt", 'w') as f:
        f.write(cmd)
    os.system("osascript /tmp/garmin2calendar.scpt")
    print()
    
def hr(t):
    if t:
        print(t)
    print('-' * 80)
    
if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    logfn = os.path.basename('garmin2calendar.log')

    try:
        log = open(logfn)
    except:
        logs = []
    else:
        logs = log.read()
        log.close()

    for f in args.file:
        if 'summary.json' in f:
            pass
        else:
            continue

        hr(f)

        with open(f, "r") as read_file:
            data = json.load(read_file)

        if args.debug:
            print(data)
            print('Start', data['summaryDTO']['startTimeLocal'])
            print('Duration in min', data['summaryDTO']['movingDuration']/60)
            print('Calc', data['summaryDTO']['calories'])

        duration = timedelta(seconds = data['summaryDTO']['duration'])
        
        startdt = data['summaryDTO']['startTimeLocal'] # 2019-10-18T17:49:20.0
        start = datetime.datetime.strptime(startdt, '%Y-%m-%dT%H:%M:%S.%f')
        
        end = start + duration
        start2 = start.strftime("%A, %B %d, %Y %I:%M %p")
        end2  = end.strftime("%A, %B %d, %Y %I:%M %p")
        entrylog = data['activityName'] + ' ' + start2 + ' ' + end2

        if entrylog not in logs:
            insert_event(args.calendar, 'Sport', data['activityName'] + \
                         ' ' + str(int(data['summaryDTO']['calories'])) + ' kcal ' + \
                         '' + str(int(data['summaryDTO']['movingDuration']/60)) + \
                         '/'+ str(int(data['summaryDTO']['duration']/60)) + ' min', start2, end2)
            log = open(logfn, 'a')
            log.write(entrylog + '\n')
        else:
            if args.verbose:
                print('- already in your calendar: ' + entrylog)

    log.close()
            

