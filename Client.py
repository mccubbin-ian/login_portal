import pika
import uuid


class LoginClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = body.decode("utf-8")

    def login(self, username, password):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key="login_queue",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=self.corr_id
            ),
            body=f"{username},{password}",
        )

        while self.response is None:
            self.connection.process_data_events()

        return self.response


def main():
    login_client = LoginClient()

    # Example usage
    username = "user1"
    password = "pwd1"

    response = login_client.login(username, password)
    print(f"Server response: {response}")


if __name__ == "__main__":
    main()
