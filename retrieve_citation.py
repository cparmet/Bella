from Bio import Entrez
import re
from datetime import date
import datetime
from format_citation import article_title, authors, DOI, errata, journal_name, page_numbers, volume_issue


def PMID_to_HW_citation(PMID, comments):
    """
    Take a PMID, retrieve the PubMed data, and convert it to a Healthwise formatted citation.
    :param PMID: PubMed ID
    :return:
    """
    Entrez.email = 'cparmet@healthwise.org'

    try:
        handle = Entrez.esummary(db="pubmed", id=PMID)
        record = Entrez.read(handle)[0]
    except IOError:
        comments.append("Bark: I can't get to PubMed.gov. Is it a network problem? I'm leashed!") # Network error
        return '', comments
    except:
        comments.append("Bark: Error fetching that article.") # Bad PMID?
        return '', comments

    author_names = authors.format_authors(record)

    try:
        year = record['PubDate'][0:4]
    except:
        comments.append("Bark: What year is it?")
        year = '20??'

    title = article_title.format_title(record)
    journal, comments = journal_name.format_journal(record, comments)
    vol_iss, comments = volume_issue.format_volume_issue(record, comments)
    pages, comments = page_numbers.format_pages(record, comments)
    DOI_value, comments = DOI.format_DOI(record, comments)
    # The hashtag in "%#d" strips leading 0s, so day 01 formats as 1. Thanks, StackOverflow.
    accessed = 'Accessed ' + '{:%B %#d, %Y}'.format(date.today()) + '.'

    # When there's no author: Title (Year)...
    if author_names == '':
        if title[-1] == '.':
            title = title[0:-1]
        citation = title + ' (' + year + '). ' + journal + vol_iss + pages + '. ' + DOI_value + accessed

    # Otherwise: Authors (Year). Title...
    else:
        citation = author_names + ' (' + year + '). ' + title + ' ' + journal + vol_iss + pages + '. ' + DOI_value + accessed

    # print(citation)
    # print(' ')
    comments = errata.erratum_check(PMID, comments)
    handle.close()
    return citation, comments


def validate_and_convert_DOI_or_PMID_to_PMID(lookupID, comments):
    """
    Look up a DOI -- or PMID -- and return a PMID.
    :param lookupID: either a DOI or a PMID.
    :return a PMID
    """

    # Format as string and strip any leading white spaces. Do now so we can reach DOI/PMIDs.
    lookupID = str(lookupID).lstrip()

    # Remove any prefacing text that might've come through. Only if it's at the start of the lookupID.
    preface_tags = ['DOI:', 'doi:', 'PMID:', 'pmid:']
    for tag in preface_tags:
        if lookupID.startswith(tag):
            lookupID = re.sub(tag, '', lookupID)

    # Drop any white spaces that remain.
    lookupID = lookupID.replace(" ", "")

    try:
        Entrez.email = "cparmet@healthwise.org"
        handle = Entrez.esearch(db="pubmed", retmax=10, term=lookupID)
        record = Entrez.read(handle)
        handle.close()
        if int(record['Count']) == 0:
            comments.append("Bark: I can't find it.")
            return '', comments
        elif int(record['Count']) > 1:
            comments.append('Bark: I got more than one article. I can only fit one in my mouth at a time, woof.')
            return '', comments
        else:  # Only 1 result, perfect!
            return (record['IdList'][0]), comments
    except:
        comments.append("Bark: I can't find it.")
        return '', comments
