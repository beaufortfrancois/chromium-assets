import json
from xml.dom.minidom import parseString

from google.appengine.api import urlfetch

from models import Assets

import webapp2


RESOURCES_URL = 'https://code.google.com/p/cs/codesearch/codesearch/json?search_request=b&query=file%3A(_resources.grd%24)+package%3Achromium&max_num_results=200&search_request=e'
RESOURCE_BASE_URL = 'https://src.chromium.org/svn/trunk/'


def is_valid_asset(url):

    # Retrieve only image and audio files which are not specific to Google Chrome
    return (url.find('google_chrome') == -1) and \
        (url.endswith('.png') or url.endswith('.jpg') \
        or url.endswith('.ico') or url.endswith('.bmp') \
        or url.endswith('.gif') or url.endswith('.wav'))


class GetChromiumAssetsTaskPage(webapp2.RequestHandler):

    def get(self):

        result = urlfetch.fetch(RESOURCES_URL)
        if result.status_code == 200:
            data = json.loads(result.content)
            resources_file_urls = []
            for result in data['search_response'][0]['search_result']:
                filename = result['top_file']['file']['name']
                if not filename.startswith('src/out/'):
                    resources_file_urls.append(RESOURCE_BASE_URL+filename)

            assets = []
            for resources_file_url in resources_file_urls:
                folder_path = resources_file_url[0:resources_file_url.rfind('/')]
                resources_result = urlfetch.fetch(resources_file_url)
                if resources_result.status_code == 200:
                    dom = parseString(resources_result.content)

                    for item in dom.getElementsByTagName('structure'):
                        url = folder_path+'/default_200_percent/'+item.getAttribute('file')
                        title = item.getAttribute('name')
                        if is_valid_asset(url):
                            assets.append((url, title))

                    for item in dom.getElementsByTagName('include'):
                        url = folder_path+'/'+item.getAttribute('file')
                        title = item.getAttribute('name')
                        if is_valid_asset(url):
                            assets.append((url, title))

            Assets.update_assets(assets)


app = webapp2.WSGIApplication([
    ('/tasks/get-chromium-assets', GetChromiumAssetsTaskPage),
], debug=True)
