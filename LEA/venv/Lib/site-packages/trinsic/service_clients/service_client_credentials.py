from msrest.pipeline import SansIOHTTPPolicy


class ServiceClientCredentials(SansIOHTTPPolicy):
    def __init__(self, api_token):
        super(ServiceClientCredentials, self).__init__()
        self.api_token = api_token

    def on_request(self, request, **kwargs):
        super(ServiceClientCredentials, self).on_request(request, **kwargs)
        request.context.session.headers['Authorization'] = 'Bearer {}'.format(self.api_token)
