import pika
import pandas as pd
from datetime import datetime
import os


def validate_user_login(username, password, csv_path="user_cred.csv"):
    csv_path = os.path.abspath(csv_path)
    try:
        df = pd.read_csv(csv_path)
        mask = (df["username"] == username) & (df["password"] == password)

        if not df[mask].empty:
            # found user and pass combination- overwrite last login info
            last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[mask, "LastLogin"] = last_login

            # Write back to the CSV file
            df.to_csv(csv_path, index=False)
            return f"Login success -{username} on {last_login}"

    except Exception as e:
        print(f"Exception occured: {e}")

    return "Login failed"


def on_request(ch, method, properties, body):
    body_str = body.decode("utf-8")
    username, password = body_str.split(",")

    response = validate_user_login(username, password)

    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=str(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="login_queue")
    channel.basic_consume(queue="login_queue", on_message_callback=on_request)

    print("Login server is waiting for requests. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
