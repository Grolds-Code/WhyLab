# WhyLab — Competition Strategy

## Goal

Build the strongest possible Alexa+ submission by optimizing for:

- originality;
- technical implementation;
- product design;
- credible customer impact;
- judge memorability.

WhyLab should not try to be the biggest project.

It should be the most coherent, defensible, polished, and memorable project we can execute exceptionally well.

---

## Core Thesis

> Alexa should not just answer "why?" — it should help you find out.

WhyLab is a persistent scientific-reasoning agent that:

1. forms competing hypotheses;
2. identifies what evidence would distinguish them;
3. designs simple tests;
4. tracks observations across sessions;
5. searches for evidence that could falsify its current belief;
6. updates its conclusion when the evidence changes.

The product is not a chatbot.

The product is the investigation loop.

---

## Winning Principle 1 — One Killer Experience

The submission must center on one unforgettable end-to-end scenario.

Primary demo scenario:

> "My basil keeps wilting even though I'm watering it. Help me figure out why."

The complete experience must work:

question  
→ hypotheses  
→ confounder detection  
→ test design  
→ saved investigation  
→ later observation  
→ evidence update  
→ falsification check  
→ conclusion  
→ next test.

If this flow is not excellent, we do not add more features.

---

## Winning Principle 2 — Everything Shown Must Be Real

Never fake:

- tool calls;
- persistent memory;
- reasoning results;
- evaluation metrics;
- dashboards;
- benchmark results;
- model capabilities.

Every visible feature in the demo must actually work.

If something is incomplete, remove it from the demo.

---

## Winning Principle 3 — Depth Over Feature Count

Do not build unnecessary features simply to make the project look larger.

A feature is accepted only if it improves at least one of:

- the core investigation loop;
- Alexa-native usability;
- technical credibility;
- judge understanding;
- benchmark evidence;
- demo quality.

Otherwise it is out of scope.

---

## Winning Principle 4 — Falsification Is the Differentiator

WhyLab must not only ask:

> "What evidence supports this hypothesis?"

It must also ask:

> "What evidence would make this hypothesis less plausible?"

Each serious hypothesis should contain:

- predictions;
- evidence for;
- evidence against;
- possible confounders;
- falsification conditions;
- unresolved uncertainty.

This falsification-first behavior is a core product differentiator.

---

## Winning Principle 5 — Prove Competence

Do not merely claim that WhyLab reasons better.

Build WhyLab-Bench.

Use scenarios with known ground truth to evaluate:

- confounder detection;
- intervention/test validity;
- falsifier identification;
- evidence updating;
- unsupported causal claims;
- tool-selection correctness;
- multi-session consistency.

Compare:

1. LLM-only baseline;
2. WhyLab structured workflow.

Report results honestly.

---

## Winning Principle 6 — Alexa Must Be Necessary

The judge should understand why this belongs on Alexa+.

WhyLab should exploit:

- hands-free interaction;
- observations captured while the user is doing something else;
- persistent investigations across time;
- natural follow-up conversations;
- glanceable visual summaries.

If the experience would be equally good as a generic chatbot page, redesign it.

---

## Winning Principle 7 — Demo First

The three-minute judging video is part of the product.

Before adding a feature, ask:

> "Will this make the final three-minute demonstration stronger?"

The planned demo should be designed before the full implementation is complete.

The first seconds should show the product solving a real problem, not slides or architecture diagrams.

---

## Winning Principle 8 — Polish Ruthlessly

Before submission:

- remove broken controls;
- remove unfinished features;
- eliminate confusing text;
- improve loading/error states;
- verify every interaction;
- make screenshots intentional;
- make README reproducible;
- make setup instructions accurate;
- make the video concise and visually clean.

A smaller polished product beats a larger rough product.

---

## Scope Guardrail

For v0.1, do not build:

- multiple unrelated domains;
- medical diagnosis;
- autonomous laboratory systems;
- Fire TV support;
- mobile apps;
- social features;
- complex authentication;
- unnecessary cloud infrastructure;
- decorative AI features.

First make one investigation exceptionally good.

---

## Definition of Competition Readiness

WhyLab is ready for submission only when:

1. the killer demo works end-to-end;
2. every visible feature is functional;
3. the project is reproducible from GitHub;
4. benchmark results are real;
5. the UI is polished;
6. the Alexa+ use case is obvious;
7. the novelty can be explained in one sentence;
8. the three-minute video tells a complete story;
9. no unnecessary feature distracts from the core idea.

---

## Final Filter

Before implementing anything, ask:

> Does this help WhyLab investigate rather than merely answer?

And:

> Does this improve our chance of impressing a judge within three minutes?

If the answer to both is no, do not build it.
