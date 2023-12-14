import json
import everytime

from convert import Convert
def lambda_handler(event, context):
    result = get_ics_str(event['id'], event['begin'], event['end'])
    return {
        'statusCode': 200,
        'body': result.decode('utf-8')
    }


def get_ics_str(every_time_id, begin, end):
    e = everytime.Everytime(every_time_id)
    xml = e.get_timetable()
    c = Convert(xml)
    cal = c.get_calendar(c.get_subjects(), begin, end)
    return cal.to_ical()
