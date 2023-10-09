# 🚀 SyncFlow

Welcome to the Syncflow, a powerful tool for synchronizing data with external services effortlessly!

## Features
- ✅ Data Synchronization with External Services
- 🐍 Powered by Django

## Content

- [Local Setup](#local-setup)
- [How this works](./How-it-works.md)
- [SalesForce syncronisation](./salesforce-integration.md)
- [Extending syncronisation to other catalouge](./invoice-integgration.md)



## Setup

### Prerequisites of Setup
- Python 3.8+
- [Rabbit MQ](https://www.rabbitmq.com/download.html)
- [Reddis](https://redis.io/download)

**Step 1: Clone the repository.**

**Step 2: Create a virtual environment (recommended):**
   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```
**Step 3. Enter syncflow directory, our whole application lies there.**

**Step 4: Install dependencies:**
   ```shell
   pip install -r requirements.txt
   ```

**Step 5: Apply migrations:**
   ```shell
   python manage.py migrate
   ```

**Step 6: Create a .env file and place it in same directory as readme, your .env should look like:**
   ```python
SECRET_KEY =
STRIPE_API_KEY =
STRIPE_ENDPOINT_SECRET =
CELERY_BROKER_URL =   # RabbitMQ URL in our case but can be other message queues as well
CELERY_RESULT_BACKEND = # reddis in our case but can be something else
FLOWER_BROKER = # rabbitMQ in our case
FLOWER_PORT =
 ```

**Step 7: Make sure rabbitMQ and Reddis running**

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

**Step 6: Monitor Celery Tasks (Optional)**

To monitor your Celery tasks, you can use tools like Flower, Populate your .env with flower configurations.
```bash
celery flower -A syncflow --port=5555
```

You can access the Flower dashboard at `http://localhost:5555`.

That's it! Your Django app with Celery, RabbitMQ, and Redis is up and running. You can now use Celery to perform background tasks and monitor their progress if needed.

## Usage
- Configure your data synchronization settings in `settings.py`.
- Create Django models for the data you want to sync.
- Implement synchronization logic in your Django views or management commands.
