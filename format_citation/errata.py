import Entrez

def erratum_check(PMID, comments):
    """ Does this PMID have an erratum?
    I can't do the erratum formatting automatically.
    But I can warn user that there is an erratum.
    """

    Entrez.email = 'cparmet@healthwise.org'
    handle = Entrez.efetch(db="pubmed", id=PMID, rettype="gb", retmode="xml")
    records = Entrez.read(handle)

    erratum_count = 0
    try:
        corrections = records['PubmedArticle'][0]['MedlineCitation']['CommentsCorrectionsList']
        for correction in corrections:
            if correction.attributes['RefType'] == 'ErratumIn':
                if erratum_count == 0:
                    comments.append("I smell an erratum, but I can't fetch it.: " + correction['RefSource'] +
                          ". \nAdd it to the end of your citation: [Erratum in Journal, Issue(Volume): page. DOI: #. Accessed date.]")
                else:  # Is this the second (or later) erratum we're reporting for this article? Then shorten report.
                    comments.append("There's another erratum! What a mess." + correction['RefSource'])

                erratum_count += 1

    except:
        pass  # No errata? Do nothing.

    return comments