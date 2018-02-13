def format_DOI(record, comments):
    # Includes here the extra space after the period. In case there is no DOI.

    try:
        DOI = record['DOI']
        DOI = 'DOI: ' + DOI + '. '

    # Key error: No DOI data.
    except:
        DOI = ''
        comments.append("I couldn't find a DOI. Please add the URL of the article.")

    # And what if DOI key did pull a result, but it was blank? Not sure this will happen, but in case it does...
    if DOI == 'DOI: ':
        comments.append("I couldn't find a DOI. Please add the URL of the article.")

    return DOI, comments