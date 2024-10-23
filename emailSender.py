import time
import mysql.connector
import requests

# Configurações do banco de dados MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pass',
    'database': 'vpc_vpc',
    'port': 3306
}

# Configurações da API Brevo
api_key = "api"
api_url = "https://api.brevo.com/v3/smtp/email"

# Função para enviar email via API Brevo
def enviar_email(destinatario, assunto, mensagem):
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    data = {
        "sender": {"name": "Sender Name", "email": "sendername@gmail.com"},
        "to": [{"email": destinatario}],
        "subject": assunto,
        "htmlContent": f"<html><body>{mensagem}</body></html>"
    }

    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 201:
        print(f"Email enviado com sucesso para {destinatario}!")
    else:
        print(f"Erro ao enviar email: {response.status_code}")
        print(response.text)

# Função para verificar e enviar as mensagens
def process_mensageria():
    try:
        # Conecta ao banco de dados
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Consulta para buscar mensagens com status 0
        query = "SELECT * FROM vpc_mensageria WHERE VPC_MEN_STATUS = 0"
        cursor.execute(query)
        messages = cursor.fetchall()

        for message in messages:
            # Envia o e-mail via API
            enviar_email(message['VPC_MEN_EMAIL_DESTINATARIO'], message['VPC_MEN_TITULO'], message['VPC_MEN_MENSAGEM'])

            # Atualiza o status da mensagem para 1 após o envio
            update_query = "UPDATE vpc_mensageria SET VPC_MEN_STATUS = 1 WHERE VPC_MEN_ID = %s"
            cursor.execute(update_query, (message['VPC_MEN_ID'],))
            connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Erro no banco de dados: {err}")

# Loop que executa a verificação a cada 10 segundos
if __name__ == "__main__":
    while True:
        process_mensageria()
        time.sleep(10)
