import re
from flask import Flask, request, redirect
from os import getcwd
from api.health_brazil import SusApi, json
from urllib.parse import quote_plus

BASE_DIR = getcwd()

app = Flask(__name__, template_folder='templates')

app.jinja_env.filters['quote_plus'] = lambda u: quote_plus(u)


def get_data(document):
    sus = SusApi()
    string = re.sub("\.|\-|\?", "", document)
    result = sus.consult_data(string)
    if isinstance(result, list):
        json_data = result[0]
    else:
        json_data = sus.parse_data()
    return json_data


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/api/v1/consult')


@app.route('/api/v1/consult', methods=['GET', 'POST'])
@app.route('/api/v1/consult/<cpf>', methods=['GET', 'POST'])
def consult(cpf=None):
    message = "Use com moderação!"
    result = True
    object_data = []
    if not cpf:
        if request.method == 'POST':
            body = json.loads(request.get_json())
            cpf = body['cpf']
            object_data = get_data(cpf)
        elif request.method == 'GET':
            cpf = request.args.get('cpf')
            if not cpf:
                result = False
                message = "Erro, nenhum cpf informado!"
            else:
                object_data = get_data(cpf)
    else:
        object_data = get_data(cpf)
    return {
        "result": result,
        "object": object_data,
        "message": message
    }


if __name__ == "__main__":
    app.run(host='0.0.0.0')
