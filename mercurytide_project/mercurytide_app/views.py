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
import string

def index(request):
    """
    A view to render the home page
    :param request: the request
    :return: renders the index page
    """
    return render(request, 'mercurytide_app/index.html', {})


def create_report(request):
    """
    A method to handle the post request and get all data needed to produce a report for the url of interest
    :param request: the request
    :return: HttpResponse containing the data for the report or an error message
    """
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
        conn.request("GET", "/")
        response = conn.getresponse()

        # ensure the url is reachable
        if response.status == 200:
            # initiate a context dict to pass to the report page
            report = {}
            # initiate the report variables
            page_contents = {}
            total_word_count = 0
            most_common_words = ''

            # Custom HTML parser
            class PageHTMLParser(HTMLParser):

                def handle_data(self, data):
                    data_without_punctuation = re.sub(ur'[^\w\d\s]+', '', data)
                    word_list = data_without_punctuation.split()
                    for word in word_list:
                        word = word.lower()
                        if word in page_contents:
                            page_contents[word] = page_contents[word] + 1
                        else:
                            page_contents[word] = 1


            # parse the html
            page_html = response.read()
            parser = PageHTMLParser()
            parser.feed(page_html)
            parser.close()

            print "after parsing"
            # get the total count of words in the page
            for count in page_contents.itervalues():
                total_word_count += count

            report['Total word count'] = total_word_count
            print 'after getting the row count'
            # get the count of unique words in the page
            unique_word_count = len(page_contents)
            report['Unique word count'] = unique_word_count
            print 'after getting the unique words'
            # Get the top 5 most common words
            page_contents_sorted = sorted(page_contents.items(), key = lambda x: x[1], reverse=True)
            print 'after sorting the contents'
            top_word_index = 0
            while top_word_index < 4:
                most_common_words += page_contents_sorted[top_word_index][0] + ', '
                top_word_index += 1
            most_common_words += page_contents_sorted[4][0]
            report['Most common 5 words'] = most_common_words

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
            report['Title'] = title
            print 'got the title'

            # get a list of meta tags and the keywords that are not used in the content
            metatags = soup.find_all('meta')
            metatags_str = ''
            keywords = []
            for tag in metatags:
                print tag.get('name')
                if tag.get('name') is not None:
                    metatags_str += tag.get('name') + ', '
                if tag.get('name') == 'keywords':
                    keywords = tag.get('content')
                    keywords = map(str,keywords.split())
            metatags_str = metatags_str[:-2]

            # add the metatags
            report['Metatags'] = metatags_str

            print keywords
            # add the list of keywords that don't appear in the content
            keywords_not_in_content = list(set(map(str.lower,keywords)) - set(map(str.lower,page_contents.keys())))
            keywords_str = ''
            i = 0
            while i < len(keywords_not_in_content) - 1:
                keywords_str += keywords_not_in_content[i] + ', '
                i += 1
            keywords_str += keywords_not_in_content[len(keywords_not_in_content) - 1]
            report['Keywords not appearing in the context'] = keywords_str

            # get the page size
            page_headers = dict(response.getheaders())
            page_size_octets = page_headers.get("content-length", "unknown")
            if page_size_octets != "unknown":
                # convert the page size to KB
                page_size_octets = int(page_size_octets) * 8 / 1024 / 8
            report['Page size'] = str(page_size_octets) + 'KB'

            # # get the links
            # class LinkParser(htmllib.HTMLParser):
            #     # return a dictionary mapping anchor texts to lists
            #     # of associated hyperlinks
            #
            #     def __init__(self, verbose=0):
            #         self.anchors = {}
            #         f = formatter.NullFormatter()
            #         htmllib.HTMLParser.__init__(self, f, verbose)
            #
            #     def anchor_bgn(self, href, name, type):
            #         self.save_bgn()
            #         self.anchor = href
            #
            #     def anchor_end(self):
            #         text = string.strip(self.save_end())
            #         if self.anchor and text:
            #             self.anchors[text] = self.anchors.get(text, []) + [self.anchor]

            # page_links = ''
            # links = soup.find_all('a')
            # for link in links:
            #     link_text = link.contents[0]
            #     the_link = link.get('href')
            #     print link_text, ' : ', the_link
            #     if type(link_text) == str:
            #         new_link = link_text + ' : ' + the_link + '\n'
            #         page_links += new_link
            # print page_links
            #
            # links = soup.find_all('a')
            # for tag in soup.findAll('a', href=True):
            #     tag['href'] = urlparse.urljoin(url, tag['href'])
            #     print tag['href']
            # for tag in links:
            #     link = tag.get('href', None)
            #     if link is not None:
            #         print link


            # link_parser = LinkParser()
            # link_parser.feed(page_html)
            # link_parser.close()
            # print 'here'
            # for link_text, link in link_parser.anchors.items():
            #     print link_text, link[0]
            #     page_links += link_text + ':' + link[0] + '\n'
            #
            # report['Links'] = page_links.encode()


            links_list = []
            links = soup.find_all('a')
            print links, 'links'
            ulr_pattern = re.compile("^http[s]?://")
            for tag in links:
                print tag, 'tag'
                link = tag.get('href', None)

                if link is not None:
                    link_text = tag.contents[0]
                    print link, 'link'
                    print link is not None, 'link is not none'
                    link_str = link
                    print ulr_pattern.match(link_str), 'pattern matching'
                    if ulr_pattern.match(link_str) is not None:
                        print type(link_text) is str, 'it is text',link_text, type(link_text)
                        print link_text, '->',  link
                        try:
                            links_list.append(link_text + '->' + link)
                        except:
                            pass
                        print 'update'
            report['Links'] = links_list
            print links, links_list, 'links list'
            return HttpResponse(simplejson.dumps(report), content_type="application/json")
        # return error
        else:
            return HttpResponse(simplejson.dumps({'error': 'The url does not exist'}), content_type="application/json")
    # return error
    except KeyError:
        return HttpResponse(simplejson.dumps({'error': 'Bad input supplied'}), content_type="application/json")
