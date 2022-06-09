import requests


class VTLookup(object):
    def __init__(self, api_key):
        self.base_url = "https://www.virustotal.com/api/v3"
        self.__api_key = api_key

        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "x-apikey": self.__api_key
        })

    def lookup_file_reputation(self, file_hash):
        url = f"{self.base_url}/files/{file_hash}"
        print(f"Requesting URL: {url}")
        try:
            r = self._session.get(url)
            if r.status_code == 200:
                response = r.json()
                result = {
                    "analysis_stats": response['data']['attributes']['last_analysis_stats'],
                    "last_submission_date": response['data']['attributes']['last_submission_date'],
                    "last_analysis_date": response['data']['attributes']['last_analysis_date']
                }
                return result
        except Exception as e:
            print(e)
