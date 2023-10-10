## Syncflow 🌐

- **Syncflow acts as an intermediary**, acting as a bridge between external systems and our internal database 🌉.
- **No point of contact between two external system** ,The idea is to let syncflow do  all the communication needed between all systems to syncronise.
- **Lot of Utility Classes**, syncflow has many utility class that can directly be inherited which will helps in various task needed for syncronisation.

## Synchronization Types 🔄

- **Inwards Synchronization**: When changes occur in external systems, our goal is to update our internal database and all other relevant systems `(ALL external system - system  from which changes occured)`.

- **Outwards Synchronization**: If data within our internal database undergoes changes, we need to efficiently communicate and propagate these changes to **ALL** external systems.

## Implementation Insights 🧩

### The Orchestra Model: Keeping it in Harmony 🎶

Our synchronization model is similar to a music orchestra, comprising two essential components:

#### The MainClass: The Conductor 🎩

- The MainClass orchestrates data synchronization, strategically deciding when and how data should flow between systems. 🎶
- It manages a list of SubscriberClasses and controls when to call their methods. 📋
- We can easily pass an unsubscribe array in mainclass to stop data flow to certain systems.

#### The Subscribers: The Musicians 🎻

- Subscriber Classes are tasked with specific synchronization responsibilities (CRUD or more) and validation. 🎵
- They adeptly handle updates from external systems (Inwards Sync) or facilitate data exchange with external systems (Outwards Sync). 🎼
- `SubscriberBaseClass` aims to provide all the general utility to help in writing code for syncronisation logic.
- A subscriber class keeps a `field_to_data` mapping with a database table.

## Key Advantages of Our Approach ✨

- **Adaptability**: Integrating new systems is very easy. Create a Subscriber class, register it with the MainClass, and let automation handle the rest.
- **Simplicity**: No need for complex data flows.
- **Efficiency**: Data moves seamlessly and expeditiously.
- **Control**: Oversee everything seamlessly from a central hub (Django admin + flower web interface).

### Inward Data Synchronization Strategies 📊

This can be achieved through two distinct methods, depending on the system:

#### Periodic API Polling ⏰

- At regular intervals, APIs are invoked to check for any system changes.
- Implemented using the celery-beat library in our system.
- Simply define when APIs will be called in the Celery configurations of `settings.py` and outline the desired data handling in `tasks.py`.

#### Webhooks 🌐

- Alternatively, we can actively listen to webhooks from external services.
- We can define an API endpoint where POST requests can be elegantly handled within `views.py`. Here, the code defines the actions taken when webhooks are received, while the MainClass and other Subscriber Classes manage the rest of the process.

### Vulnerability and its Solution 🛡️

#### Vulnerability: Single Failure Can Be Fatal 🚨

In our system, Syncflow serves as the central medium connecting all systems. It's like to a single node in a network graph from which all other nodes are connected. Consequently, if Syncflow were to go down, the entire synchronization process would be disrupted. 😱

#### Solution: Harnessing the Power of Message Queues

Message queues are a robust solution to this challenge. They act as intermediary buffers that temporarily store and manage messages between systems. When Syncflow communicates with external systems or internal processes, it sends messages to a message queue instead of direct communication.

This approach offers several benefits:

- **Fault Tolerance**: If Syncflow experiences downtime, messages remain safely stored in the queue until it's up and running again. No data is lost. 🛡️
- **Load Balancing**: Message queues can distribute the workload efficiently, preventing overload and ensuring smooth data flow. ⚖️
- **Scalability**: As your system grows, you can easily scale your message queue infrastructure to handle increased traffic. 📈
- **Asynchronous Processing**: Message queues enable asynchronous communication, reducing system bottlenecks and enhancing overall performance. 🚀

By implementing message queues, we significantly enhance the reliability and fault tolerance of our synchronization system, safeguarding against single points of failure. 🌐🚀

## Other Pages
- [Local Setup](#local-setup)
- [How this works](./How-it-works.md)
- [SalesForce syncronisation](./salesforce-integration.md)
- [Extending syncronisation to other catalouge](./invoice-integgration.md)

