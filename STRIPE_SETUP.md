# Stripe Setup Guide

## Quick Start (5 minutes to first payment)

### 1. Create Stripe Account
1. Go to https://stripe.com and sign up
2. Complete basic account setup

### 2. Get Your API Keys
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Copy your **Secret key** (starts with `sk_test_`)

### 3. Create Products & Prices in Stripe

Go to https://dashboard.stripe.com/test/products and create 3 products:

**Product 1: Starter**
- Name: WalterFetch Starter
- Price: $99/month (recurring)
- Copy the Price ID (starts with `price_`)

**Product 2: Pro**
- Name: WalterFetch Pro
- Price: $249/month (recurring)
- Copy the Price ID (starts with `price_`)

**Product 3: Enterprise**
- Name: WalterFetch Enterprise
- Price: $499/month (recurring)
- Copy the Price ID (starts with `price_`)

### 4. Add Environment Variables to Vercel

1. Go to your Vercel project settings
2. Navigate to Settings > Environment Variables
3. Add these variables:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
NEXT_PUBLIC_URL=https://your-site.vercel.app
```

### 5. Update Price IDs in Code

Edit `app/page.tsx` and replace the placeholder price IDs:

```typescript
const plans = [
  {
    name: 'Starter',
    price: 99,
    priceId: 'price_YOUR_STARTER_PRICE_ID' // Replace this
  },
  {
    name: 'Pro',
    price: 249,
    priceId: 'price_YOUR_PRO_PRICE_ID' // Replace this
  },
  {
    name: 'Enterprise',
    price: 499,
    priceId: 'price_YOUR_ENTERPRISE_PRICE_ID' // Replace this
  }
]
```

### 6. Test It!

1. Click any "Get Started" button on your site
2. Use Stripe test card: `4242 4242 4242 4242`
3. Any future expiry date, any CVC
4. Complete checkout

### 7. Go Live (When Ready)

1. Get real API keys from https://dashboard.stripe.com/apikeys (live mode)
2. Create real products in live mode
3. Update Vercel environment variables with live keys
4. Update price IDs to live price IDs

## Test Card Numbers

- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

Use any future date and any 3-digit CVC.

## Monitoring Payments

View all test payments at:
https://dashboard.stripe.com/test/payments

## Support

Questions? Email hello@waltersignal.ai
