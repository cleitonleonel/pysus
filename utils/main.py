import re
from api.health_brazil import SusApi, json


def main(document):
    string = re.sub("\.|\-|\?", "", document)
    result = sus.consult_data(string)
    if isinstance(result, list):
        json_data = json.dumps(result[0], indent=4)
    else:
        json_data = json.dumps(sus.parse_data(), indent=4)
    print(json_data)


if __name__ == '__main__':
    sus = SusApi()
    # sus.get_token()  # Usar apenas se a falha do site for corrigida, esse método requer interação manual.
    sus.current_token = ""  # "$2a$10$IqImGD3B.2G/VMEOpdRoiuiOZqnlw/.NhCz6LsHAadPA6OOLHzDnS"
    cpf = input("Entre com um cpf para efetuar a consulta: ")  # Requer um cpf válido com cadastro no SUS.
    main(cpf)
