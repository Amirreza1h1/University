# Scenario 04: Refusal Stock

## Plan and expected results

| Buyer | Product | Base delay | Expected ACL response |
|---|---|---:|---|
| `1B` | A | 500 ms | `INFORM` |
| `2B` | A | 1000 ms | `INFORM` |
| `3B` | B | 1500 ms | `REFUSE` |
| `4B` | B | 2000 ms | `INFORM` |

- Final inventory: `{A=0, B=1}`
- Successful buyers: `[1B, 2B, 4B]`
- Processed requests: `4`
- The remaining B unit proves that refusing `3B` did not decrement inventory.

## Screenshot capture command

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=refusal-stock" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

## Required evidence

| Filename | What must be visible | Status |
|---|---|---|
| `01-rma-agents.png` | RMA showing the seller and all four named buyers. | Manual; not captured |
| `02-sniffer-messages.png` | A REFUSE reply to `3B` followed by an INFORM reply to `4B` for B. | Manual; not captured |
| `03-console-results.png` | A successes for `1B`/`2B`, refusal for `3B`, and B success for `4B`. | Manual; not captured |
| `04-seller-final-report.png` | `{A=0, B=1}`, `[1B, 2B, 4B]`, and processed count 4. | Manual; not captured |
| `run-output.txt` | Complete automated non-GUI output created by the runner. | Automated |
