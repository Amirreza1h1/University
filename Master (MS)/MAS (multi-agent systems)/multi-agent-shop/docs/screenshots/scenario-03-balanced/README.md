# Scenario 03: Balanced

## Plan and expected results

| Buyer | Product | Base delay | Expected ACL response |
|---|---|---:|---|
| `1B` | A | 500 ms | `INFORM` |
| `2B` | B | 1000 ms | `INFORM` |
| `3B` | A | 1500 ms | `INFORM` |
| `4B` | B | 2000 ms | `INFORM` |

- Final inventory: `{A=0, B=0}`
- Successful buyers: `[1B, 2B, 3B, 4B]`
- Processed requests: `4`

## Screenshot capture command

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=balanced" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

## Required evidence

| Filename | What must be visible | Status |
|---|---|---|
| `01-rma-agents.png` | RMA showing the seller and all four named buyers. | Manual; not captured |
| `02-sniffer-messages.png` | Four requests and four correlated INFORM replies. | Manual; not captured |
| `03-console-results.png` | Every buyer successful with its requested product in its list. | Manual; not captured |
| `04-seller-final-report.png` | `{A=0, B=0}`, all four successful buyers, and processed count 4. | Manual; not captured |
| `run-output.txt` | Complete automated non-GUI output created by the runner. | Automated |
