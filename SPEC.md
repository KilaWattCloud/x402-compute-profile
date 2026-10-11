# x402 Compute Provisioning Profile, v0.1 (draft)

Key words MUST, SHOULD and MAY are used as in RFC 2119. Evidence labels: (live) means seen working against the reference implementation in live tests in October 2026. (unverified) means taken from the reference client code or earlier notes and not confirmed in live tests. (proposed) means a recommendation that the reference implementation may not yet follow.

## 1. Scope
One buyer agent, one seller endpoint, one payment per provisioning request, settled in USDC on Base (network `eip155:8453`) using the x402 `exact` scheme. Other networks and schemes are out of scope for v0.1.

## 2. Flow
1. Quote. The client sends the request body (section 3) without payment. The seller replies HTTP 402 with x402 payment requirements: price, network, asset, pay-to address and a validity window. The client pays nothing at this step. (live)
2. Decide. The client checks the price against its own limits. A client MUST NOT pay without an explicit limit set by its operator, such as a per-job and a per-session maximum. (proposed)
3. Pay. The client signs the payment and repeats the same request with the payment header and an `Idempotency-Key` header. (unverified)
4. Receive. The seller settles the payment, places the job, and replies with a job id and a status. The first successful response MAY include a credential (an API key) for reading job status. (live)
5. Track. The client reads job status with the job id and the credential. (live)

## 3. Request body
JSON, `Content-Type: application/json`. A seller MUST reject other media types with HTTP 415 and charge nothing. (unverified)

Fields: `gpu_type` (string, from a list the seller publishes), `card_count` (integer, at least 1, upper limit depends on gpu_type), `duration_seconds` (number, 60 to 86400 in the reference implementation), optional `routing_policy`, optional `workload_type`. Unknown fields SHOULD be rejected. See schemas/request.schema.json.

A seller SHOULD publish its supported `gpu_type` values and limits in machine-readable discovery (the reference implementation uses `/.well-known/x402`). (unverified)

## 4. Price and quote validity
The price in the 402 response applies to exactly the request body that produced it. If the price changes before payment, the seller MUST reply with error `price_changed` and charge nothing, and the client MUST request a new quote. (unverified)

## 5. Idempotency
The paid request carries an `Idempotency-Key`. If a client does not receive a response to a paid request, it MAY retry once with the same key. A seller MUST NOT charge twice for the same signed payment: it replies HTTP 409 with `payment_already_used`, and SHOULD include the original transaction hash and job id. (unverified)
A client that cannot confirm the outcome after one retry MUST check job status before sending any new payment. (proposed)

## 6. Status lifecycle
A job is in exactly one of: placed, ready, failed, ended. (proposed names)
- placed: payment settled, capacity requested, not yet usable.
- ready: capacity is usable. The seller SHOULD report `ready_at`.
- failed: capacity never became ready. The seller SHOULD refund (section 7).
- ended: the job ran and stopped. The seller SHOULD report `ended_at` and `runtime_seconds`.
Status responses include `status`, `ready` (boolean) and, when known, `ready_at`, `ended_at`, `runtime_seconds`. (live)

## 7. Refunds
If a job never becomes ready, the seller MUST refund the buyer in full and MUST say how: on-chain, or as seller-held credit. (proposed)
Known gap: the reference implementation refunds never-ready jobs automatically as seller credit, not on-chain. A buyer that wants on-chain refunds cannot get them today.
If no capacity matches before payment, the seller MUST reply HTTP 503 with `no_capacity` and take no payment. (unverified)

## 8. Errors
Error bodies are JSON with a string `error` code and SHOULD include a human-readable `message`. See schemas/error.schema.json.

Evidence note: the error codes and HTTP statuses in this table come from the reference client's error mapping and have not been verified in live tests, except 429 rate_limited, which was seen in live testing. Sanctions screening (403) has not been tested.

| HTTP | error code | Meaning | Charged? |
|------|------------|---------|----------|
| 400 | invalid_json, unknown_gpu_type, size_not_available, wrong_payment_header | bad request or unsupported size | no |
| 402 | insufficient_funds_or_invalid_signature, price_changed | payment required or declined | no |
| 403 | sanctions_screening, sanctions_screening_failed | payment rejected by screening | no |
| 409 | payment_already_used | duplicate payment | not again |
| 415 | unsupported_media_type | body is not JSON | no |
| 429 | rate_limited | too many requests | no |
| 503 | no_capacity | nothing matches | no |

## 9. Client safety requirements (proposed)
A client acting for an agent SHOULD: refuse to pay without explicit operator confirmation and a maximum price; enforce a per-job and a per-session spend cap; never print private keys or credentials in logs or tool output; validate inputs locally before any network call; and never retry a signed payment except as in section 5.

## 10. Privacy
Seller internals (supplier identity, internal cost) SHOULD NOT appear in buyer-facing responses. (proposed)

## 11. Known gaps in v0.1
- Status strings in the reference implementation are not yet listed exactly; section 6 names are proposed.
- Refunds are credit only (section 7).
- Only Base USDC is covered. Lightning or other rails are out of scope.
- Authentication for status reads is described loosely ("credential") and needs a precise definition.
- No conformance tests exist yet.
- Most error paths, replay protection, price-change handling and the no-capacity refund have not been verified in live tests; see the (unverified) labels.
- Sanctions screening has not been tested.
