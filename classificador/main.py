#libs
from dotenv import load_dotenv
load_dotenv(r'C:\Users\alanm\OneDrive\Área de Trabalho\Workspace Python\Projects Python\classificarEmails\env\.env')

from openai import (
    AuthenticationError,
    NotFoundError
)
from os import (
    environ,
)
from dspy import(
    OpenAI,
    settings
)

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


def main():
    load_lm_to_dspy()


if __name__ == '__main__':
    main()