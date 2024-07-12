class list_data():
    def __init__(self):
        self.size = 0
        self.list = []
    
    def add(self, no):
        if no is None:
            raise ValueError('Valor Inválido!')
        else:
            self.list.append(no)

    def get_dados(self):
        return self.list

class no():
    def __init__(self, uid, client, subject, text, main_subject, resu_subject):
        self.uid = uid
        self.client = client
        self.subject = subject
        self.text = text
        self.main_subject = main_subject
        self.resu_subject = resu_subject
    def __str__(self, send_text : bool = False):
        return f"""
****
* Email_ID: {self.uid}
* Client: {self.client}
* Subject: {self.subject}
* Main Subject: {self.main_subject}
* Resumed Subject: {self.resu_subject}
* Text: {self.text}
****
""" if send_text else f"""
****
* Email_ID: {self.uid}
* Client: {self.client}
* Subject: {self.subject}
* Main Subject: {self.main_subject}
* Resumed Subject: {self.resu_subject}
****"""

