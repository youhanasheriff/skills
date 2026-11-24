<!-- page id="start-welcome" group="Overview" title="Welcome" -->
# Acme documentation

Acme is a sample product used to show the page format. Replace these files with your own.

<div class="cards">
<a href="#guide-first-steps"><b>Product guides</b><span>Every feature, step by step.</span></a>
<a href="#api-orders"><b>API reference</b><span>Every endpoint.</span></a>
</div>

## How it fits together

```mermaid
flowchart TB
  web["Web app<br>React"]:::own --> api["API server"]:::own
  api --> db[("Postgres")]:::data
  api --> pay["Payment provider"]:::ext
```

> **Note** These docs describe the code on `main`. **Planned** marks decided work; **Known gap** marks code that differs.

<!-- page id="guide-first-steps" group="Getting started" title="First steps" -->
# First steps

Sign up and place a first order.

1. Open **Sign up** and enter your email.
2. Choose **New order**.

> **Planned** Saved carts, decided on 1 Jan 2027.

```mermaid
sequenceDiagram
  participant U as User
  participant W as Web app
  participant A as API
  U->>W: New order
  W->>A: POST /orders
  A-->>W: 201 Created
```

<!-- page id="api-orders" group="Orders" title="Orders" -->
# Orders

Create and read orders. See [First steps](#guide-first-steps).

### POST /orders

Creates an order. Auth: session cookie.

| Field | Type | Required | Notes |
|---|---|---|---|
| `items` | array | yes | At most 50 |

**Response** `201` with the order.

> **Known gap** No rate limit on this route (`src/orders.rs`).
