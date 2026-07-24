# Scenario 05: Restriction Priority

## Plan and expected results

| Buyer | Product | Base delay | Expected ACL response |
|---|---|---:|---|
| `1B` | B | 500 ms | `INFORM` |
| `2B` | B | 1000 ms | `INFORM` |
| `4B` | B | 1500 ms | `FAILURE` (out of stock) |
| `3B` | B | 2000 ms | `REFUSE` |

- Final inventory: `{A=2, B=0}`
- Successful buyers: `[1B, 2B]`
- Processed requests: `4`
- `3B` must receive REFUSE even after B reaches zero, proving restriction-first evaluation.

## Screenshot capture command

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=restriction-priority" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

## Required evidence

| Filename | What must be visible | Status |
|---|---|---|
| `01-rma-agents.png` | RMA showing the seller and all four named buyers. | Manual; not captured |
| `02-sniffer-messages.png` | `4B` receiving FAILURE before `3B` receives REFUSE. | Manual; not captured |
| `03-console-results.png` | Two B successes, `4B` out-of-stock failure, then `3B` refusal. | Manual; not captured |
| `04-seller-final-report.png` | `{A=2, B=0}`, `[1B, 2B]`, and processed count 4. | Manual; not captured |
| `run-output.txt` | Complete automated non-GUI output created by the runner. | Automated |
