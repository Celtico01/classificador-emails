#version
version = '0.78'
#libs
from os import (
    environ,
    getcwd,
    chdir,
    path,
)

from data_structure import (
    list_data,
    no
)

from datetime import (
    datetime, 
    timedelta
)

from secure_smtplib import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from imbox import (
    Imbox
)

from openai import (
    AuthenticationError,
    NotFoundError
)

from dspy import(
    OpenAI,
    settings,
    Signature,
    InputField,
    OutputField,
    Module,
    ChainOfThought,
)

from dotenv import load_dotenv
chdir(path.pardir)
load_dotenv(path.join(getcwd(), 'env', '.env'))

def load_lm_to_dspy(model = 'gpt-4o'):
    try:
        gpt4o = OpenAI(model=model, api_key=environ['OPENAI_API_KEY'])
    except AuthenticationError:
        print('Forneça uma chave API válida!')
    except NotFoundError:
        print('Forneça um modelo válido!')

    if gpt4o('hi'):
        #print(gpt4o('If you are there and everything is working please replay just thse: Everything Working!')[0])
        settings.configure(lm=gpt4o, trace=[], temperature=0.0)
        del gpt4o
    
class sig_classificador_texto(Signature):
    """A partir do {texto} classifique o assunto principal do texto
    crie {assunto_principal}"""
    
    texto = InputField(desc='Conteudo do Email')
    assunto_principal = OutputField(desc='o assunto obtido do texto')

class sig_classificador_assunto(Signature):
    """A partir do {assunto} 
    caso o {assunto} seja muito grande crie o {assunto_resumido}"""

    assunto = InputField(desc='Assunto do Email')
    assunto_resumido = OutputField(desc='assunto resumido obtido do assunto caso o assunto seja muito grande')

class modulo_classificador(Module):
    def __init__(self):
        super().__init__()
        self.generate_resu_assunto = ChainOfThought(sig_classificador_assunto)
        self.generate_resu_texto = ChainOfThought(sig_classificador_texto)
    
    def forward(self, assunto, texto):
        return [self.generate_resu_assunto(assunto=assunto),
                self.generate_resu_texto(texto=texto)]
    
def send_to_gmail(data = None, day = None):
    if data is None or day is None:
        raise ValueError("No data to send | No Day")
    else:
        corpo = ''
        for d in data.get_dados():
            corpo += d.__str__() # you can send the text to, 
                                 # just pass the var send_text as True to the function!
                                 # the default is False!
        msg = MIMEMultipart()
        msg['From'] = environ['EMAIL']
        msg['To'] = environ['SEND_TO']
        msg['Subject'] = 'Emails received in: ' + day.strftime(r'%Y/%m/%d')
        msg.attach(MIMEText(corpo if corpo != '' else 'No Emails Received!', 'plain'))

        try:
            server = smtplib.SMTP(environ['smtp_server'], int(environ['smtp_port']))
            server.starttls()
            server.login(environ['EMAIL'], environ['APP_PASSWORD'])

            server.sendmail(msg['From'], msg['To'], msg.as_string())
            print('Email Enviado!') # criar log depois!
        except Exception as e:
            print(f'Erro ao enviar email: {e}')
        finally:
            server.quit()

def main():
    load_lm_to_dspy()
    cot = modulo_classificador() # otimizar depois! usando optimizers
    #save
    path_modules = path.join(getcwd(), 'modulos')
    if not path.exists(path.join(path_modules, 'cot-base-v-'+version+'.json')):
        cot.save(path.join(path_modules, 'cot-base-v-'+version+'.json'))
        #print('teste')
    try:
        #load the optimizer here!
        pass
    except FileNotFoundError:
        #optimize here!
        pass
    data = list_data()
    #try: implementar depois caso seja preciso!
    with Imbox(hostname='imap.gmail.com', username=environ['EMAIL'], password=environ['APP_PASSWORD']) as imbox:
        day = datetime.now() - timedelta(days=1)
        #print(day)

        messages = imbox.messages(date__on=day)
        # criar estrutura de dados
        for uid, message in messages:
            email_id = uid
            client = message.sent_from
            subject = message.subject
            text = message.body['plain']
            result_ass, result_text = cot(assunto=subject, texto=text[0])
            main_subject = result_text.assunto_principal
            resu_subject = result_ass.assunto_resumido

            #salvar na estrutura de dados
            #print(f"email_id = {email_id}")
            #print(f"cliente_gmail = {client}")
            #print(f"assunto = {subject}")
            #print(f"texto = {text}")
            #print(f"assunto_principal = {main_subject}")
            #print(f"assunto_resumido = {resu_subject}")

            data.add(no(uid=email_id, 
                        client=client, 
                        subject=subject, 
                        text=text[0], 
                        main_subject=main_subject, 
                        resu_subject=resu_subject))
            
        send_to_gmail(data, day)

if __name__ == '__main__':
    main()
    #print(path.join(getcwd(), 'modulos','cot_base' + '-v:' + version + '.json'))