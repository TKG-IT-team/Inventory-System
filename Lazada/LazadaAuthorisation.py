from lazop_sdk import LazopClient, LazopRequest
import Lazada.config_tools_lazada as config_tools
import ctypes

class Authorisation:
    def __init__(self):
        #Required parameters to concatenate authorization URL  
        self.redirect_uri = "https://thekettlegourmet.com/"
        self.response_type = "code"
        app_key, app_secret = config_tools.read_credentials_config()
        self.app_key = app_key
        self.app_secret = app_secret
    
    def concatenate_authorization_url(self):
        host = "https://auth.lazada.com"
        path = "/oauth/authorize"
        force_auth = "true"
        uri = f"{host}{path}?response_type={self.response_type}&force_auth={force_auth}&redirect_uri={self.redirect_uri}&client_id={self.app_key}"
        return uri

    def get_access_token(self, code):
        # code = "0_110194_P5OR9Z4G8j6ap5IoGCihVWsB44280"
        url = "https://auth.lazada.com/rest"

        client = LazopClient(url, self.app_key ,self.app_secret)
        request = LazopRequest("/auth/token/create")
        request.add_api_param("code", code)
        response = client.execute(request)
        print(response.body)
        return response.body['access_token'], response.body['refresh_token']
    
    def refresh_access_token(self, refresh_token):
        url = "https://auth.lazada.com/rest"

        client = LazopClient(url, self.app_key ,self.app_secret)
        request = LazopRequest("/auth/token/refresh")
        request.add_api_param("refresh_token", refresh_token)
        response = client.execute(request)
        # print(response.body)
        if (not 'access_token' in response.body) or (not 'refresh_token' in response.body):
            critical_msg = f"Access Token is invalid. Please refer to the developer guide to get an valid access token."
            print(critical_msg)
            ctypes.windll.user32.MessageBoxW(0, f"Lazada API: {critical_msg}", "Error Message", 0)  
        return response.body['access_token'], response.body['refresh_token']

# #Generate URL
#print(Authorisation().concatenate_authorization_url())
# #Get access token
#Authorisation().get_access_token("0_110194_bUY4S4eS639eQEnpHTPeM7Om22436")
