import { SignedIn, SignedOut, SignInButton } from "@clerk/nextjs";
import {
  Activity,
  Banknote,
  BrainCircuit,
  CalendarRange,
  CircleCheck,
  Clock3,
  Command,
  Landmark,
  Mail,
  Radar,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import Link from "next/link";

import { LivePreview } from "@/components/landing/live-preview";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const features = [
  {
    icon: Radar,
    title: "Situational awareness",
    description:
      "Watch cash posture, obligations, and runway signals in one place without switching between disconnected tools.",
  },
  {
    icon: BrainCircuit,
    title: "Foresight with context",
    description:
      "Understand what changed and why with plain-language driver cards and scenario planning that feels operational.",
  },
  {
    icon: Activity,
    title: "Calm monitoring",
    description:
      "Surface spend spikes, duplicate payments, and subscription creep with confidence labels instead of alarm noise.",
  },
  {
    icon: CalendarRange,
    title: "Timing control",
    description:
      "Model payroll, vendors, and debt obligations to shift payment timing and improve cash runway safely.",
  },
];

const pricing = [
  {
    name: "Free",
    price: "$0",
    subtitle: "Operator baseline",
    points: [
      "Command center with demo mode",
      "Single institution connection",
      "Core runway and obligations views",
      "Basic anomaly alerts",
    ],
  },
  {
    name: "Pro",
    price: "$149/mo",
    subtitle: "Team command center",
    points: [
      "Unlimited institutions and sync jobs",
      "Scenario modeling and payroll planning",
      "Guidance summaries + operator prompts",
      "Priority support and billing controls",
    ],
    highlighted: true,
  },
];

const steps = [
  {
    icon: Landmark,
    title: "Connect financial data",
    detail: "Securely connect institutions in minutes and begin scoped sync by organization.",
  },
  {
    icon: Clock3,
    title: "Review current posture",
    detail: "Start each day with cash position, obligations timing, and runway under active scenarios.",
  },
  {
    icon: ShieldCheck,
    title: "Act with confidence",
    detail: "Use anomaly and guidance signals to choose timing adjustments before risk compounds.",
  },
];

const outcomes = [
  { icon: Users, value: "32%", label: "faster weekly operator reviews" },
  { icon: Banknote, value: "45 days", label: "average runway extension after timing changes" },
  { icon: Sparkles, value: "3-5", label: "guided questions generated per cycle" },
];

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[linear-gradient(160deg,#f8fbf9_0%,#eef6f3_45%,#f7f4ee_100%)]">
      <div className="pointer-events-none absolute -left-16 top-8 h-60 w-60 rounded-full bg-emerald-200/40 blur-3xl animate-float-slow" />
      <div className="pointer-events-none absolute right-6 top-24 h-72 w-72 rounded-full bg-amber-200/35 blur-3xl animate-float-reverse" />

      <section className="mx-auto grid max-w-7xl gap-10 px-6 pb-16 pt-16 lg:grid-cols-[1.15fr_1fr] lg:pt-20">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-emerald-800">
            <Command className="h-3.5 w-3.5" /> keystone
          </p>

          <h1 className="mt-6 max-w-3xl text-4xl font-semibold tracking-tight text-slate-900 md:text-6xl md:leading-[1.05]">
            Financial command center for operators who need clarity before the next move.
          </h1>

          <p className="mt-6 max-w-2xl text-lg text-slate-600">
            Keystone gives your operating team one calm surface for current posture, near-term risk, and next-step
            guidance across cash, runway, payroll, and obligations.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <SignedOut>
              <SignInButton mode="modal" forceRedirectUrl="/app/settings" fallbackRedirectUrl="/app/settings">
                <Button className="h-11 px-5 text-sm">Start with Clerk sign-in</Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/app">
                <Button className="h-11 px-5 text-sm">Open command center</Button>
              </Link>
            </SignedIn>
            <Link href="/#pricing">
              <Button variant="outline" className="h-11 border-slate-300 px-5 text-sm">
                View pricing
              </Button>
            </Link>
          </div>

          <div className="mt-10 grid gap-3 sm:grid-cols-3">
            <ValuePill icon={Landmark} title="Unified accounts" text="Plaid-powered sync with org scoping." />
            <ValuePill icon={Banknote} title="Runway drivers" text="What changed, and exactly why." />
            <ValuePill icon={Sparkles} title="Action prompts" text="3-5 questions for your next operator review." />
          </div>
        </div>

        <div className="lg:pt-4">
          <LivePreview />
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl scroll-mt-24 px-6 py-12 pt-16">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="border-white/70 bg-white/85 backdrop-blur">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <feature.icon className="h-4 w-4 text-emerald-700" />
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm leading-relaxed text-slate-600">{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="mx-auto max-w-7xl scroll-mt-24 px-6 py-12 pt-16">
        <div className="mb-8">
          <h2 className="text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">How Keystone fits your weekly operating rhythm</h2>
          <p className="mt-3 max-w-2xl text-slate-600">
            From first sync to decision cadence, Keystone is designed to support operators managing uncertainty.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((step, idx) => (
            <Card key={step.title} className="border-slate-200 bg-white/90">
              <CardHeader>
                <CardDescription className="text-xs uppercase tracking-[0.18em] text-slate-500">Step {idx + 1}</CardDescription>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <step.icon className="h-4 w-4 text-emerald-700" />
                  {step.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">{step.detail}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="insights" className="mx-auto max-w-7xl scroll-mt-24 px-6 py-12 pt-16">
        <Card className="border-slate-200 bg-white/90">
          <CardHeader>
            <CardTitle className="text-2xl tracking-tight">Operator outcomes that compound over time</CardTitle>
            <CardDescription className="text-slate-600">
              Teams that centralize finance operations in Keystone reduce reaction time and improve planning quality.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            {outcomes.map((outcome) => (
              <div key={outcome.label} className="rounded-lg border border-border/70 bg-muted/30 p-4">
                <p className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                  <outcome.icon className="h-4 w-4 text-emerald-700" />
                  metric
                </p>
                <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{outcome.value}</p>
                <p className="mt-1 text-sm text-slate-600">{outcome.label}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section id="pricing" className="mx-auto max-w-7xl scroll-mt-24 px-6 py-16 pt-20">
        <div className="mb-8">
          <h2 className="text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">Pricing that scales with your operating cadence</h2>
          <p className="mt-3 max-w-2xl text-slate-600">
            Start free, then move to Pro when you need deeper scenario planning and continuous monitoring across teams.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {pricing.map((tier) => (
            <Card
              key={tier.name}
              className={tier.highlighted ? "border-emerald-300 bg-emerald-50/70" : "border-slate-200 bg-white/90"}
            >
              <CardHeader>
                <CardTitle className="text-2xl tracking-tight">{tier.name}</CardTitle>
                <CardDescription className="text-slate-600">{tier.subtitle}</CardDescription>
                <p className="pt-2 text-3xl font-semibold text-slate-900">{tier.price}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {tier.points.map((point) => (
                  <p key={point} className="flex items-start gap-2 text-sm text-slate-700">
                    <CircleCheck className="mt-0.5 h-4 w-4 text-emerald-700" />
                    {point}
                  </p>
                ))}

                <div className="pt-3">
                  <Link href="/app">
                    <Button className="w-full">Open command center</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="contact" className="mx-auto max-w-7xl scroll-mt-24 px-6 pb-16 pt-8">
        <Card className="border-slate-200 bg-white/90">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl tracking-tight">
              <Mail className="h-5 w-5 text-emerald-700" />
              Contact the Keystone team
            </CardTitle>
            <CardDescription className="text-slate-600">
              Tell us your operating context and we will tailor onboarding recommendations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4 md:grid-cols-2" action="#" method="post">
              <div className="space-y-1.5">
                <Label htmlFor="name">Name</Label>
                <Input id="name" name="name" placeholder="Alex Morgan" required />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="email">Work email</Label>
                <Input id="email" name="email" type="email" placeholder="alex@company.com" required />
              </div>
              <div className="space-y-1.5 md:col-span-2">
                <Label htmlFor="company">Company</Label>
                <Input id="company" name="company" placeholder="Acme Operations" />
              </div>
              <div className="space-y-1.5 md:col-span-2">
                <Label htmlFor="message">How can we help?</Label>
                <textarea
                  id="message"
                  name="message"
                  rows={5}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-primary"
                  placeholder="Share your current cash planning process and where guidance is missing."
                  required
                />
              </div>
              <div className="md:col-span-2">
                <Button type="submit" className="w-full">
                  Send message
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </section>

      <footer className="border-t border-border/70 bg-white/80">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-sm text-slate-600 md:flex-row md:items-center md:justify-between">
          <p>© {new Date().getFullYear()} Keystone. Financial intelligence for operators.</p>
          <div className="flex items-center gap-4">
            <Link href="/#features" className="hover:text-slate-900">
              Features
            </Link>
            <Link href="/#pricing" className="hover:text-slate-900">
              Pricing
            </Link>
            <Link href="/#contact" className="hover:text-slate-900">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}

function ValuePill({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Landmark;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-lg border border-white/80 bg-white/75 p-3 backdrop-blur">
      <p className="flex items-center gap-1.5 text-sm font-medium text-slate-800">
        <Icon className="h-4 w-4 text-emerald-700" />
        {title}
      </p>
      <p className="mt-1 text-xs text-slate-600">{text}</p>
    </div>
  );
}
