# Test Scenarios

The Phase 1 JUnit suite tests `PurchaseService` without starting JADE. Runtime scenarios additionally verify the ACL mapping performed by the seller behaviour.

| Scenario ID | Buyer | Requested product | Initial inventory | Expected ACL response | Expected inventory after processing | Buyer recorded? | Expected buyer purchase list |
|---|---|---|---|---|---|---|---|
| TS-01 | `1B` | A | `{A=2, B=2}` | `INFORM` | `{A=1, B=2}` | Yes | `[A]` |
| TS-02 | `1B` | B | `{A=2, B=2}` | `INFORM` | `{A=2, B=1}` | Yes | `[B]` |
| TS-03 | `3B` | B | `{A=2, B=2}` | `REFUSE` | `{A=2, B=2}` | No | `[]` |
| TS-04 | `4B` | B | `{A=2, B=0}` | `FAILURE` | `{A=2, B=0}` | No | `[]` |
| TS-05 | Any valid sender | Invalid content such as `C` | `{A=2, B=2}` | `FAILURE` | `{A=2, B=2}` | No | `[]` |
| TS-06 | `5B` | B after two successful B sales | `{A=2, B=0}` | `FAILURE` | `{A=2, B=0}` | No | `[]` |
| TS-07 | `1B`, then `2B` | A, then B | `{A=2, B=2}` | Two `INFORM` replies | `{A=1, B=1}` | Both | `1B: [A]`, `2B: [B]` |
| TS-08 | `3B` | B when B is already 0 | `{A=2, B=0}` | `REFUSE` because restriction is checked first | `{A=2, B=0}` | No | `[]` |

## Default deterministic runtime scenario

| Order | Buyer | Delay | Request | Expected result | Inventory afterward |
|---|---|---:|---|---|---|
| 1 | `1B` | 500 ms | B | `INFORM`; purchase succeeds | `{A=2, B=1}` |
| 2 | `2B` | 1000 ms | B | `INFORM`; purchase succeeds | `{A=2, B=0}` |
| 3 | `3B` | 1500 ms | B | `REFUSE`; restricted buyer | `{A=2, B=0}` |
| 4 | `4B` | 2000 ms | B | `FAILURE`; out of stock | `{A=2, B=0}` |

Expected final report:

```text
[seller] Final inventory: {A=2, B=0}
[seller] Successful buyers: [1B, 2B]
[seller] Processed requests: 4
```

## Automated test coverage

The 20-test JUnit suite contains 13 purchase-service tests and 7 JADE-independent scenario-configuration tests. It covers initial inventory, successful A and B purchases, product-specific decrement, the `3B` restriction, refusal immutability, out-of-stock behavior, successful-buyer tracking, non-negative inventory, immutable returned collections, invalid method inputs, scenario fallback, buyer uniqueness, deterministic delays, restriction-priority ordering, and valid products.

Invalid ACL content is handled at the JADE adapter boundary in `SellerRequestBehaviour`: it produces `FAILURE`, sends a reply, and increments the processed count, preventing a malformed request from crashing or stalling the seller.
