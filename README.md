# x402 Compute Provisioning Profile

Status: draft v0.1. Not a standard. Not endorsed by the x402 Foundation, Block, or the goose project.

An open profile describing how an AI agent can request, pay for, track and get a refund for provisioned compute (for example a GPU job) using x402 payments, with no account sign-up.

It builds on the x402 protocol. It does not change x402. It only describes the compute-specific parts: the request body, the status lifecycle, refund semantics, idempotency and error codes.

## Contents
- [SPEC.md](SPEC.md): the profile text
- [schemas/](schemas): JSON Schemas for the request, the status response and the error body
- [examples/](examples): sample requests and responses

## Reference implementation
Kilawatt Cloud (https://www.kilawattcloud.dev) implements this profile at `POST /api/public/x402/exec`, with a goose and MCP client at https://github.com/KilaWattCloud/kilawatt-mcp-server (MIT). The profile is written from that implementation's client code and live test runs. SPEC.md labels each item as live, unverified or proposed. Where the implementation differs from a sensible profile, SPEC.md says so under "Known gaps".

## What this is not
This repository does not prove adoption. As of the first draft there are no known outside implementers. Feedback, corrections and competing implementations are welcome through issues.

## License
MIT. See LICENSE.

## Checks
CI validates the examples against the schemas.
