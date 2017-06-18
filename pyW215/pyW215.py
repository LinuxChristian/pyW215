try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # Assume Python 2.x
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
import xml.etree.ElementTree as ET
import hmac
import time
import logging

_LOGGER = logging.getLogger(__name__)

ON = 'ON'
OFF = 'OFF'

W215_A2_DEV_ID = {
    'SWITCH': 1,
    'THERMAL': 2,
    'POWERMETER': 3
}

DEFAULT_DEV_ID = {
    'SWITCH': 1,
    'POWERMETER': 2,
    'THERMAL': 3
}


class SmartPlug(object):
    """
    Class to access:
        * D-Link Smart Plug Switch W215
        * D-Link Smart Plug DSP-W110

    Usage example when used as library:
    p = SmartPlug("192.168.0.10", ('admin', '1234'))

    # change state of plug
    p.state = OFF
    p.state = ON

    # query and print current state of plug
    print(p.state)

    Note:
    The library is greatly inspired by the javascript library by @bikerp (https://github.com/bikerp).
    Class layout is inspired by @rkabadi (https://github.com/rkabadi) for the Edimax Smart plug.
    """

    def __init__(self, ip, password, user="admin",
                 use_legacy_protocol=False):
        """
        Create a new SmartPlug instance identified by the given URL and password.

        :rtype : object
        :param host: The IP/hostname of the SmartPlug. E.g. '192.168.0.10'
        :param password: Password to authenticate with the plug. Located on the plug.
        :param user: Username for the plug. Default is admin.
        :param use_legacy_protocol: Support legacy firmware versions. Default is False.
        """
        self.ip = ip
        self.url = "http://{}/HNAP1/".format(ip)
        self.user = user
        self.password = password
        self.use_legacy_protocol = use_legacy_protocol
        if self.use_legacy_protocol:
            _LOGGER.info("Enabled support for legacy firmware.")
        self._error_report = False
        self.dev_id = DEFAULT_DEV_ID
        if self.use_legacy_protocol:
            try:
                hw_ver = self.fetchMyCgi()['HW Ver']
                # change dev map for HW A2
                if hw_ver == 'A2':
                    self.dev_id = W215_A2_DEV_ID
                # this assume the model number is W215, might be wrong
                self.model_name = 'W215_' + hw_ver
            except:
                self.model_name = 'Unknown'
        else:
            self.model_name = self.SOAPAction("", "ModelName", "")

    def moduleParameters(self, module):
        """Returns moduleID XML.

        :type module: str
        :param module: module number/ID
        :return XML string with moduleID
        """
        return '''<ModuleID>{}</ModuleID>'''.format(module)

    def controlParameters(self, module, status):
        """Returns control parameters as XML.

        :type module: str
        :type status: str
        :param module: The module number/ID
        :param status: The state to set (i.e. true (on) or false (off))
        :return XML string to join with payload
        """
        if self.use_legacy_protocol:
            return '''{}<NickName>Socket 1</NickName><Description>Socket 1</Description>
                      <OPStatus>{}</OPStatus><Controller>1</Controller>'''.format(self.moduleParameters(module), status)
        else:
            return '''{}<NickName>Socket 1</NickName><Description>Socket 1</Description>
                      <OPStatus>{}</OPStatus>'''.format(self.moduleParameters(module), status)

    def radioParameters(self, radio):
        """Returns RadioID as XML.

        :type radio: str
        :param radio: Radio number/ID
        """
        return '''<RadioID>{}</RadioID>'''.format(radio)

    def requestBody(self, Action, params):
        """Returns the request payload for an action as XML>.

        :type Action: str
        :type params: str
        :param Action: Which action to perform
        :param params: Any parameters required for request
        :return XML payload for request
        """
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <{} xmlns="http://purenetworks.com/HNAP1/">
            {}
        </{}>
        </soap:Body>
        </soap:Envelope>
               '''.format(Action, params, Action)

    def SOAPAction(self, Action, responseElement, params=""):
        """Generate the SOAP action call.

        :type Action: str
        :type responseElement: str
        :type params: str
        :param Action: The action to perform on the device
        :param responseElement: The XML element that is returned upon success
        :param params: Any additional parameters required for performing request (i.e. RadioID, moduleID, ect)
        :return: Text enclosed in responseElement brackets
        """
        # Authenticate client
        auth = self.auth()

        if auth is None:
            return None
        payload = self.requestBody(Action, params)

        # Timestamp in microseconds
        time_stamp = str(round(time.time() / 1e6))

        action_url = '"http://purenetworks.com/HNAP1/{}"'.format(Action)
        AUTHKey = hmac.new(auth[0].encode(), (time_stamp + action_url).encode()).hexdigest().upper() + " " + time_stamp

        headers = {'Content-Type': '"text/xml; charset=utf-8"',
                   'SOAPAction': '"http://purenetworks.com/HNAP1/{}"'.format(Action),
                   'HNAP_AUTH': '{}'.format(AUTHKey),
                   'Cookie': 'uid={}'.format(auth[1])}

        try:
            response = urlopen(Request(self.url, payload.encode(), headers))
        except (HTTPError, URLError):
            _LOGGER.warning("Failed to open url to {}".format(self.ip))
            self._error_report = True
            return None

        xmlData = response.read().decode()
        root = ET.fromstring(xmlData)

        # Get value from device
        try:
            value = root.find('.//{http://purenetworks.com/HNAP1/}%s' % responseElement).text
        except AttributeError:
            _LOGGER.warning("Unable to find %s in response." % responseElement)
            return None

        if value is None and self._error_report is False:
            _LOGGER.warning("Could not find %s in response." % responseElement)
            self._error_report = True
            return None

        self._error_report = False
        return value

    def fetchMyCgi(self):
        """Fetches statistics from my_cgi.cgi"""
        try:
            response = urlopen(Request('http://{}/my_cgi.cgi'.format(self.ip), b'request=create_chklst'))
        except (HTTPError, URLError):
            _LOGGER.warning("Failed to open url to {}".format(self.ip))
            self._error_report = True
            return None

        lines = response.readlines()
        return {line.decode().split(':')[0].strip(): line.decode().split(':')[1].strip() for line in lines}

    @property
    def current_consumption(self):
        """Get the current power consumption in Watt."""
        try:
            res = self.SOAPAction('GetCurrentPowerConsumption', 'CurrentConsumption',
                                  self.moduleParameters(self.dev_id['POWERMETER']))
        except:
            return 'N/A'
        try:
            res = float(res)
        except ValueError:
            _LOGGER.error("Failed to retrieve current power consumption from SmartPlug")
        return res

    @property
    def total_consumption(self):
        """Get the total power consumpuntion in the device lifetime."""
        try:
            res = self.SOAPAction("GetPMWarningThreshold", "TotalConsumption",
                                  self.moduleParameters(self.dev_id['POWERMETER']))
        except:
            return 'N/A'
        try:
            float(res)
        except ValueError:
            _LOGGER.error("Failed to retrieve total power consumption from SmartPlug")
        return res

    @property
    def temperature(self):
        """Get the device temperature in celsius."""
        try:
            res = self.SOAPAction('GetCurrentTemperature', 'CurrentTemperature',
                                  self.moduleParameters(self.dev_id['THERMAL']))
        except:
            res = 'N/A'

        return res

    @property
    def state(self):
        """Get the device state (i.e. ON or OFF)."""
        response = self.SOAPAction('GetSocketSettings', 'OPStatus', self.moduleParameters(self.dev_id['SWITCH']))
        if response is None:
            return 'unknown'
        elif response.lower() == 'true':
            return ON
        elif response.lower() == 'false':
            return OFF
        else:
            _LOGGER.warning("Unknown state %s returned" % str(response.lower()))
            return 'unknown'

    @state.setter
    def state(self, value):
        """Set device state.

        :type value: str
        :param value: Future state (either ON or OFF)
        """
        if value.upper() == ON:
            return self.SOAPAction('SetSocketSettings', 'SetSocketSettingsResult',
                                   self.controlParameters(self.dev_id['SWITCH'], "true"))
        elif value.upper() == OFF:
            return self.SOAPAction('SetSocketSettings', 'SetSocketSettingsResult',
                                   self.controlParameters(self.dev_id['SWITCH'], "false"))
        else:
            raise TypeError("State %s is not valid." % str(value))

    def auth(self):
        """Authenticate using the SOAP interface.

        Authentication is a two-step process. First a initial payload
        is sent to the device requesting additional login information in the form
        of a publickey, a challenge string and a cookie.
        These values are then hashed by a MD5 algorithm producing a privatekey
        used for the header and a hashed password for the XML payload.

        If everything is accepted the XML returned will contain a LoginResult tag with the
        string 'success'.

        See https://github.com/bikerp/dsp-w215-hnap/wiki/Authentication-process for more information.
        """

        payload = self.initial_auth_payload()

        # Build initial header
        headers = {'Content-Type': '"text/xml; charset=utf-8"',
                   'SOAPAction': '"http://purenetworks.com/HNAP1/Login"'}

        # Request privatekey, cookie and challenge
        try:
            response = urlopen(Request(self.url, payload, headers))
        except URLError:
            if self._error_report is False:
                _LOGGER.warning('Unable to open a connection to dlink switch {}'.format(self.ip))
                self._error_report = True
            return None
        xmlData = response.read().decode()
        root = ET.fromstring(xmlData)

        # Find responses
        Challenge = root.find('.//{http://purenetworks.com/HNAP1/}Challenge').text
        Cookie = root.find('.//{http://purenetworks.com/HNAP1/}Cookie').text
        Publickey = root.find('.//{http://purenetworks.com/HNAP1/}PublicKey').text

        if (Challenge is None or Cookie is None or Publickey is None) and self._error_report is False:
            _LOGGER.warning("Failed to receive initial authentication from smartplug.")
            self._error_report = True
            return None

        # Generate hash responses
        PrivateKey = hmac.new((Publickey + self.password).encode(), Challenge.encode()).hexdigest().upper()
        login_pwd = hmac.new(PrivateKey.encode(), Challenge.encode()).hexdigest().upper()

        response_payload = self.auth_payload(login_pwd)
        # Build response to initial request
        headers = {'Content-Type': '"text/xml; charset=utf-8"',
                   'SOAPAction': '"http://purenetworks.com/HNAP1/Login"',
                   'HNAP_AUTH': '"{}"'.format(PrivateKey),
                   'Cookie': 'uid={}'.format(Cookie)}
        response = urlopen(Request(self.url, response_payload, headers))
        xmlData = response.read().decode()
        root = ET.fromstring(xmlData)

        # Find responses
        login_status = root.find('.//{http://purenetworks.com/HNAP1/}LoginResult').text.lower()

        if login_status != "success" and self._error_report is False:
            _LOGGER.error("Failed to authenticate with SmartPlug {}".format(self.ip))
            self._error_report = True
            return None

        self._error_report = False  # Reset error logging
        return PrivateKey, Cookie

    def initial_auth_payload(self):
        """Return the initial authentication payload."""

        return b'''<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
        <Login xmlns="http://purenetworks.com/HNAP1/">
        <Action>request</Action>
        <Username>admin</Username>
        <LoginPassword/>
        <Captcha/>
        </Login>
        </soap:Body>
        </soap:Envelope>
        '''

    def auth_payload(self, login_pwd):
        """Generate a new payload containing generated hash information.

        :type login_pwd: str
        :param login_pwd: hashed password generated by the auth function.
        """

        payload = '''<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
        <Login xmlns="http://purenetworks.com/HNAP1/">
        <Action>login</Action>
        <Username>{}</Username>
        <LoginPassword>{}</LoginPassword>
        <Captcha/>
        </Login>
        </soap:Body>
        </soap:Envelope>
        '''.format(self.user, login_pwd)

        return payload.encode()
