from datetime import date
import datetime
from pytz import timezone

def accessed_today_mountain_time():
    ''' Return the phrase about Accessed date.
        Use Mountain Time.
        When the Flask App is run on the AWS server, date.today will return date in UTC.
        So we need to pick a timezone.
    '''

    # todays_date = '{:%B %#d, %Y}'.format(date.today())
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_mountain = now_utc.astimezone(timezone(zone='US/Mountain'))

    # The hashtag in "%#d" method works locally, but not when deployed on Lambda
    #   is supposed to strip leading 0s, so day 01 formats as 1.
    #   Not sure why it works in local test code but on AWS, it comes out as 01.
    #   So I brute force the format
    # now_mountain = '{:%B %#d, %Y}'.format(now_mountain)
    formatted_date = '{:%B}'.format(now_mountain) + ' ' + str(now_mountain.day) + ', ' + str(now_mountain.year)

    accessed = 'Accessed ' + formatted_date + '.'
    return accessed
