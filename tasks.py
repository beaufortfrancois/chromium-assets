import json
from xml.dom.minidom import parseString

from google.appengine.api import urlfetch

from models import Assets

import webapp2


# $ git ls-files | grep resources.grd
RESOURCES_FILE_URLS = [
  'ash/resources/ash_resources.grd',
  'chrome/app/generated_resources.grd',
  'chrome/app/theme/chrome_unscaled_resources.grd',
  'chrome/app/theme/theme_resources.grd',
  'chrome/browser/browser_resources.grd',
  'chrome/browser/devtools/frontend/devtools_discovery_page_resources.grd',
  'chrome/browser/resources/component_extension_resources.grd',
  'chrome/browser/resources/memory_internals_resources.grd',
  'chrome/browser/resources/net_internals_resources.grd',
  'chrome/browser/resources/options_resources.grd',
  'chrome/browser/resources/quota_internals_resources.grd',
  'chrome/browser/resources/signin_internals_resources.grd',
  'chrome/browser/resources/sync_file_system_internals_resources.grd',
  'chrome/browser/resources/sync_internals_resources.grd',
  'chrome/browser/resources/translate_internals_resources.grd',
  'chrome/common/common_resources.grd',
  'chrome/common/extensions_api_resources.grd',
  'chrome/renderer/resources/renderer_resources.grd',
  'chrome_frame/resources/chrome_frame_resources.grd',
  'cloud_print/service/win/service_resources.grd',
  'cloud_print/virtual_driver/win/install/virtual_driver_setup_resources.grd',
  'components/dom_distiller_resources.grd',
  'content/content_resources.grd',
  'content/shell/shell_resources.grd',
  'net/base/net_resources.grd',
  'ui/keyboard/keyboard_resources.grd',
  'ui/resources/ui_resources.grd',
  'ui/resources/ui_unscaled_resources.grd',
  'ui/webui/resources/webui_resources.grd',
  'webkit/glue/resources/webkit_resources.grd',
]
RESOURCE_BASE_URL = 'https://src.chromium.org/svn/trunk/src/'


def is_valid_asset(url):

    # Retrieve only image and audio files which are not specific to Google Chrome
    return (url.find('google_chrome') == -1) and \
        (url.endswith('.png') or url.endswith('.jpg') \
        or url.endswith('.ico') or url.endswith('.bmp') \
        or url.endswith('.gif') or url.endswith('.wav'))


class GetChromiumAssetsTaskPage(webapp2.RequestHandler):

    def get(self):

        resources_file_urls = []
        for resources_file_url in RESOURCES_FILE_URLS:
          resources_file_urls.append(RESOURCE_BASE_URL + resources_file_url)

        assets = []
        for resources_file_url in resources_file_urls:
            print resources_file_url
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
