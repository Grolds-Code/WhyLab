# WhyLab Friction Log

This log documents concrete friction encountered while building WhyLab for the Alexa+ track of the Amazon Developer Hackathon 2026.

## 1. Understanding which Alexa+ developer path was available

**Task attempted:**  
Set up an Alexa+ development environment for an MCP-backed persistent reasoning agent.

**Steps taken:**  
I reviewed the Alexa+ track requirements and developer resources and investigated the Category SDK, MCP Toolkit, CLI, and Web Simulator before implementing the integration.

**Expected result:**  
A clear hackathon-specific path showing which Alexa+ tools participants could access and how to test an MCP-backed experience end to end.

**Actual result:**  
The native Alexa+ developer tools were gated to selected partners. This was not immediately obvious from every setup path, so identifying the supported hackathon route required additional investigation.

**Severity:** Important

**Workaround:**  
I implemented the supported self-hosted MCP approach over Streamable HTTP and built a web-based Alexa+ concept experience backed by the same live investigation state.

**Suggestion:**  
Provide one Alexa+ hackathon quick-start page that clearly distinguishes:

1. tools available to all participants,
2. gated preview tools,
3. the recommended self-hosted MCP workflow,
4. a minimal reference implementation.

This would reduce setup uncertainty and let participants reach their first working integration faster.

---

## 2. Verifying MCP protocol compliance

**Task attempted:**  
Verify that the deployed WhyLab MCP server satisfied the Alexa+ requirement for MCP protocol version 2025-11-25 or later over Streamable HTTP.

**Steps taken:**  
I checked the installed MCP SDK version, inspected protocol references in the package, and connected an MCP client to the deployed server to inspect the negotiated protocol version.

**Expected result:**  
A straightforward documented command or diagnostic showing the protocol version negotiated by a deployed MCP server.

**Actual result:**  
The Python package version alone did not establish protocol compliance. I needed to inspect the SDK and then run a live client check against production.

**Severity:** Moderate

**Workaround:**  
I connected directly to the production MCP endpoint and read the negotiated protocol version, confirming that WhyLab uses MCP protocol `2026-07-28`.

**Suggestion:**  
Include an official verification snippet in the Alexa+ MCP documentation that prints:

- transport type,
- negotiated MCP protocol version,
- exposed tool names.

This would make pre-submission compliance checks much easier.

---

## 3. Diagnosing tool failures through Streamable HTTP

**Task attempted:**  
Debug a production `start_investigation` MCP tool failure.

**Steps taken:**  
I reproduced the failure with a live MCP smoke test, inspected production logs, traced the exception through the MCP tool manager, and isolated the underlying structured-generation validation failure.

**Expected result:**  
The client-facing error or server logs would surface the underlying application exception clearly.

**Actual result:**  
The initial client error was generic, while the useful root cause appeared deeper inside nested asynchronous task-group and transport traces. The MCP connection itself was healthy, but distinguishing a transport problem from an application-level tool failure required additional log inspection.

**Severity:** Moderate

**Workaround:**  
I inspected server-side logs, reproduced the failure locally, added a regression test, hardened the structured-output validator, and generalized the live MCP smoke test. The deployed workflow subsequently passed end to end.

**Suggestion:**  
Provide clearer separation between:

- MCP transport/session errors,
- tool invocation errors,
- application exceptions.

A concise root-cause field or structured diagnostic attached to development-mode tool errors would significantly shorten debugging time.

---

## Outcome

These frictions did not prevent completion of WhyLab, but resolving them materially shaped the final engineering workflow.

The resulting production system now has:

- a live self-hosted Streamable HTTP MCP server,
- negotiated MCP protocol `2026-07-28`,
- four exposed reasoning tools,
- persistent investigation state,
- automated regression coverage,
- and a live MCP smoke test covering the complete investigation workflow.
