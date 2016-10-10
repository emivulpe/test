from django.shortcuts import render
from bs4 import BeautifulSoup
import re
from HTMLParser import HTMLParser
import httplib
import urllib
import simplejson
import json
from django.http import HttpResponse

def index(request):
    """
    A view to render the home page
    :param request: the request
    :return: renders the index page
    """
    return render(request, 'mercurytide_app/index.html', {})
def create_report2(request):
    URL = request.POST['url']
    return HttpResponse(simplejson.dumps({'success': URL}), content_type="application/json")


def create_report(request):
    """
    A method to handle the post request and get all data needed to produce a report for the url of interest
    :param request: the request
    :return: HttpResponse containing the data for the report or an error message
    """
    print "in create report"
    try:
        # get the url of interest
        URL = request.POST['url']
        conn = httplib.HTTPSConnection(URL)
        print "try connection"
        conn.request("GET", "/")
        response = conn.getresponse()
        # ensure the url is reachable
        if response.status == 200:
            print "status ok"
            # initiate a context dict to pass to the report page
            report = {}
            # initiate the report variables
            page_contents = {}
            total_word_count = 0
            most_common_words = []

            # Custom HTML parser
            class PageHTMLParser(HTMLParser):

                def handle_data(self, data):
                    data_without_punctuation = re.sub(ur'[^\w\d\s]+', '', data)
                    word_list = data_without_punctuation.split()
                    for word in word_list:
                        if word in page_contents:
                            page_contents[word] = page_contents[word] + 1
                        else:
                            page_contents[word] = 1
            # parse the html
            print "before parsing"
            page_html = response.read()
            parser = PageHTMLParser()
            parser.feed(page_html)
            print "after parsing"
            # get the total count of words in the page
            for count in page_contents.itervalues():
                total_word_count += count

            report['total_word_count'] = total_word_count

            # get the count of unique words in the page
            unique_word_count = len(page_contents)
            report['unique_word_count'] = unique_word_count

            # Get the top 5 most common words
            page_contents_sorted = sorted(page_contents.items(), key = lambda x: x[1], reverse=True)

            top_word_index = 0
            while top_word_index < 5:
                most_common_words.append(page_contents_sorted[top_word_index][0])
                top_word_index += 1
            report['most_common_words'] = most_common_words

            # process the html with beautifulsoup4
            print "beautiful soup"
            soup = BeautifulSoup(page_html, 'html.parser')

            # get the title of the page
            title = soup.find('title').contents[0]
            report['title'] = title

            # get the list of the links
            page_links = []
            links = soup.find_all('a')
            for link in links:
                link_text = link.contents[0]
                the_link = link.get('href')
                new_link = (link_text, the_link)
                page_links.append(new_link)
            report['page_links'] = page_link

            # get a list of meta tags and the keywords that are not used in the content
            metatags = soup.find_all('meta')
            metatags_list = []
            keywords = []
            for tag in metatags:
                metatags_list.append((tag.get('name'), tag.get('content', 'No content')))
                if tag.get('name') == 'keywords':
                    keywords = tag.get('content')
                    keywords = keywords.split(',')

            keywords_not_in_content = set(keywords) - set(page_contents.keys())
            report['keywords'] = keywords_not_in_content

            # get the page size in octets
            print "before urllib"
            page = urllib.urlopen(URL)
            meta = page.info()
            page_size_octets = meta.getheaders("Content-Length")[0]
            print "after urllib"
            # convert the page size to KB
            human_readable_page_size = int(page_size_octets) * 8 / 1024 / 8
            report['page_size'] = human_readable_page_size

            return HttpResponse(simplejson.dumps({'success': report}), content_type="application/json")
        # return error
        else:
            return HttpResponse(simplejson.dumps({'error': 'The url does not exist'}), content_type="application/json")
    # return error
    except KeyError:
        return HttpResponse(simplejson.dumps({'error': 'Bad input supplied'}), content_type="application/json")
