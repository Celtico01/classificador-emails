#libs
from os import (
    environ,
    getcwd,
    chdir,
    path,
)

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
        print(gpt4o('If you are there and everything is working please replay just thse: Everything Working!')[0])
        settings.configure(lm=gpt4o)
        del gpt4o

def load_all_new_messages(email, senha, host='imap.gmail.com', unread=True):
    #try: implementar depois caso seja preciso!
    with Imbox(hostname=host, username=email, password=senha) as imbox:
        return imbox.messages(unread=unread)
    
class sig_classificador(Signature):
    """A partir do {assunto} e do {texto} 
    crie {assunto_principal} 
    e crie o {assunto_resumido} 
    caso o assunto seja muito grande"""
    
    assunto = InputField(desc='Assunto do Email')
    texto = InputField(desc='Conteudo do Email')
    assunto_principal = OutputField(desc='o assunto obtido do texto')
    assunto_resumido = OutputField(desc='assunto resumido obtido do assunto caso o assunto seja muito grande')

def rationaly_type():
    return OutputField( prefix="Raciocinio: Vamos pensar passo a passo em ordem de",
                        desc="${produzir assunto_principal e assunto_resumido}. Nos ...",)

class modulo_classificador(Module):
    def __init__(self):
        super().__init__()

        self.generate_answer = ChainOfThought(sig_classificador, rationale_type=rationaly_type())
    
    def forward(self, assunto, texto):
        return self.generate_answer(assunto=assunto, texto=texto)
    
def formatar_output():
    raise NotImplementedError

def main():
    load_lm_to_dspy()
    cot = modulo_classificador() # otimizar depois! usando optimizers
    #try: implementar depois caso seja preciso!
    with Imbox(hostname='imap.gmail.com', username=environ['EMAIL'], password=environ['SENHA_EMAIL']) as imbox:
        messages = imbox.messages(unread=False)
    
    # criar estrutura de dados
        for uid, message in messages:
            email_id = uid
            cliente = message.sent_from
            assunto = message.subject
            texto = message.body['plain']
            result = cot(assunto=assunto, texto=texto[0])
            assunto_principal = result.assunto_principal
            assunto_resumido = result.assunto_resumido

            #salvar na estrutura de dados
            print(f"email_id = {email_id}")
            print(f"cliente_gmail = {cliente}")
            print(f"assunto = {assunto}")
            print(f"texto = {texto}")
            print(f"assunto_principal = {assunto_principal}")
            print(f"assunto_resumido = {assunto_resumido}")

if __name__ == '__main__':
    main()