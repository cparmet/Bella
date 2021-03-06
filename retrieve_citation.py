import Entrez
import re
from datetime import date
import datetime
from format_citation import article_title, authors, DOI, errata, journal_name, page_numbers, volume_issue, accessed_date
from flask import current_app as app

def PMID_to_formatted_citation(PMID, comments):
    """
    Take a PMID, retrieve the PubMed data, and format it based on our style guide.
    :param PMID: PubMed ID
    :return:
    """
    Entrez.email = app.config['EMAIL']

    try:
        handle = Entrez.esummary(db="pubmed", id=PMID)
        record = Entrez.read(handle)[0]
    except IOError:
        comments.append("Is there a network problem? Unleash me please!") # Network error
        return '', comments
    except:
        comments.append("I can't fetch an article with that ID.") # DOI not on PubMed? Or Bad PMID?
        comments.append("Try looking up the article on www.pubmed.gov. (Note: PubMed may not have the DOI.) If the article is there, copy its PMID and bring it to me. If the article isn't on PubMed, I can't fetch a citation for you. Sorry. :( ")
        return '', comments

    author_names = authors.format_authors(record)

    try:
        year = record['PubDate'][0:4]
    except:
        comments.append("What year is it?")
        year = '20??'

    title, comments = article_title.format_title(record, PMID, comments)
    journal, comments = journal_name.format_journal(record, comments)
    vol_iss, comments = volume_issue.format_volume_issue(record, comments)
    pages, comments = page_numbers.format_pages(record, comments)
    DOI_value, comments = DOI.format_DOI(record, comments)
    accessed = accessed_date.format_accessed_date()

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
        Entrez.email = app.config['EMAIL']
        handle = Entrez.esearch(db="pubmed", retmax=10, term=lookupID)
        record = Entrez.read(handle)
        handle.close()
        if int(record['Count']) == 0:
            comments.append("I can't fetch an article with that ID.")  # DOI not on PubMed? Or Bad PMID?
            comments.append("Try looking up the article on www.pubmed.gov. (Note: PubMed may not have the DOI.) If the article is there, copy its PMID and bring it to me. If the article isn't on PubMed, I can't fetch a citation for you. Sorry. :( ")
            return '', comments
        elif int(record['Count']) > 1:
            comments.append('I found more than one article. Are there characters missing from the ID?')
            return '', comments
        else:  # Only 1 result, perfect!
            return (record['IdList'][0]), comments
    except IOError: # Network error
        comments.append("Is there a network problem? Unleash me please!") # Network error
        return '', comments
    except:
        comments.append("I can't fetch an article with ID " + lookupID + '. Can you double check it?')  # Bad PMID?
        comments.append("Try looking up the article on www.pubmed.gov. (Note: PubMed may not have the DOI.) If the article is there, copy its PMID and bring it to me. If the article isn't on PubMed, I can't fetch a citation for you. Sorry. :( ")
        return '', comments
