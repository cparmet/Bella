# PAGE NUMBERS
# Notes:
# - If there is at least one page number, these functions add : before it.
# - u2013 is an enDash.

def make_stop_a_full_number(start, stop):
    # Page numbers are in style AAAA - B.
    # I need to convert to AAAA - BBBB.
    # I've already stripped whitespace, removed '-', and turned start and stop into integers.

    # Convert back to strings
    start, stop = str(start), str(stop)

    # If N = length of stop
    # We know that the value of stop is > value of last N digits in start.
    # So split start into its head digits that will be same in stop_new
    # And replace tail of start (lesser value) with (greater) value of stop.

    digits_in_stop = len(stop)
    head = start[0:-digits_in_stop]
    #     tail = start[-digits_in_stop:]
    stop_new = head + stop

    return str(stop_new)


def probe_and_process_pages_with_leading_letters(start, stop, comments):
    # We know there are two pages and start begins with a letter.
    # But is it in one of the four styles page numbers I can handle?
    #   [1] S178-9
    #   [2] S178-179
    #   [3] S178-S9
    #   [4] S178-S179 (what I want them all to look like)

    # Main use case is supplements. But also handles pages that begin with any letter, for example "e1765-88" [23184105].

    letter = start[0]

    if letter == 's':
        letter = letter.upper()  # capitalize S only, per HW citation rules for supplements.

    start = start[1:]  # Extract everything after the leading letter.

    try:
        start = int(start)  # Is everything after the letter an integer?

        try:
            stop = int(stop)  # Is the second page already an integer?

        except:
            # Nope, second page has letter(s) too. Can I safely convert it to an integer?

            # Does second page begin with same letter as first page did, like S?
            if stop[0] == letter:
                # Then style is [3] or [4]

                try:
                    stop = int(stop[1:])  # Is everything after the letter an integer?

                except:
                    # Second number begins with same letter, but it also has another non-integer character in there.
                    # I can't handle those situations (can't do the start - stop subtraction).
                    # But I'll add the letter back to start, and convert the dash to an endash.
                    pages_new = ': ' + letter + start + u'\2013' + stop
                    return pages_new, comments
            else:
                # Second page isn't an integer AND doesn't begin with an S.
                # So I can't handle this situation (can't do the start - stop subtraction).
                # But I know first page is S### (no other letters).
                # So I feel safe -- will test this to confirm -- adding S before second page.
                # And will convert dash to endash
                pages_new = ': ' + letter + start + u'\2013' + letter + stop
                return pages_new, comments

        # Ok, if we're still here:
        #  * We're in one of the four styles we can do start-stop on.
        #  * And start & stop are both integers at this point.

        if (start - stop) > 0:  # By my hypothesis, this means it's styles [1] or [3]
            # Convert stop to full number, HW style.
            stop = make_stop_a_full_number(start, stop)

        # Else: It's style [2] or [4]. Stop is already a full number.

        # In either case: Add the Ss (back) in, and convert dash to endash.
        pages_new = ': ' + letter + str(start) + u'\u2013' + letter + str(stop)

    except:
        # There's a non-integer character after the S.
        comments.append("I don't understand the page numbering. I'm a golden retriever.")
        pages_new = ': ' + pages_old

    return pages_new, comments


def format_pages(record, comments):
    try:
        pages_old = record['Pages']
    except:
        pages_old = ''

    pages_old = pages_old.replace(" ", "")  # Remove any white space

    try:
        # Is it a range of two pages?
        start, stop = pages_old.split('-')

        try:
            # Are they both integers?
            start = int(start)
            stop = int(stop)

            # Do we need to convert page style from AAAA-B to AAAA-BBBB?
            # My hypothesis: If we need to convert, AAAA minus B will be positive. Because AAAA>B.

            if (start - stop) > 0:
                # Convert stop to HW style:
                stop = make_stop_a_full_number(start, stop)
                pages_new = ': ' + str(start) + u'\u2013' + str(stop)

            # If it's already formatted correctly, AAAA minus BBBB will be negative.
            # Also, if the difference is 0, I can't imagine why, but let's handle it gracefully.
            elif (start - stop) <= 0:
                pages_new = ': ' + pages_old

        except:
            # There are two pages, but they're not integers
            # Let's probe to see if they're in a workable style, like supplements for example, S65-67 or S65-S67.
            # Does first page begin with a letter?
            try:
                int(start[0])

                # If that worked, first character is a number, not a letter.
                # Which means the letter is somewhere else in the page number.
                # Maybe the letter is after the number. page 37A.

                # Not a style I can do anything with.

                comments.append('Please double check how I numbered the pages. Woof.')
                pages_new = ': ' + pages_old

            except:
                # If we're here, the first character is a letter.

                pages_new, comments = probe_and_process_pages_with_leading_letters(start, stop, comments)

    except:
        if pages_old == '':  # No pages?
            pages_new = ''
        else:  # Treat it as one page.
            pages_new = ': ' + pages_old

    return pages_new, comments