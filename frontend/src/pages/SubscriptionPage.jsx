import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Check } from "lucide-react";

export default function SubscriptionPage() {
  const [email, setEmail] = useState("");
  const [plan, setPlan] = useState("monthly");

  const plans = [
    { id: "monthly", name: "Monthly", price: "PKR 1,500/month" },
    { id: "yearly", name: "Yearly", price: "PKR 15,000/year" },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Subscribed with ${email} on ${plan} plan`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Subscription</h1>
      <p className="text-muted-foreground mb-6">
        Choose a plan to access premium features.
      </p>
      <Separator className="my-6" />
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        {plans.map((p) => (
          <div
            key={p.id}
            className={`rounded-lg border p-6 cursor-pointer ${plan === p.id ? "border-primary" : ""}`}
            onClick={() => setPlan(p.id)}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">{p.name}</h2>
              {plan === p.id && <Check className="h-5 w-5 text-primary" />}
            </div>
            <p className="text-2xl font-bold">{p.price}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="max-w-md space-y-4">
        <Input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Button type="submit" className="w-full">
          Subscribe
        </Button>
      </form>
    </div>
  );
}
