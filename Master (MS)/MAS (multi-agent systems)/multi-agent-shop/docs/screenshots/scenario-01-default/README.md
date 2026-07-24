# Scenario 01: Default

## Plan and expected results

| Buyer | Product | Base delay | Expected ACL response |
|---|---|---:|---|
| `1B` | B | 500 ms | `INFORM` |
| `2B` | B | 1000 ms | `INFORM` |
| `3B` | B | 1500 ms | `REFUSE` |
| `4B` | B | 2000 ms | `FAILURE` (out of stock) |

- Final inventory: `{A=2, B=0}`
- Successful buyers: `[1B, 2B]`
- Processed requests: `4`

## Screenshot capture command

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=default" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

## Required evidence

| Filename | What must be visible | Status |
|---|---|---|
| `01-rma-agents.png` | RMA showing `seller`, `1B`, `2B`, `3B`, and `4B`. | Manual; not captured |
| `02-sniffer-messages.png` | Four REQUEST messages and the two INFORM, one REFUSE, and one FAILURE replies. | Manual; not captured |
| `03-console-results.png` | All buyer results and purchase lists: `[B]`, `[B]`, `[]`, `[]`. | Manual; not captured |
| `04-seller-final-report.png` | Final inventory, successful buyers, and processed count above. | Manual; not captured |
| `run-output.txt` | Complete automated non-GUI output created by `scripts/run-scenarios.ps1`. | Automated |
