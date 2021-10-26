import os
import json
import base64
import requests
import subprocess
from datetime import datetime
try:
    from PIL import Image
except ImportError:
    import Image

BASE_URL = 'https://scpa-backend.prod.saude.gov.br'
BASE_URL_CAPTCHA = 'https://captcha-api.prod.saude.gov.br'


def format_date(date):
    datetime_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    return datetime_object.strftime("%d/%m/%Y")


def open_image(base64string):
    open('imgCaptcha.png', 'wb').write(base64.b64decode(base64string.replace("data:image/png;base64,", "")))
    os.system('convert imgCaptcha.png -resize 300% file.png')
    return subprocess.Popen(["display", "file.png"])


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = self.get_headers()
        self.session = requests.Session()

    def get_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        return self.headers

    def send_request(self, method, url, **kwargs):
        requests.packages.urllib3.disable_warnings()
        self.response = self.session.request(method, url, **kwargs)
        return self.response


class SusApi(Browser):

    def __init__(self):
        super().__init__()
        self.base64_image = None
        self.current_token_id = None
        self.current_token = ""

    def get_token_id(self):
        self.headers["authorization"] = 'Basic U0NQQTo3RjFCM0Q1ODhBNzMyMUYxQ0Q4ODZCNzlBMjU4MD' \
                                        'IwOUE4REIwMzRBNjg0RkMyNDMyRTVCMEU5NTIzREQwNDNG'
        self.headers["origin"] = "https://scpa.saude.gov.br"
        self.headers["referer"] = "https://scpa.saude.gov.br/"

        text = self.send_request('GET',
                                 f"{BASE_URL_CAPTCHA}/v1/captcha/challenge",
                                 headers=self.headers,
                                 verify=False).text
        try:
            return json.loads(text)
        except ValueError:
            pass
        return text

    def get_token(self):
        token_result = self.get_token_id()
        self.current_token_id = dict(token_result)["tokenId"]
        self.base64_image = dict(token_result)["challengeImage"]
        image = open_image(self.base64_image)
        self.headers["authorization"] = 'Basic U0NQQTo3RjFCM0Q1ODhBNzMyMUYxQ0Q4ODZCNzlBMjU4MD' \
                                        'IwOUE4REIwMzRBNjg0RkMyNDMyRTVCMEU5NTIzREQwNDNG'
        self.headers["tokenid"] = self.current_token_id
        img_code = input('Por favor digite os dados da imagem: ')
        image.kill()

        data = {
            "challengeText": img_code
        }
        text = self.send_request('POST',
                                 f"{BASE_URL_CAPTCHA}/v1/captcha/validate-challenge",
                                 headers=self.headers,
                                 json=data,
                                 verify=False).text

        if not json.loads(text).get("success"):
            return self.get_token()
        try:
            self.current_token = json.loads(text)["tokenVerify"]
            return self.current_token
        except ValueError:
            pass
        return text

    def consult_data(self, document):
        self.headers = self.get_headers()
        self.headers["code"] = self.current_token
        text = self.send_request('GET',
                                 f"{BASE_URL}/public/scpa-usuario/validacao-cpf/{document}",
                                 headers=self.headers,
                                 verify=False).text
        try:
            self.response = json.loads(text)
            return self.response
        except ValueError:
            pass
        return text

    def parse_data(self):
        result_dict = {}
        result_dict["nome"] = self.response["pessoa"].get("nome")
        result_dict["cpf"] = self.response["pessoa"].get("id")
        result_dict["data_atualizacao"] = format_date(self.response["pessoa"].get("dataAtualizacaoRfb"))
        result_dict["data_processamento"] = format_date(self.response["pessoa"].get("dataProcessamento"))
        result_dict["cpf"] = self.response["pessoa"].get("id")
        result_dict["situacao_cpf"] = self.response.get("tipoSituacaoCPF") if \
            self.response.get("tipoSituacaoCPF") not in (0, 2, 3, 5) else "REGULAR" if \
            self.response.get("tipoSituacaoCPF") == 0 else "SUSPENSO" if \
            self.response.get("tipoSituacaoCPF") == 2 else "CANCELADO" if \
            self.response.get("tipoSituacaoCPF") == 3 else "FALECIDO" if \
            self.response.get("tipoSituacaoCPF") == 5 else self.response.get("tipoSituacaoCPF")
        result_dict["nascimento"] = format_date(self.response.get("dataNascimento"))
        result_dict["sexo"] = self.response.get("sexo")
        result_dict[
            "telefone"] = f'{self.response["pessoa"].get("numeroDdd")}{self.response["pessoa"].get("numeroTelefone")}'
        result_dict["titulo_eleitor"] = self.response.get("numeroTituloEleitor")
        result_dict["estrangeiro"] = False if self.response.get("situacaoEstrangeiro") == "N" else True
        result_dict["morando_exterior"] = False if self.response.get("situacaoResidenteExterior") == "N" else True
        result_dict["nome_mae"] = self.response.get("nomeMae")
        result_dict["unidade_administrativa"] = self.response.get("idUnidadeAdministrativa")
        result_dict["endereco"] = {}
        result_dict["endereco"]["codigo_municipio"] = self.response["pessoa"].get("idMunicipioIbge")
        result_dict["endereco"]["municipio"] = self.response["pessoa"].get("nomeMunicipio")
        result_dict["endereco"]["bairro"] = self.response["pessoa"].get("nomeBairro")
        result_dict["endereco"]["estado"] = self.response["pessoa"].get("siglaUf")
        result_dict["endereco"]["logradouro"] = self.response["pessoa"].get("nomeLogradouro")
        result_dict["endereco"]["cep"] = self.response["pessoa"].get("numeroCep")
        result_dict["endereco"]["numero"] = self.response["pessoa"].get("numeroLogradouro")
        return result_dict
