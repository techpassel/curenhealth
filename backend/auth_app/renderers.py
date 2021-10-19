import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if(isinstance(data, dict)):
            token = data.get('token', None)
            if token is not None and isinstance(token, bytes):
                # Also as mentioned above, we will decode `token` if it is of type bytes.
                data['token'] = token.decode('utf-8')
            return json.dumps({
                'user': data
            })
        else:
            return json.dumps({
                'error': data
            })
