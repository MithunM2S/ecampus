import urllib.request
import urllib.parse
import json
from django.conf import settings


class TextLocalServices(object):

    def call_vendor_api(self, api_data, resource_url):
        try:
            api_data['apikey'] = settings.SMS_API_KEY
            data =  urllib.parse.urlencode(api_data)
            data = data.encode('utf-8')
            request = urllib.request.Request(settings.SMS_API_ENDPOINT + resource_url)
            response = urllib.request.urlopen(request, data).read()
            return json.loads(response.decode('utf-8'))
        except:
            return False

    def send_sms(self, recipients, template):

        send_api_data = {
                            'numbers': ",".join(map(str, recipients)),
                            'message' : template,
                            'sender': settings.SMS_SENDER_ID
                        }
        return self.call_vendor_api(send_api_data, '/send/?')

    def get_templates(self, ):
        get_template_api_data = {
                                'id': 797596
                            }
        return self.call_vendor_api(get_template_api_data, '/get_templates/?')
