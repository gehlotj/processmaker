''' 
Currently we use processmaker to submit events. The following python program pushes the case
to the next step in workflow right before 7 days of the event start date. This notify the users that the event is close by
and no more changes can be made.

Requirement: The following script will require a third party plugin called extrarest to be installed in processmaker. The plugin can be
download from the following link:
    https://github.com/amosbatto/pmcommunity/tree/master/extraRest
'''

import requests,sys,datetime,json,logging

logging.basicConfig(
    filename="routine.log",
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class AccessToken:
    CLIENT_ID = "ADDID"
    CLIENT_SECRET = "ADDSECRET"

    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.url = 'http://yoururl/workflow/oauth2/token'

    def get_token(self):
            data = json.dumps({"grant_type":"password","scope":"*","client_id":AccessToken.CLIENT_ID,"client_secret":AccessToken.CLIENT_SECRET,"username":self.username,"password":self.password})
            r = requests.post(self.url, data=data, headers={'Content-Type': 'application/json','Accept': 'application/json'})
            return r.json()['access_token']

class Req:
    def __init__(self,token,url,payload=None):
        self.token = token
        self.url = url
        self.payload = payload
        self.header = {'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(self.token)}

    def get(self):
        r = requests.get(self.url, data=self.payload, headers=self.header)
        return r

    def route(self):
        r = requests.put(self.url, headers=self.header)
        return r

    def push(self):
        r = requests.put(self.url, data=json.dumps(self.payload), headers=self.header)
        return r



class Routine:

    def __init__(self):
        self.base_url = 'http://yoururl/api/1.0/workflow/'
        self.project_uid = '9198303225000000000000000000'
        self.days_before_trigger = 7#35 #This value decide how many days before the case should route
        self.token = None
        self.task_uid = '1523132325c8rftyyd51044xaosk'


    def getToken(self):
        self.token = AccessToken('myusername','mypassword').get_token()
        if self.token is None:
            print('Cannot retrieve token. Invalid Credentials')
            sys.exit(0)
        return self.token


    def routeData(self):
        self.token = self.getToken()
        uid = Req(self.token,self.base_url+'project/'+self.project_uid+'/report-tables').get()
        uid_value = json.loads(uid.text)[0]['rep_uid']
        get_data = Req(self.token,self.base_url+'project/'+self.project_uid+'/report-table/'+uid_value+'/data').get()
        get_data_dict = json.loads(get_data.text)
        result = self.extractData(get_data_dict)
        for val in result:
            if val[1] is not None:
                push_data = Req(self.token,self.base_url+'/extrarest/case/'+val[0]+'/route-case',{'del_index':str(val[1])}).push()
                logging.debug("Routing Confirmed for {0}".format(val[2]))
            else:
                logging.debug("Del index doesnt exists for {0}".format(val[2]))


    def extractData(self,result):
        ans = []
        for data in result['rows']:
            try:
                datetime_object = datetime.datetime.strptime(data['startdate'], '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    datetime_object = datetime.datetime.strptime(data['startdate'], '%m-%d-%Y %I:%M %p')
                except:
                    logging.critical("Error with {0} on date {1}".format(data['app_number'],data['startdate']))
            date_lookup = (datetime_object-datetime.datetime.now()).days
            if (date_lookup <= self.days_before_trigger) and (data['app_status'] == 'TO_DO'):
                    del_index = self.getDelindex(data['app_uid'],self.task_uid)
                    ans.append((data['app_uid'],del_index,data['app_number']))
        return ans


    def getDelindex(self,app_uid,task_uid=None):
        '''
        The following function will get del index of the case passed using app_uid
        '''
        try:
            get_data = Req(self.token,self.base_url+'cases/'+app_uid+'/tasks').get()
            data = json.loads(get_data.text)
            for val in data:
                if val['tas_uid'] == task_uid:
                    return val['delegations'][0]['del_index']
        except:
            return None

x = Routine().routeData()

