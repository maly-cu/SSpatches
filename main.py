from os.path import join, dirname, realpath

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from plyer import notification
from plyer.utils import platform

from plyer import gps
from kivy.properties import StringProperty
from kivy.clock import mainthread

kivy.require('1.8.0')


class CombinedDemo(BoxLayout):

    # ----------------- Notification -------------------------

    def do_notify(self, mode='normal'):
        title = self.ids.notification_title.text
        message = self.ids.notification_text.text
        ticker = self.ids.ticker_text.text
        kwargs = {'title': title, 'message': message, 'ticker': ticker}

        if mode == 'fancy':
            kwargs['app_name'] = "Plyer Notification Example"
            if platform == "win":
                kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                          'plyer-icon.ico')
                kwargs['timeout'] = 4
            else:
                kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                          'plyer-icon.png')
        elif mode == 'toast':
            kwargs['toast'] = True
        notification.notify(**kwargs)

    # ----------------- GPS -------------------------



class CombinedDemoApp(App):
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.

        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return CombinedDemo()
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

    # def on_pause(self):
    #     return True


if __name__ == '__main__':
    CombinedDemoApp().run()