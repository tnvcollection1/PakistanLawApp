import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

export default function FeedbackPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    toast.success("Feedback submitted! Thank you.");
    setName("");
    setEmail("");
    setMessage("");
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Feedback</h1>
      <p className="text-muted-foreground mb-6">
        We value your feedback. Please let us know how we can improve.
      </p>
      <Separator className="my-6" />
      <form onSubmit={handleSubmit} className="max-w-lg space-y-4">
        <div>
          <label className="text-sm font-medium">Name</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div>
          <label className="text-sm font-medium">Email</label>
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <label className="text-sm font-medium">Message</label>
          <Textarea value={message} onChange={(e) => setMessage(e.target.value)} required />
        </div>
        <Button type="submit">Submit Feedback</Button>
      </form>
    </div>
  );
}
