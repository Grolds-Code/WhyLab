# WhyLab — Judge Demo Script

## Core message

> Alexa should not just answer "why?" — it should help you find out.

WhyLab is a persistent scientific-reasoning agent for investigable causal questions.

It does not simply generate an explanation. It creates competing hypotheses, defines what evidence would distinguish them, records real observations, deterministically updates epistemic state, and recommends the next useful experiment.

## Demo rule

Everything shown in the demo must come from the real deployed WhyLab system.

No simulated reasoning results, fake tool calls, fabricated Alexa integration, or invented benchmark claims.

## Opening — 0:00 to 0:40

Start on the live WhyLab app, not on slides.

Say:

> "Most assistants try to answer 'why?' immediately. WhyLab takes a different approach: if the cause is uncertain, it helps you investigate."

Use a real, pre-created and persisted basil investigation as the memorable narrative entry point:

> "Suppose my basil keeps wilting even though I'm watering it."

Start with that live investigation already loaded so the demo does not spend valuable time waiting for model generation.

Point out that WhyLab did not return one confident explanation. It created competing hypotheses and kept them open until evidence arrived.

The investigation must be genuinely created by the deployed WhyLab system beforehand — never hard-coded or simulated for the video.

Then say:

> "The key idea is that the language model can propose hypotheses, but it does not decide what is supported. Evidence-state changes are handled by WhyLab's deterministic reasoning engine."

## Evidence Update — 0:40 to 1:25

Record a real observation in the basil investigation:

> "The soil moisture is 67 percent."

Show the evidence trail updating.

Explain:

> "WhyLab does not ask the model whether this observation sounds convincing. It evaluates the observation against explicit evidence rules."

Show the resulting hypothesis-state changes.

Emphasize that some hypotheses can become `SUPPORTED` or `CONTRADICTED`, while unresolved hypotheses remain `OPEN`.

Say:

> "This makes the reasoning auditable. The generated assumptions are separate from the evidence state, and WhyLab never automatically marks a hypothesis as KNOWN."

Briefly show the evidence trail so the judge can see what changed and why.

## Next Test — 1:25 to 1:55

Open the recommended next experiment.

Say:

> "WhyLab is not trying to find a measurement that explains everything. It prefers measurements that can actually support or contradict a specific hypothesis."

Show the recommended observation and the hypothesis it targets.

Explain:

> "This matters because a useful investigation should reduce uncertainty, not just collect more symptoms."

If the basil case produces a clear discriminating test, use that live result.

Do not narrate any recommendation that is not actually shown by the deployed system.

## Alexa+ Concept Experience — 1:55 to 2:25

Return to the investigation view and show the Alexa+ concept experience panel.

Say:

> "WhyLab is designed for investigations that unfold over time while someone is doing something in the real world."

Point to the live conversational summary and the next recommended experiment.

Explain:

> "This panel is grounded in the same persistent investigation state, evidence engine, and planner you just saw. It is a concept experience for the Alexa+ track — not a claim that WhyLab is already running inside an unreleased Alexa+ runtime."

Then say:

> "That separation matters to me: the conversational layer can be natural and hands-free, while the scientific state underneath remains explicit, persistent, and testable."

## Cross-Domain Proof — 2:25 to 2:45

Briefly show one unseen production investigation from a different domain, such as the laptop-battery or website-performance case.

Say:

> "Basil is only the narrative demo. The same engine also handles unseen causal questions in other domains."

Point out that the live system generated a different set of competing hypotheses and a measurable next test.

Keep this section short. Its purpose is only to prove generality, not to start a second full demo.

## Closing — 2:45 to 3:00

Return to the main investigation view.

Say:

> "WhyLab turns 'why?' from a request for an instant explanation into a persistent investigation."

Then close with:

> "Alexa should not just answer 'why?' — it should help you find out."

End on the live product screen.

Do not finish on code, architecture, or a slide.
