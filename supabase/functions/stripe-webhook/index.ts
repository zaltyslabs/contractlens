// Supabase Edge Function: Stripe Webhook Handler
// Deploy: supabase functions deploy stripe-webhook
// 
// Handles:
//   - checkout.session.completed → upgrade user's subscription tier
//   - customer.subscription.deleted → downgrade to free
//   - customer.subscription.updated → sync tier changes

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import Stripe from "https://esm.sh/stripe@13.11.0?target=deno";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY")!, {
      apiVersion: "2023-10-16",
      httpClient: Stripe.createFetchHttpClient(),
    });

    const signature = req.headers.get("stripe-signature")!;
    const body = await req.text();
    const webhookSecret = Deno.env.get("STRIPE_WEBHOOK_SECRET")!;

    let event: Stripe.Event;
    try {
      event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
    } catch (err) {
      return new Response(`Webhook signature verification failed: ${err.message}`, {
        status: 400,
        headers: corsHeaders,
      });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    console.log(`Processing: ${event.type}`);

    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object;
        const customerEmail = session.customer_details?.email;
        const metadata = session.metadata || {};
        const tier = metadata.tier || "side_hustler";

        if (!customerEmail) {
          console.log("No email in session, skipping");
          break;
        }

        // Look up user by email
        const { data: profiles, error: lookupError } = await supabase
          .from("profiles")
          .select("id")
          .eq("email", customerEmail)
          .limit(1);

        if (lookupError || !profiles?.length) {
          console.log(`User not found for email: ${customerEmail}`);
          break;
        }

        await updateSubscription(
          supabase,
          profiles[0].id,
          tier,
          session.customer as string,
          session.subscription as string,
        );

        console.log(`Upgraded ${customerEmail} to ${tier}`);
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data.object;
        const customerId = subscription.customer as string;

        const { data: profiles } = await supabase
          .from("profiles")
          .select("id")
          .eq("stripe_customer_id", customerId)
          .limit(1);

        if (profiles?.length) {
          await updateSubscription(supabase, profiles[0].id, "free", customerId, null);
          console.log(`Downgraded customer ${customerId} to free`);
        }
        break;
      }

      case "customer.subscription.updated": {
        const subscription = event.data.object;
        const customerId = subscription.customer as string;

        // Only act on active subscriptions with a price
        if (subscription.status !== "active") break;

        const priceId = subscription.items?.data?.[0]?.price?.id;
        const tier = getTierFromPriceId(priceId);

        if (tier) {
          const { data: profiles } = await supabase
            .from("profiles")
            .select("id")
            .eq("stripe_customer_id", customerId)
            .limit(1);

          if (profiles?.length) {
            await updateSubscription(supabase, profiles[0].id, tier, customerId, subscription.id);
            console.log(`Synced tier for customer ${customerId}: ${tier}`);
          }
        }
        break;
      }
    }

    return new Response(JSON.stringify({ received: true }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("Webhook error:", err);
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

// ── Helpers ──

const TIER_LIMITS: Record<string, number> = {
  free: 1,
  side_hustler: 5,
  power_freelancer: 20,
  agency: 50,
};

function getTierFromPriceId(priceId: string): string | null {
  // Map your Stripe price IDs to tier names
  const priceMap: Record<string, string> = {
    "price_1TaJVTRNLvxcQdtwhyN6WhI9": "side_hustler",
    "price_1TaJVaRNLvxcQdtwU2uAwGPj": "power_freelancer",
    "price_1TaJVfRNLvxcQdtwOZeV74j6": "agency",
  };
  return priceMap[priceId] || null;
}

async function updateSubscription(
  supabase: any,
  userId: string,
  tier: string,
  stripeCustomerId: string,
  stripeSubscriptionId: string | null,
) {
  const limit = TIER_LIMITS[tier] || 1;

  await supabase
    .from("profiles")
    .update({
      subscription_tier: tier,
      scans_limit: limit,
      stripe_customer_id: stripeCustomerId,
      stripe_subscription_id: stripeSubscriptionId,
      updated_at: new Date().toISOString(),
    })
    .eq("id", userId);
}
