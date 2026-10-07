import { useEffect, useState, type FormEvent } from 'react'
import {
  checkHealth,
  getNextTest,
  recordObservation,
  startInvestigation,
  type EpistemicState,
  type Experiment,
  type Investigation,
} from './api'
import './App.css'

const DEMO_QUESTION =
  "My basil keeps wilting even though I'm watering it. Help me figure out why."

const stateLabels: Record<EpistemicState, string> = {
  open: 'Open',
  supported: 'Supported',
  contradicted: 'Contradicted',
  known: 'Known',
}

function WhyLabMark() {
  return (
    <div className="brand-mark" aria-hidden="true">
      <span className="brand-orbit brand-orbit-one" />
      <span className="brand-orbit brand-orbit-two" />
      <span className="brand-core" />
    </div>
  )
}

function App() {
  const [question, setQuestion] = useState(DEMO_QUESTION)
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [observationValue, setObservationValue] = useState('67')
  const [isRecording, setIsRecording] = useState(false)
  const [observationError, setObservationError] = useState<string | null>(null)
  const [nextTest, setNextTest] = useState<Experiment | null>(null)
  const [nextTestError, setNextTestError] = useState<string | null>(null)
  const [isServiceLive, setIsServiceLive] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false

    checkHealth().then((isLive) => {
      if (!cancelled) {
        setIsServiceLive(isLive)
      }
    })

    return () => {
      cancelled = true
    }
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedQuestion = question.trim()

    if (!trimmedQuestion || isStarting) {
      return
    }

    setIsStarting(true)
    setError(null)

    try {
      const created = await startInvestigation(trimmedQuestion)
      setInvestigation(created)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'WhyLab could not start this investigation.',
      )
    } finally {
      setIsStarting(false)
    }
  }

  async function handleRecordObservation(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!investigation || isRecording) {
      return
    }

    const numericValue = Number(observationValue)

    if (
      !Number.isFinite(numericValue) ||
      numericValue < 0 ||
      numericValue > 100
    ) {
      setObservationError(
        'Enter a soil-moisture value between 0 and 100 percent.',
      )
      return
    }

    setIsRecording(true)
    setObservationError(null)

    try {
      const updated = await recordObservation(
        investigation.id,
        'soil_moisture',
        numericValue,
        'percent',
      )

      setInvestigation(updated)

      try {
        const experiment = await getNextTest(updated.id)
        setNextTest(experiment)
        setNextTestError(null)
      } catch (requestError) {
        setNextTest(null)
        setNextTestError(
          requestError instanceof Error
            ? requestError.message
            : 'WhyLab could not recommend the next experiment.',
        )
      }
    } catch (requestError) {
      setObservationError(
        requestError instanceof Error
          ? requestError.message
          : 'WhyLab could not record this observation.',
      )
    } finally {
      setIsRecording(false)
    }
  }

  function resetInvestigation() {
    setInvestigation(null)
    setError(null)
    setObservationError(null)
    setObservationValue('67')
    setNextTest(null)
    setNextTestError(null)
    setQuestion(DEMO_QUESTION)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <WhyLabMark />
          <div>
            <div className="brand-name">WhyLab</div>
            <div className="brand-version">Research companion · v0.1</div>
          </div>
        </div>

        <button
          className="new-investigation"
          type="button"
          onClick={resetInvestigation}
        >
          <span aria-hidden="true">＋</span>
          New investigation
        </button>

        <nav className="sidebar-nav" aria-label="WhyLab navigation">
          <button className="nav-item nav-item-active" type="button">
            <span className="nav-icon" aria-hidden="true">
              ◌
            </span>
            Investigation
          </button>

          <div className="nav-item nav-item-muted">
            <span className="nav-icon" aria-hidden="true">
              ⌁
            </span>
            Evidence trail
          </div>

          <div className="nav-item nav-item-muted">
            <span className="nav-icon" aria-hidden="true">
              ◇
            </span>
            Experiments
          </div>
        </nav>

        <div className="sidebar-spacer" />

        <div className="epistemic-note">
          <span className="note-dot" />
          <div>
            <strong>Falsification first</strong>
            <p>
              WhyLab keeps generated explanations separate from evidence state.
            </p>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">Scientific reasoning workspace</span>
          </div>

          <div className="system-status">
            <span
              className={`status-dot ${
                isServiceLive === true
                  ? 'status-dot-live'
                  : isServiceLive === false
                    ? 'status-dot-offline'
                    : 'status-dot-checking'
              }`}
            />
            {isServiceLive === true
              ? 'Live reasoning service'
              : isServiceLive === false
                ? 'Reasoning service unavailable'
                : 'Checking reasoning service'}
          </div>
        </header>

        {!investigation ? (
          <section className="welcome-panel">
            <div className="ambient ambient-one" />
            <div className="ambient ambient-two" />

            <div className="welcome-content">
              <div className="question-orb" aria-hidden="true">
                <div className="orb-ring orb-ring-one" />
                <div className="orb-ring orb-ring-two" />
                <div className="orb-center">?</div>
              </div>

              <p className="welcome-kicker">Ask a question worth testing</p>

              <h1>
                Don&apos;t just ask <em>why.</em>
                <br />
                Find out.
              </h1>

              <p className="welcome-copy">
                WhyLab turns a real-world question into competing hypotheses,
                falsifiable predictions, observations, and the next useful
                experiment.
              </p>

              <form className="question-form" onSubmit={handleSubmit}>
                <label className="sr-only" htmlFor="question">
                  Investigation question
                </label>

                <textarea
                  id="question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={3}
                  placeholder="What are you trying to understand?"
                  disabled={isStarting}
                />

                <div className="question-actions">
                  <span className="scope-note">
                    v0.1 supports basil-wilting investigations
                  </span>

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={isStarting || !question.trim()}
                  >
                    {isStarting ? (
                      <>
                        <span className="spinner" aria-hidden="true" />
                        Forming hypotheses
                      </>
                    ) : (
                      <>
                        Start investigation
                        <span aria-hidden="true">→</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {error && (
                <div className="error-banner" role="alert">
                  <strong>WhyLab couldn&apos;t start that investigation.</strong>
                  <span>{error}</span>
                </div>
              )}

              <div className="method-strip">
                <div>
                  <span className="method-number">01</span>
                  <strong>Compete</strong>
                  <p>Keep multiple explanations alive.</p>
                </div>

                <div className="method-divider" />

                <div>
                  <span className="method-number">02</span>
                  <strong>Test</strong>
                  <p>Look for evidence that discriminates.</p>
                </div>

                <div className="method-divider" />

                <div>
                  <span className="method-number">03</span>
                  <strong>Revise</strong>
                  <p>Change the conclusion when evidence changes.</p>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="investigation-view">
            <div className="investigation-heading">
              <div>
                <span className="eyebrow">Active investigation</span>
                <h1>{investigation.question}</h1>
              </div>

              <div className="investigation-id">
                <span>Investigation</span>
                <code>{investigation.id.slice(0, 18)}…</code>
              </div>
            </div>

            <div className="investigation-summary">
              <div className="summary-card">
                <span>Domain</span>
                <strong>{investigation.domain}</strong>
              </div>

              <div className="summary-card">
                <span>Hypotheses</span>
                <strong>{investigation.hypotheses.length}</strong>
              </div>

              <div className="summary-card">
                <span>Observations</span>
                <strong>{investigation.observations.length}</strong>
              </div>

              <div className="summary-card">
                <span>Status</span>
                <strong className="capitalize">
                  {investigation.status}
                </strong>
              </div>
            </div>

            <div className="section-heading">
              <div>
                <span className="eyebrow">Competing explanations</span>
                <h2>What could explain this?</h2>
              </div>

              <p>
                Every hypothesis starts open. Evidence — not fluency — changes
                its state.
              </p>
            </div>

            <div className="hypothesis-grid">
              {investigation.hypotheses.map((hypothesis) => (
                <article className="hypothesis-card" key={hypothesis.id}>
                  <div className="hypothesis-meta">
                    <span className="hypothesis-id">{hypothesis.id}</span>
                    <span
                      className={`state-pill state-${hypothesis.state}`}
                    >
                      {stateLabels[hypothesis.state]}
                    </span>
                  </div>

                  <h3>{hypothesis.claim}</h3>

                  <div className="hypothesis-section">
                    <span className="card-label">Prediction</span>
                    <p>
                      {hypothesis.predictions[0] ??
                        'No prediction recorded yet.'}
                    </p>
                  </div>

                  <div className="hypothesis-section falsifier">
                    <span className="card-label">What could count against it</span>
                    <p>
                      {hypothesis.falsifiers[0] ??
                        'No falsifier recorded yet.'}
                    </p>
                  </div>
                </article>
              ))}
            </div>

            <div className="next-stage">
              <div>
                <span className="eyebrow">Evidence update</span>
                <h2>
                  {investigation.observations.length > 0
                    ? 'Evidence changed the picture.'
                    : 'Bring in an observation.'}
                </h2>
                <p>
                  {investigation.observations.length > 0
                    ? 'WhyLab has applied the observation to the competing hypotheses. The cards above now reflect the current evidence state.'
                    : 'Report what you observe in the real world. WhyLab will apply deterministic evidence rules and revise only the hypotheses affected by that evidence.'}
                </p>
              </div>

              <form
                className="observation-panel"
                onSubmit={handleRecordObservation}
              >
                <div className="observation-heading">
                  <div>
                    <span className="card-label">Observation</span>
                    <strong>Soil moisture</strong>
                  </div>

                  <span className="observation-variable">
                    soil_moisture
                  </span>
                </div>

                <div className="observation-control">
                  <input
                    aria-label="Soil moisture percentage"
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={observationValue}
                    onChange={(event) =>
                      setObservationValue(event.target.value)
                    }
                    disabled={isRecording}
                  />
                  <span className="observation-unit">%</span>

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={isRecording || !observationValue}
                  >
                    {isRecording ? (
                      <>
                        <span className="spinner" aria-hidden="true" />
                        Updating evidence
                      </>
                    ) : (
                      <>
                        Record observation
                        <span aria-hidden="true">→</span>
                      </>
                    )}
                  </button>
                </div>

                {observationError && (
                  <div className="observation-error" role="alert">
                    {observationError}
                  </div>
                )}

                {investigation.observations.length > 0 && (
                  <div className="observation-confirmation">
                    <span className="status-dot" />
                    {investigation.observations.length} observation
                    {investigation.observations.length === 1 ? '' : 's'} stored
                    in this investigation
                  </div>
                )}
              </form>
            </div>

            {nextTest && (
              <section className="experiment-panel">
                <div className="experiment-intro">
                  <span className="eyebrow">
                    Next discriminating experiment
                  </span>

                  <h2>{nextTest.question}</h2>

                  <p>
                    This test is chosen from the current evidence state to
                    distinguish the explanations that remain plausible.
                  </p>
                </div>

                <div className="experiment-grid">
                  <div className="experiment-detail">
                    <span className="card-label">Change</span>
                    <strong>{nextTest.variable_changed}</strong>
                  </div>

                  <div className="experiment-detail">
                    <span className="card-label">Compare</span>
                    <strong>
                      {nextTest.target_hypotheses.join(' vs ')}
                    </strong>
                  </div>

                  <div className="experiment-detail">
                    <span className="card-label">Duration</span>
                    <strong>
                      {nextTest.duration_days}{' '}
                      {nextTest.duration_days === 1 ? 'day' : 'days'}
                    </strong>
                  </div>
                </div>

                <div className="experiment-body">
                  <div>
                    <span className="card-label">Hold constant</span>
                    <ul>
                      {nextTest.variables_held_constant.map((variable) => (
                        <li key={variable}>{variable}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <span className="card-label">Observe</span>
                    <ul>
                      {nextTest.observations_required.map((observation) => (
                        <li key={observation}>{observation}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="prediction-comparison">
                  {Object.entries(nextTest.predicted_results).map(
                    ([hypothesisId, prediction]) => (
                      <div
                        className="prediction-row"
                        key={hypothesisId}
                      >
                        <span>{hypothesisId}</span>
                        <p>{prediction}</p>
                      </div>
                    ),
                  )}
                </div>
              </section>
            )}

            {nextTestError && (
              <div className="next-test-error" role="alert">
                <strong>Evidence was updated successfully.</strong>
                <span>
                  The next experiment could not be loaded: {nextTestError}
                </span>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  )
}

export default App
