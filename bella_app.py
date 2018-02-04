from flask import Flask, redirect, render_template, request, url_for
import retrieve_citation as rc

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []
citation = ""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        global comments
        global citation

        comments_to_display = list(comments) # "list" here just means copy to new list, before we reset it.
        citation_to_display = citation

        comments = [] # Reset for next round
        citation = "" # ''

        return render_template("main_page.html", comments=comments_to_display, citation=citation_to_display)

    if request.method == 'POST':

        lookup_ID = request.form["lookup_ID"]

        # Gracefully handle blank search.
        if lookup_ID =='':
            comments.append("Please enter an ID.")
            return redirect(url_for('index'))

        # Validate ID. If PMID, confirm it exists. If DOI, convert to PMID.
        PMID_result, comments = rc.validate_and_convert_DOI_or_PMID_to_PMID(lookup_ID, comments)

        # If PMID exists, fetch citation.
        if PMID_result != '':
            citation, comments = rc.PMID_to_HW_citation(PMID_result, comments)
        else:
            citation = ""

        # This tells browser "Please request this page again, this time using a 'GET' method", so that the user can see the results of their post
        return redirect(url_for('index'))

@app.route("/chrome")
def from_chrome():
    lookup_ID = request.args['id']

    global comments
    global citation

    ## REST OF THIS ROUTE'S CODE IS SAME AS POST ABOVE

    # Gracefully handle blank search.
    if lookup_ID == '':
        comments.append("I didn't get an article ID to search for.")
        return redirect(url_for('index'))

    # Validate ID. If PMID, confirm it exists. If DOI, convert to PMID.
    PMID_result, comments = rc.validate_and_convert_DOI_or_PMID_to_PMID(lookup_ID, comments)

    # If PMID exists, fetch citation.
    if PMID_result != '':
        citation, comments = rc.PMID_to_HW_citation(PMID_result, comments)
    else:
        citation = ""

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()