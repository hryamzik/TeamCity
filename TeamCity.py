import getpass
import json as JSON
import keyring
import requests
import sys

class TeamCity:
    def __init__(self, url="http://127.0.0.1:8111", username=None):
        self.url = url
        self.username = username
        self.session = requests.Session()
        self.json_headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    def show(self):
        print self.url
    
    def checkAuth(self, request):
        pass
    
    def _getPassword(self):
        if not self.username:
            self.username = raw_input("Username:")
        
        password = keyring.get_password(self.url, self.username)
        if not password:
            password = self._getNewPassword(False)
        return password
    
    def _getNewPassword(self, reenterUserName=True):
        if reenterUserName:
            username = raw_input("Username (%s):" % (self.username))
            if username.strip() != '':
                self.username = username
    
        password = getpass.getpass()
        try:
            keyring.set_password(self.url, self.username, password)
        except keyring.errors.PasswordSetError:
            print >> sys.stderr, "Failed to store password"
        return password
    
    def _request(self, uri, method="GET", headers=None, json=None, data=None):
        if headers == None:
            headers = self.json_headers
        r = None
        if method == "GET":
            r = self.session.get("%s/%s" % (self.url, uri), headers=headers)
        elif method == "POST":
            r = self.session.post(
                       "%s/%s" % (self.url, uri),
                       headers=headers,
                       json=json,
                       )
        elif method == "PUT":
            if not data and json:
                data = JSON.dumps(json)
            r = self.session.put(
                       "%s/%s" % (self.url, uri),
                       headers=headers,
                       data=data,
                       )
        elif method == "DELETE":
            if not data and json:
                data = JSON.dumps(json)
            r = self.session.delete(
                       "%s/%s" % (self.url, uri),
                       headers=headers,
                       data=data,
                       )
        if r.status_code == 401:
            r = self._authorizedRequest(uri, method=method, headers=headers, json=json, data=data)
        return r
    
    def _authorizedRequest(self, uri, method="GET", headers=None, json=None, data=None, retry=False):
        print >> sys.stderr, "Authenticating"
        if headers == None:
            headers = self.json_headers
        password = None
        if not retry:
            password = self._getPassword()
        else:
            password = self._getNewPassword()
        
        if method == "GET":
            r = self.session.get(
                       "%s/httpAuth/%s" % (self.url, uri),
                       headers=headers,
                       auth=requests.auth.HTTPBasicAuth(self.username, password)
                       )
        elif method == "POST":
            r = self.session.post(
                       "%s/httpAuth/%s" % (self.url, uri),
                       headers=headers,
                       json=json,
                       auth=requests.auth.HTTPBasicAuth(self.username, password)
                       )
        elif method == "PUT":
            r = self.session.put(
                       "%s/httpAuth/%s" % (self.url, uri),
                        headers=headers,
                        data=data,
                        auth=requests.auth.HTTPBasicAuth(self.username, password)
                        )
        elif method == "DELETE":
            r = self.session.delete(
                       "%s/httpAuth/%s" % (self.url, uri),
                        headers=headers,
                        data=data,
                        auth=requests.auth.HTTPBasicAuth(self.username, password)
                        )
        
        if r.status_code == 401:
            r = self._authorizedRequest(uri, method=method, headers=headers, json=json, data=data, retry=True)
        return r
    
    def getAgents(self, connected=None, authorized=None, enabled=None):
        r = None
        locators = []
        
        if connected:
            locators.append("connected:true")
        if authorized:
            locators.append("authorized:true")
        if enabled:
            locators.append("enabled:true")
        
        if len(locators) == 0:
            r = self._request("app/rest/agents")
        else:
            r = self._request("app/rest/agents?locator=%s" % (",").join(locators))
        return r.json()
    
    def getBuilds(self,locator=None):
        r = None
        if not locator:
            r = self._request("app/rest/builds")
        else:
            r = self._request("app/rest/builds?locator=%s:true" % locator)
        return r.json()
    
    def getBuildQueue(self):
        r = self._request("app/rest/buildQueue")
        return r.json()
    
    def triggerBuild(self, build):
        r = self._request("app/rest/buildQueue",
                          method="POST",
                          json={ "buildTypeId": build }
                          )
        return r.json()
    
    def configIsPaused(self, build):
        r = self._request("app/rest/buildTypes/%s/paused" % build, headers={})
        return r.json()
    
    def pauseConfig(self, build):
        r = self._request("app/rest/buildTypes/%s/paused" % build,
                          method="PUT",
                          headers={},
                          data="true"
                          )
        return r
    
    def resumeConfig(self, build):
        r = self._request("app/rest/buildTypes/%s/paused" % build,
                          method="PUT",
                          headers={},
                          data="false"
                          )
        return r
    
    def getBuildConfigParams(self, build):
        r = self._request("app/rest/buildTypes/%s/parameters" % build)
        return r.json()
    
    def getBuildConfigParam(self, build, param):
        r = self._request("app/rest/buildTypes/%s/parameters/%s" % (build, param))
        return r.json()
    
    def setBuildConfigParam(self, build, param, value):
        r = self._request("app/rest/buildTypes/%s/parameters/%s" % (build, param),
                          method="PUT",
                          json={"value": value}
                         )
        try:
            return r.json()
        except:
            return r
    
    def deleteBuildConfigParam(self, build, param):
        r = self._request("app/rest/buildTypes/%s/parameters/%s" % (build, param), method="DELETE")
        try:
            return r.json()
        except:
            return r
    pass