from datetime import date
import datetime


def format_volume_issue(record, comments):
    try:
        volume = record['Volume']
    except:
        volume = ''
    try:
        issue = record['Issue']
    except:
        issue = ''

    # Supplement style? As in ADA.
    suppl_split = volume.lower().split('suppl')  # First, try to split the string before and after suppl (lowercased)
    if len(suppl_split) == 2:  # This means there was a suppl in there, because two pieces came out of the split.
        volume = suppl_split[0] + '(Suppl' + suppl_split[1] + ')'  # Format as #1(Suppl#2)
        volume = volume.replace(" ", "")  # Remove whitespace

    # If there's a volume nummber, add a leading comma and space to put ,# betwee journal and volume.
    if volume != '':
        volume = ', ' + volume

    # If there's an issue, put it in parentheses.
    if issue != '':
        issue = '(' + issue + ')'

    volume_issue = volume + issue

    # Check for EPub
    if volume_issue == '' and record['EPubDate'] != '':

        try:
            epubdate = datetime.datetime.strptime(record['EPubDate'], '%Y %b %d').strftime('%B %e %Y')

            # If I only use that formula, I get inconsistent spacing.
            # Some PMIDs, not all, add an extra space. 29270635 29270634
            # Let's break it up manually:

            components = epubdate.split(' ')
            if '' in components:  # If there are any list items
                components.remove('')
            try:
                month, day, year = components
                volume_issue = ', published online ' + month + ' ' + day + ', ' + year
            except:
                comments.append("Please double check the 'published online' date.")
        except:
            comments.append("Please double check the 'published online' date.")

    return volume_issue, comments
