import datetime

from django.contrib import auth

from . import app_settings
from .utils import from_dotted_path

class ForceLogoutMiddleware(object):
    SESSION_KEY = 'force-logout:last-login'

    def __init__(self):
        self.fn = from_dotted_path(app_settings.CALLBACK)

        def callback(sender, user=None, request=None, **kwargs):
            if request:
                request.session[self.SESSION_KEY] = datetime.datetime.utcnow()
        auth.signals.user_logged_in.connect(callback, weak=False)

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        user_timestamp = self.fn(request.user)

        if not user_timestamp:
            return

        try:
            timestamp = request.session[self.SESSION_KEY]
        except KeyError:
            # May not have logged in since we started populating this key.
            return

        if timestamp > user_timestamp:
            return

        auth.logout(request)