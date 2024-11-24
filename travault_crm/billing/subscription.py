from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from agencies.models import CustomUser
from .models import StripeCustomer
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def update_subscription_quantity(stripe_customer):
    """
    Update the Stripe subscription quantity based on the number of users in an agency.
    
    Args:
        stripe_customer (StripeCustomer): The StripeCustomer instance containing subscription details
        
    Returns:
        Subscription: The updated Stripe subscription object if quantity changed,
                     or existing subscription if no change needed
        
    Raises:
        Exception: Any Stripe API errors or database errors that occur during the update
        
    Example:
        stripe_customer = agency.stripecustomer
        updated_subscription = update_subscription_quantity(stripe_customer)
    """
    try:
        # Get current user count
        user_count = stripe_customer.agency.users.count()
        logger.info(f"Updating subscription for agency {stripe_customer.agency.agency_name}. User count: {user_count}")

        # Get current subscription
        subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)
        current_quantity = subscription['items']['data'][0]['quantity']

        # Only update if the quantity is different
        if current_quantity != user_count:
            logger.info(f"Updating quantity from {current_quantity} to {user_count}")
            
            updated_sub = stripe.Subscription.modify(
                stripe_customer.stripe_subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'quantity': user_count
                }]
            )
            logger.info(f"Successfully updated subscription quantity to {user_count}")
            return updated_sub
        else:
            logger.info("Quantity unchanged, no update needed")
            return subscription

    except Exception as e:
        logger.error(f"Error updating subscription quantity: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=CustomUser)
def update_subscription_on_user_change(sender, instance, created, **kwargs):
    """
    Signal handler to update Stripe subscription when a user is created or modified.
    
    Args:
        sender (Model): The model class (CustomUser)
        instance (CustomUser): The user instance that was saved
        created (bool): True if this is a new instance, False if it's an update
        **kwargs: Additional keyword arguments passed by the signal
        
    Note:
        This function is automatically called by Django's post_save signal whenever
        a CustomUser is created or updated. It checks if the user belongs to an
        agency and updates the corresponding Stripe subscription quantity.
        
    Example:
        # Signal is automatically triggered on user save:
        user.save()  # Triggers this handler
    """
    logger.info(f"User change detected for {instance.email}")
    
    try:
        # Check if user has an agency
        if instance.agency:
            logger.info(f"Processing for agency: {instance.agency.agency_name}")
            
            # Get or create StripeCustomer
            stripe_customer = instance.agency.stripecustomer
            
            if stripe_customer and stripe_customer.stripe_subscription_id:
                update_subscription_quantity(stripe_customer)
            else:
                logger.warning(f"No active subscription found for agency {instance.agency.agency_name}")
        else:
            logger.info(f"User {instance.email} not associated with any agency")

    except StripeCustomer.DoesNotExist:
        logger.warning(f"No StripeCustomer found for agency {instance.agency.agency_name}")
    except Exception as e:
        logger.error(f"Error in subscription update signal: {str(e)}", exc_info=True)

@receiver(post_delete, sender=CustomUser)
def update_subscription_on_user_delete(sender, instance, **kwargs):
    """
    Signal handler to update Stripe subscription when a user is deleted.
    
    Args:
        sender (Model): The model class (CustomUser)
        instance (CustomUser): The user instance that was deleted
        **kwargs: Additional keyword arguments passed by the signal
        
    Note:
        This function is automatically called by Django's post_delete signal
        whenever a CustomUser is deleted. It updates the Stripe subscription
        quantity to reflect the reduced number of users.
        
    Example:
        # Signal is automatically triggered on user delete:
        user.delete()  # Triggers this handler
    """
    logger.info(f"User deletion detected for {instance.email}")
    
    try:
        # Check if user had an agency
        if hasattr(instance, 'agency') and instance.agency:
            logger.info(f"Processing deletion for agency: {instance.agency.agency_name}")
            
            # Get StripeCustomer
            stripe_customer = instance.agency.stripecustomer
            
            if stripe_customer and stripe_customer.stripe_subscription_id:
                update_subscription_quantity(stripe_customer)
            else:
                logger.warning(f"No active subscription found for agency {instance.agency.agency_name}")
        else:
            logger.info(f"Deleted user {instance.email} was not associated with any agency")

    except StripeCustomer.DoesNotExist:
        logger.warning(f"No StripeCustomer found for agency")
    except Exception as e:
        logger.error(f"Error in subscription update signal on deletion: {str(e)}", exc_info=True)