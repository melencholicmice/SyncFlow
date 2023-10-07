import stripe



class CustomerCRUD:
    API_KEY = None  # Class-level variable to store the API key

    @classmethod
    def initialize(cls, api_key):
        cls.API_KEY = api_key

    @staticmethod
    def create_customer(**kwargs):
        if CustomerCRUD.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")

        stripe.Customer.create(
            email=kwargs['instance'].email,
            name=kwargs['instance'].name,
            api_key=CustomerCRUD.API_KEY
        )

    @staticmethod
    def delete_customer(**kwargs):

        if CustomerCRUD.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")

        try:
            customers = stripe.Customer.list(
                email=kwargs['instance'].email,
                api_key=CustomerCRUD.API_KEY
            )
            customer_id = customers['data'][0]['id']
        except:
            # :TODO: Add to dead letter queue
            return

        try:
            stripe.Customer.delete(customer_id,
                api_key=CustomerCRUD.API_KEY
            )
        except:
            # :TODO: - use dead letter queue here
            return
        return

    @staticmethod
    def update_customer(**kwargs):
        if CustomerCRUD.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")

        try:
            customers = stripe.Customer.list(
                    email=kwargs['original_fields'].email,
                    api_key=CustomerCRUD.API_KEY
            )


            customer_id = customers['data'][0]['id']
        except:
            # :TODO: - use dead letter queue here
            return

        update_params = kwargs["updated_params"]

        try:
            stripe.Customer.modify(customer_id,
                **update_params, # dictioniary unpacking
                api_key = CustomerCRUD.API_KEY
            )
        except stripe.error.StripeError as e:
            # :TODO: use a dead letter queue here
            print(f"Error updating customer: {e}")



