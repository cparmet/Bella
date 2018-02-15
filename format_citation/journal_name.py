import pandas as pd
from titlecase import titlecase


def format_journal(record, comments):
    try:
        journal = record['FullJournalName']
    except:
        journal = ''
        comments.append("I couldn't find the name of the journal.")

    # Format select journal names.

    # PubMed gives you two options:
    # - Regular abbreviated journal name: too abbreviated
    # - FullJournalName: sometimes works for our style guide,
    #   but other times it's too long. Like Heart (British Cardiac Society).
    # We'll start with FullJournalName and use a XLSX table of common journals
    #   whose names we know we need to change.
    # It won't catch 'em all, but it's a start.

    ## NOTES:
    # 1. XLSX is a public AWS S3 file.

    xls_url = 'https://s3.amazonaws.com/bella_zappa_S3bucket/static/Journal_names_map.xlsx'
    journal_map = pd.read_excel(xls_url).drop_duplicates()
    # Lowercase everything
    journal_map[' _title'] = journal_map['PubMed_title'].apply(str.lower)

    # Check if the lowercase version of Journal matches anything in the journal_map dataframe
    match = journal_map.ix[journal_map['PubMed_title'] == journal.lower()]['Formatted_title']
    if not match.isnull().all():
        journal = match.head(1).values[0]
    else:
        # Replace ampersand with and
        journal = journal.replace(' & ', ' and ')  # Field & Stream -> Field and Stream
        journal = journal.replace(' &', ' and ')  # Field &Stream -> Field and Stream
        journal = journal.replace('& ', ' and ')  # Field& Stream -> Field and Stream
        journal = journal.replace('&', ' and ')  # Field&Stream -> Field and Stream

        # If first word is 'The_', drop it
        if journal[0:4] == 'The ':
            journal = journal[4:]

        # Title Case it
        # This function will not capitalize "small words" from New York Times Manual of Style
        journal = titlecase(journal)

        # A post-Titlecase fix: That package capitalizes "nor", "off", "out", "up", but our style guide does not.
        # But cannot imagine a journal title with "nor" in the name!!
        journal = journal.replace(' Nor ', ' nor ')
        journal = journal.replace(' Nor,', ' nor,')
        journal = journal.replace(', Nor ', ', nor ')
        journal = journal.replace(',Nor ', ', nor ')

        journal = journal.replace(' Off ', ' off ')
        journal = journal.replace(' Off,', ' off,')
        journal = journal.replace(', Off ', ', off ')
        journal = journal.replace(',Off ', ', off ')

        journal = journal.replace(' Out ', ' out ')
        journal = journal.replace(' Out,', ' out,')
        journal = journal.replace(', Out ', ', out ')
        journal = journal.replace(',Out ', ', out ')

        journal = journal.replace(' Up ', ' up ')
        journal = journal.replace(' Up,', ' up,')
        journal = journal.replace(', Up ', ', up ')
        journal = journal.replace(',Up ', ', up ')

    return journal, comments

