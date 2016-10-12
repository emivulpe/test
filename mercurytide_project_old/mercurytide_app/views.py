from django.shortcuts import render
from bs4 import BeautifulSoup
import re
import urllib2
from HTMLParser import HTMLParser
import httplib
import urllib
import simplejson
import json
from django.http import HttpResponse
import htmllib
import formatter

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

        # do some url validations
        URL.replace('https://', '')
        URL.replace('http://', '')
        if not URL.startswith('www.'):
            URL = 'www.' + URL

        # connect to the url
        conn = httplib.HTTPSConnection(URL)
        print "try connection"
        conn.request("GET", "/")
        print "get request"
        response = conn.getresponse()
        print "get response", response.status
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

                def __init__(self, verbose=0):
                    self.links = {}
                    f = formatter.NullFormatter()
                    HTMLParser.__init__(self,)

                def link_start(self, href, name, type):
                    self.save_bgn()
                    self.link = href

                def link_end(self):
                    text = string.strip(self.save_end())
                    if self.link and text:
                        self.links[text] = self.links.get(text, []) + [self.link]

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

            links = parser.links
            print links
            print 'got the links'

            print "after parsing"
            # get the total count of words in the page
            for count in page_contents.itervalues():
                total_word_count += count

            report['total_word_count'] = total_word_count
            print 'after getting the row count'
            # get the count of unique words in the page
            unique_word_count = len(page_contents)
            report['unique_word_count'] = unique_word_count
            print 'after getting the unique words'
            # Get the top 5 most common words
            page_contents_sorted = sorted(page_contents.items(), key = lambda x: x[1], reverse=True)
            print 'after sorting the contents'
            top_word_index = 0
            while top_word_index < 5:
                most_common_words.append(page_contents_sorted[top_word_index][0])
                top_word_index += 1
            report['most_common_words'] = most_common_words

            # process the html with beautifulsoup4
            print "before beautiful soup"
            soup = BeautifulSoup(page_html, 'html.parser')
            print "after beautiful soup"
            # get the title of the page
            title = soup.find('title').contents
            if len(title) > 0:
                title = title[0]
            else:
                title = 'unknown'
            report['title'] = title
            print 'got the title'

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
            report['keywords'] = list(keywords_not_in_content)

            page_headers = dict(response.getheaders())

            page_size_octets = page_headers.get("content-length", "unknown")
            if page_size_octets != "unknown":
                # convert the page size to KB
                page_size_octets = int(page_size_octets) * 8 / 1024 / 8
            report['page_size'] = str(page_size_octets) + 'KB'
            return HttpResponse(simplejson.dumps(report), content_type="application/json")
        # return error
        else:
            return HttpResponse(simplejson.dumps({'error': 'The url does not exist'}), content_type="application/json")
    # return error
    except KeyError:
        return HttpResponse(simplejson.dumps({'error': 'Bad input supplied'}), content_type="application/json")
