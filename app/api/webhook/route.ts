import { NextRequest } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(req: NextRequest) {
  try {
    const body = await req.text();
    const signature = req.headers.get('stripe-signature');

    if (!signature) {
      return Response.json({ error: 'No signature' }, { status: 400 });
    }

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
    } catch (err: any) {
      console.error('Webhook signature verification failed:', err.message);
      return Response.json({ error: 'Invalid signature' }, { status: 400 });
    }

    // Handle the event
    switch (event.type) {
      case 'checkout.session.completed':
        const session = event.data.object as Stripe.Checkout.Session;
        console.log('Payment successful:', session.id);

        // TODO:
        // 1. Create customer record in database
        // 2. Send welcome email
        // 3. Trigger initial lead generation
        // 4. Set up delivery schedule

        await handleSuccessfulPayment(session);
        break;

      case 'customer.subscription.updated':
      case 'customer.subscription.deleted':
        const subscription = event.data.object as Stripe.Subscription;
        console.log('Subscription changed:', subscription.id);

        // TODO: Update customer subscription status
        await handleSubscriptionChange(subscription);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return Response.json({ received: true });
  } catch (error: any) {
    console.error('Webhook error:', error);
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

async function handleSuccessfulPayment(session: Stripe.Checkout.Session) {
  console.log('New customer:', {
    sessionId: session.id,
    customerId: session.customer,
    email: session.customer_details?.email,
    subscriptionId: session.subscription,
  });

  // TODO: Implement customer onboarding
  // - Create database record
  // - Send welcome email with ICP form
  // - Schedule first lead generation job
}

async function handleSubscriptionChange(subscription: Stripe.Subscription) {
  console.log('Subscription update:', {
    id: subscription.id,
    status: subscription.status,
    customerId: subscription.customer,
  });

  // TODO: Implement subscription management
  // - Update customer tier/limits
  // - Pause/resume lead generation
  // - Handle cancellations
}
