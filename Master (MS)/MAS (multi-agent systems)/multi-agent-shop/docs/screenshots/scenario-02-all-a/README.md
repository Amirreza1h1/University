# Scenario 02: All A

## Plan and expected results

| Buyer | Product | Base delay | Expected ACL response |
|---|---|---:|---|
| `1B` | A | 500 ms | `INFORM` |
| `2B` | A | 1000 ms | `INFORM` |
| `3B` | A | 1500 ms | `FAILURE` (out of stock) |
| `4B` | A | 2000 ms | `FAILURE` (out of stock) |

- Final inventory: `{A=0, B=2}`
- Successful buyers: `[1B, 2B]`
- Processed requests: `4`

## Screenshot capture command

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=all-a" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

## Required evidence

| Filename | What must be visible | Status |
|---|---|---|
| `01-rma-agents.png` | RMA showing the seller and all four named buyers. | Manual; not captured |
| `02-sniffer-messages.png` | Four A requests, two INFORM replies, and two out-of-stock FAILURE replies. | Manual; not captured |
| `03-console-results.png` | `1B`/`2B` successful with `[A]`; `3B`/`4B` failed with `[]`. | Manual; not captured |
| `04-seller-final-report.png` | `{A=0, B=2}`, `[1B, 2B]`, and processed count 4. | Manual; not captured |
| `run-output.txt` | Complete automated non-GUI output created by the runner. | Automated |
