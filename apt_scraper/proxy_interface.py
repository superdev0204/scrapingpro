from helper_class import *

class PROXYCLASSNEW():

    def __init__(self, api_key):

        self._MAX_TRIAL_REQUESTS = 10
        self._WAIT_TIME_BETWEEN_REQUESTS = 5
        self.api_key = api_key


    def get_url_response(self, url):

        url = f"https://api.scraperapi.com?api_key={self.api_key}&url={url}"
        print('Processing URL: ', url)

        payload = {}
        headers = {}
        count = 0
        while 1:
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                return response.text
            except Exception as error:
                print('error in getting url response: ', error)
            count += 1
            if count > 3:
                return ''


    def get_page_html(self, search_url):


        trials = 0

        print("-"*50)

        print()

        while trials < 2:

            return self.get_url_response(search_url)

        return False

    def make_soup_url(self, page_url):

        html_response = self.get_page_html(page_url)

        # Helper().write_random_file(html_response, 'file.html')

        if not html_response:

            return html_response

        return BeautifulSoup(html_response, 'html.parser')



if __name__ == "__main__":

    interface = INTERFACING()