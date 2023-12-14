# -*- coding: utf8 -*-
__author__ = "Hoseong Son <me@sookcha.com>"

import datetime
import xml.etree.ElementTree as ElementTree
from dateutil import parser
from icalendar import Calendar, Event
import uuid
import requests


class Convert():
    def __init__(self, filename):
        self.filename = filename

    def get_subjects(self):
        result = []
        try:
            tree = ElementTree.parse(self.filename)
            root = tree.getroot()
        except:
            tree = ElementTree.fromstring(self.filename)
            root = tree

        for subject in root.iter('subject'):
            name = subject.find("name").get("value")
            single_subject = {}

            single_subject["name"] = name
            single_subject["professor"] = subject.find("professor").get("value")
            single_subject["info"] = list(map(
                lambda x: {
                    "day": x.get("day"),
                    "place" : x.get("place"),
                    "startAt": '{:02d}:{:02d}'.format(*divmod(int(x.get("starttime")) * 5, 60)),
                    "endAt": '{:02d}:{:02d}'.format(*divmod(int(x.get("endtime")) * 5, 60))
                }, subject.find("time").findall("data")
                )
            )
            result.append(single_subject)

        return result

    def get_calendar(self, timetable, start_date, end_date, hide_details=False):
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', 'Naver Calendar')
        for item in timetable:
            for time in item["info"]:
                event = Event()
                event.add('summary', item["name"] if not hide_details else "수업")
                event.add('uid', uuid.uuid4().hex)
                event.add('dtstart', parser.parse("%s %s" % (self.get_nearest_date(start_date, time["day"]), time["startAt"])))
                event.get('dtstart').params['TZID'] = 'Asia/Seoul'
                event.add('dtend', parser.parse("%s %s" % (self.get_nearest_date(start_date, time["day"]), time["endAt"])))
                event.add('rrule', {'freq': 'WEEKLY', 'until': parser.parse(end_date)})
                if time["place"] != "" and not hide_details:
                    event.add('location', time["place"])
                cal.add_component(event)

        return cal
    
    def export_calender_as_ics(self, cal, path):
        with open(path, 'wb') as f:
            f.write(cal.to_ical())

    def get_nearest_date(self, start_date, weekday):
        start_date = parser.parse(start_date)
        weekday = int(weekday)

        if start_date.weekday() >= weekday:
            if start_date.weekday() > weekday: start_date += datetime.timedelta(days=7)
            start_date -= datetime.timedelta(start_date.weekday() - weekday)
        else:
            start_date += datetime.timedelta(weekday - start_date.weekday())

        return start_date
