'''
   The following code snippet will download the case passed as an argument to function
   downloadSingleDoc
'''
class Req:
    def __init__(self,token,url,payload=None):
        self.token = token
        self.url = url
        self.payload = payload
        self.header = {'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(self.token)}

    def downloadSingleDoc(self,case_num):
        r = requests.get(self.url,headers=self.header)
        raw_data = b''
        if r.status_code == 200:
            temp = json.loads(r.content.decode())
            url = self.url+'sysworkflow/en/neoclassic/'+temp[0]['app_doc_link']
            d = requests.get(url,stream = True)
            filename = case_num+'.pdf'
            f = open(filename,'wb')
            for data in d.iter_content():
                raw_data = raw_data + data
                f.write(data)
            f.close()
        return send_file(filename,attachment_filename=filename,as_attachment=True)

#use case
#Req(session['token'],'http://yoururl/api/1.0/workflow/cases/'+appid+'/output-documents').downloadSingleDoc('0000')
