# WhyLab — 3-Minute Demo Video Storyboard

## Goal

Show a real WhyLab investigation from uncertainty to evidence update to the next falsifying test, while making the Alexa+ use case obvious.

The video must use the deployed production system. No simulated tool calls, fake reasoning results, or fabricated Alexa+ runtime integration.

## 0:00–0:40 — The problem

**Screen:** Live WhyLab app with a real, pre-created basil investigation already loaded.

**Narration focus:** Most assistants answer “why?” immediately. WhyLab helps the user investigate when the cause is uncertain.

**Show:**
- the real user question;
- competing hypotheses;
- all hypotheses initially unresolved;
- the Alexa+ concept experience grounded in live investigation state.

**Key line:**

> “We don’t know yet. Here is how we can find out.”

## 0:40–1:25 — Evidence changes the investigation

**Screen:** Record a real observation in the basil investigation.

Use:

> “The soil moisture is 67 percent.”

Then switch to the evidence trail.

**Show:**
- the observation being saved;
- which hypotheses changed state;
- which remain `OPEN`;
- the evidence trail explaining why.

**Narration focus:** WhyLab does not ask the language model whether the evidence “sounds convincing.” It evaluates the observation against explicit evidence rules.

**Key line:**

> “The model proposes the hypotheses. The evidence engine decides what the observation actually changes.”

## 1:25–1:55 — Ask the next useful question

**Screen:** Open the next recommended experiment.

**Show:**
- the measurement WhyLab recommends;
- the hypothesis or hypotheses it targets;
- the observation required.

**Narration focus:** WhyLab prefers measurements that can actually support or contradict a remaining explanation instead of collecting broad shared symptoms.

**Key line:**

> “A useful investigation should reduce uncertainty, not just collect more data.”

Use only the recommendation actually returned by the deployed system.

## 1:55–2:25 — Why this belongs on Alexa+

**Screen:** Return to the investigation view and focus on the Alexa+ concept experience panel.

**Show:**
- the user’s real causal question;
- WhyLab’s live hypothesis-state briefing;
- the current next-test recommendation;
- the disclosure that the panel is grounded in live investigation state.

**Narration focus:** WhyLab is designed for investigations that unfold over time while the user is interacting with the real world.

**Key line:**

> “The conversational layer can feel natural and hands-free, while the scientific state underneath remains explicit, persistent, and testable.”

Be precise: this is an Alexa+ concept experience backed by a real self-hosted MCP reasoning service, not a claim that WhyLab is already running inside unreleased Alexa+ runtime capabilities.

## 2:25–2:45 — Prove it is not a basil demo

**Screen:** Briefly switch to one real unseen production investigation, preferably the laptop-battery or website-performance case.

**Show:**
- a different domain;
- a different set of hypotheses;
- a real measurable next-test recommendation.

**Narration focus:** Basil is the narrative demo, not special-case logic.

**Key line:**

> “The same investigation engine works on unseen causal questions across different domains.”

Keep this section brief. Do not start a second full investigation during the video.

## 2:45–3:00 — Close on the product idea

**Screen:** Return to the main live investigation view.

**Narration focus:** End on the product proposition, not on architecture or code.

**Key lines:**

> “WhyLab turns ‘why?’ from a request for an instant explanation into a persistent investigation.”

> “Alexa should not just answer ‘why?’ — it should help you find out.”

Hold on the live product for the final seconds.
