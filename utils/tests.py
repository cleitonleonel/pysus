import json
import random
import requests

BASE_URL = 'http://localhost:5000'
# BASE_URL = 'https://pysus-api.herokuapp.com' Não implementado.


def generate_cpf():
    numbers = [random.randint(0, 9) for x in range(9)]
    for _ in range(2):
        val = sum([(len(numbers) + 1 - i) * v for i, v in enumerate(numbers)]) % 11
        numbers.append(11 - val if val > 1 else 0)
    cpf = ''.join(map(str, numbers))
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = self.get_headers()
        self.session = requests.Session()

    def get_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        return self.headers

    def send_request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 200:
            return response
        return None


class ControllerAPI(Browser):

    def __init__(self):
        super().__init__()
        self.document = None

    def data_by_cpf(self):
        self.response = self.send_request('GET', f"{BASE_URL}/api/v1/consult/{self.document}",
                                          headers=self.headers)
        return self.response.json()

    def get_data(self):
        data = {
            "cpf": self.document
        }
        self.response = self.send_request('GET', f"{BASE_URL}/api/v1/consult",
                                          params=data, headers=self.headers)
        return self.response.text

    def post_data(self):
        data = {
            "cpf": self.document,
        }
        self.response = self.send_request('POST', f"{BASE_URL}/api/v1/consult",
                                          json=json.dumps(data), headers=self.headers)
        return self.response.json()


if __name__ == '__main__':
    api = ControllerAPI()
    api.document = generate_cpf()  # Gera cpf`s aleatórios, pode ser passado um cpf válido manualmente.

    get_direct = api.data_by_cpf()
    get_by_payload = api.get_data()
    post_by_data = api.post_data()

    print("RESULTADO MÉTODO GET VIA PARÂMETRO NA URL: ", get_direct)
    print("RESULTADO MÉTODO GET VIA PAYLOAD: ", get_direct)
    print("RESULTADO MÉTODO POST VIA DATA: ", get_direct)
