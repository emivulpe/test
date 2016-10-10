from django.shortcuts import render
from bs4 import BeautifulSoup
import re
from HTMLParser import HTMLParser
import httplib


def index(request):
    return render(request, 'mercurytide_app/index.html', {})

def create_report(request):
    try:

        URL = request.POST['url']
        conn = httplib.HTTPSConnection(URL)
        conn.request("GET", "/")
        response = conn.getresponse()
        if response.status == 200:
            # initiate a context dict to pass to the report page
            context_dict = {}
            # initiate the report variables
            page_contents = {}
            total_word_count = 0
            most_common_words = []

            # Custom HTML parser
            class pageHTMLParser(HTMLParser):

                def handle_data(self, data):
                    data_without_punctuation = re.sub(ur'[^\w\d\s]+', '', data)
                    word_list = data_without_punctuation.split()
                    for word in word_list:
                        if word in page_contents:
                            page_contents[word] = page_contents[word] + 1
                        else:
                            page_contents[word] = 1
            # parse the html
            page_html = response.read()
            parser = MyHTMLParser()
            parser.feed(page_html)

            # get the total count of words in the page
            for count in page_contents.itervalues():
                total_word_count += count

            context_dict['total_word_count'] = total_word_count

            # get the count of unique words in the page
            unique_word_count = len(page_contents)
            context_dict['unique_word_count'] = unique_word_count

            # Get the top 5 most common words
            page_contents_sorted = sorted(page_contents.items(), key = lambda x: x[1], reverse=True)

            top_word_index = 0
            while top_word_index < 5:
                most_common_words.append(page_contents_sorted[top_word_index][0])
                top_word_index += 1
            context_dict['most_common_words'] = most_common_words

            # process the html with beautifulsoup
            soup = BeautifulSoup(page_html, 'html.parser')

            # get the title of the page
            title = soup.find('title').contents[0]
            context_dict['title'] = title

            # get the list of the links
            page_links = []
            links = soup.find_all('a')
            for link in links:
                link_text = link.contents[0]
                the_link = link.get('href')
                new_link = (link_text, the_link)
                page_links.append(new_link)
            context_dict['page_links'] = page_link

            # get a list of meta tags and the keywords that are not used in the content
            metatags = soup.find_all('meta')
            metatags_list = []
            for tag in metatags:
                metatags_list.append((tag.get('name'), tag.get('content', 'No content')))
                if tag.get('name') == 'keywords':
                    keywords = tag.get('content')
                    keywords = keywords.split(',')

            keywords_not_in_content = set(keywords) - set(page_contents.keys())
            context_dict['keywords'] = keywords_not_in_content
            return HttpResponse(simplejson.dumps({'error': 'The url does not exist'}), content_type="application/json")

            #return render(request, 'mercurytide_app/report.html', context_dict)

        else:
            return HttpResponse(simplejson.dumps({'error': 'The url does not exist'}), content_type="application/json")

    except KeyError:
        return HttpResponse(simplejson.dumps({'error': 'Bad input supplied'}), content_type="application/json")