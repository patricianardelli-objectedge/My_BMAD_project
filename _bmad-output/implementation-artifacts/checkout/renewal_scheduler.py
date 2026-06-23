"""
Renewal Scheduler for Subscriptions
Processes daily subscription renewals at 2 AM UTC
"""

from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

RENEWAL_VERSION = "1.0"

logger = logging.getLogger(__name__)


@dataclass
class RenewalJob:
    """Renewal job tracking"""
    job_id: str
    job_date: date
    subscriptions_found: int = 0
    renewals_created: int = 0
    renewal_failures: int = 0
    status: str = 'pending'  # pending, running, completed, failed
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


def get_interval_days(cadence: str) -> int:
    """Get number of days for subscription cadence"""
    intervals = {
        'one-time': 0,
        'monthly': 30,
        'bi-weekly': 14,
        'bi-month': 14,
        'three-month': 90
    }
    return intervals.get(cadence, 0)


def create_renewal_order(subscription: dict, previous_order: dict) -> Dict:
    """Create a renewal order from subscription and previous order"""
    import uuid
    
    renewal_order = {
        'order_id': str(uuid.uuid4()),
        'user_id': subscription.get('user_id'),
        'email': previous_order.get('email'),
        'status': 'pending',
        'cart_items': previous_order.get('cart_items', []),
        'subscription_data': {
            'cadence': subscription.get('cadence'),
            'start_date': datetime.now().date().isoformat(),
            'initial_price': previous_order.get('total_amount'),
            'recurring_price': previous_order.get('total_amount'),
            'stripe_subscription_id': subscription.get('stripe_subscription_id'),
            'payment_status': 'pending'
        },
        'shipping_address': previous_order.get('shipping_address', {}),
        'billing_address': previous_order.get('billing_address'),
        'total_amount': previous_order.get('total_amount'),
        'currency': previous_order.get('currency', 'USD'),
        'payment_method': previous_order.get('payment_method'),
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    return renewal_order


def calculate_next_billing_date(current_date: date, cadence: str) -> date:
    """Calculate next billing date"""
    days = get_interval_days(cadence)
    if days == 0:
        return None
    return current_date + timedelta(days=days)


def process_subscription_renewals(
    subscriptions: List[dict],
    orders_map: Dict[str, dict]
) -> RenewalJob:
    """
    Process subscription renewals
    Mock implementation (would be called by APScheduler)
    
    Args:
        subscriptions: List of subscriptions due for renewal
        orders_map: Map of order_id -> order data for reference
    
    Returns:
        RenewalJob with results
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    job = RenewalJob(
        job_id=job_id,
        job_date=date.today(),
        started_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    logger.info(f"Renewal job {job_id} starting. Found {len(subscriptions)} subscriptions due for renewal.")
    
    try:
        job.subscriptions_found = len(subscriptions)
        
        for subscription in subscriptions:
            try:
                order_id = subscription.get('order_id')
                previous_order = orders_map.get(order_id, {})
                
                if not previous_order:
                    job.renewal_failures += 1
                    logger.warning(f"Could not find previous order {order_id} for subscription {subscription.get('subscription_id')}")
                    continue
                
                # Create renewal order
                renewal_order = create_renewal_order(subscription, previous_order)
                
                # Calculate next billing date
                cadence = subscription.get('cadence', 'monthly')
                interval_days = get_interval_days(cadence)
                
                if interval_days > 0:
                    current_next_date = date.today()
                    new_next_date = calculate_next_billing_date(current_next_date, cadence)
                    
                    # Update subscription (in real app, this would update DB)
                    # subscription['next_billing_date'] = new_next_date.isoformat()
                    
                    job.renewals_created += 1
                    logger.info(f"Renewal created for subscription {subscription.get('subscription_id')}: "
                              f"Order {renewal_order['order_id']}, Next billing: {new_next_date}")
                else:
                    # One-time subscription, skip renewal
                    logger.debug(f"Skipping one-time subscription {subscription.get('subscription_id')}")
                
            except Exception as e:
                job.renewal_failures += 1
                logger.error(f"Error processing renewal for subscription {subscription.get('subscription_id')}: {str(e)}")
        
        job.status = 'completed'
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        logger.error(f"Renewal job {job_id} failed: {str(e)}")
    
    job.completed_at = datetime.utcnow().isoformat() + 'Z'
    
    # Log results
    logger.info(f"Renewal job {job_id} completed: "
              f"{job.subscriptions_found} found, "
              f"{job.renewals_created} created, "
              f"{job.renewal_failures} failures")
    
    return job


def create_renewal_scheduler_config() -> Dict:
    """
    Create scheduler configuration for APScheduler
    This would be used in app initialization
    """
    return {
        'trigger': 'cron',
        'hour': 2,
        'minute': 0,
        'timezone': 'UTC',
        'id': 'subscription_renewal_job',
        'name': 'Process Subscription Renewals',
        'max_instances': 1,  # Prevent concurrent executions
        'replace_existing': True
    }


def send_renewal_failure_alert(job: RenewalJob, alert_recipients: List[str]) -> bool:
    """
    Send alert email if renewal job had failures
    """
    if job.status == 'failed' or job.renewal_failures > 0:
        # In production, send via email service
        logger.warning(f"Renewal job {job.job_id} had {job.renewal_failures} failures. "
                      f"Alert recipients: {alert_recipients}")
        return True
    return False


def send_payment_failed_notification(order_id: str, email: str, error_message: str) -> bool:
    """
    Send customer notification for failed payment
    """
    # In production, send via email service
    subject = "Payment Failed - Action Needed"
    body = f"""
    Your subscription renewal payment failed: {error_message}
    
    Please update your payment method to continue receiving deliveries.
    
    Order ID: {order_id}
    """
    
    logger.info(f"Payment failure notification would be sent to {email} for order {order_id}")
    return True
