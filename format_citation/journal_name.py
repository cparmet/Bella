import pandas as pd
from titlecase import titlecase

def format_journal(record, comments):
    try:
        journal = record['FullJournalName']
    except:
        journal = ''
        comments.append("I couldn't find the journal name.")

    # Format select journal names.

    # PubMed gives you two options:
    # - Regular abbreviated journal name: too abbreviated
    # - FullJournalName: sometimes works for HW style,
    #   but other times it's too long. Like Heart (British Cardiac Society).
    # We'll start with FullJournalName and use a XLSX table of common journals
    #   whose names we know we need to change.
    # It won't catch 'em all, but it's a start.

    ## NOTES:
    # 1. XLSX is a public AWS S3 file.
    # 2. This XLSX also makes this HW-specific style change:
    #  - from: The New England journal of medicine
    #  - to: New England Journal of Medicine

    xls_url = 'https://s3.amazonaws.com/bella_zappa_S3bucket/static/Journal_names_map.xlsx'
    journal_map = pd.read_excel(xls_url).drop_duplicates()
    match = journal_map.ix[journal_map['PubMed_name'] == journal]['HW_style']
    if not match.isnull().all():
        journal = match.head(1).values[0]
    else:
        journal = titlecase(journal)

    journal = titlecase(journal)

    return journal, comments
