# 🚀 SyncFlow

![SyncFlow Diagram](https://github.com/melencholicmice/Reverberance2022/assets/109169835/7a053298-5ff8-476b-ac90-f8b1880abb20)

Welcome to SyncFlow, a powerful tool for synchronizing data with external services effortlessly!

## Tech Stack Used 🧑‍💻
- Python 🐍
- Django (Django ORM for communicating with the DB, web framework for accepting webhook data) 🦄
- RabbitMQ (as a message queue between Celery (consumer) and Django (producer)) 🐇
- Redis (as a backend result storage)
- Celery (to spawn workers and as a consumer for RabbitMQ) 🥬
- Celery Beat (for API polling and periodic task scheduling, not required if no periodic task scheduling exists)
- [`Optional`] Flower (web interface) to monitor Celery tasks 🌻

## Features 👀
- Integrate with one connect with all
- Easy Framework for Data Synchronization with External Services
- Removes repetitive tasks, so you can focus on integration only.
- High Fault Tolerance using RabbitMQ and Redis
- Fast Performance using Celery

## Content 🗒️

- [Local Setup](#local-setup)
- [How This Works](./How-it-works.md)
- [SalesForce Synchronization](./salesforce-integration.md)
- [Extending Synchronization to Other Catalogs](./invoice-integration.md)

## Setup

### Prerequisites of Setup
- Python 3.8+
- [Rabbit MQ](https://www.rabbitmq.com/download.html)
- [Redis](https://redis.io/download)

**Step 1: Clone the repository.**

**Step 2: Create a virtual environment (recommended):**
```shell
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Enter the SyncFlow directory, our whole application lies there.**

**Step 4: Install dependencies:**
```shell
pip install -r requirements.txt
```

**Step 5: Apply migrations:**
```shell
python manage.py migrate
```

**Step 6: Create a .env file and place it in the same directory as the README. Your .env should look like:**
```python
SECRET_KEY =
STRIPE_API_KEY =
STRIPE_ENDPOINT_SECRET =
CELERY_BROKER_URL =   # RabbitMQ URL in our case but can be other message queues as well
CELERY_RESULT_BACKEND = # Redis in our case but can be something else
FLOWER_BROKER = # RabbitMQ in our case
FLOWER_PORT =
```

**Step 7: Make sure RabbitMQ and Redis are running.**

**Step 8: Start the development server:**
```shell
python manage.py runserver
```

**Step 9: Start Celery Worker**

In a new terminal window, navigate to your project directory and start the Celery worker:
```bash
celery -A syncflow worker --loglevel=info
```

**Step 10: Start Celery Beat**

If you have periodic tasks that need to be scheduled, you can start Celery Beat:
```bash
celery -A syncflow beat --loglevel=info
```

**Step 11: Monitor Celery Tasks (Optional)**

To monitor your Celery tasks, you can use tools like Flower. Populate your .env with Flower configurations.
```bash
celery flower -A syncflow --port=5555
```

You can access the Flower dashboard at `http://localhost:5555`.

That's it! Your Django app with Celery, RabbitMQ, and Redis is up and running. You can now use Celery to perform background tasks and monitor their progress if needed.
