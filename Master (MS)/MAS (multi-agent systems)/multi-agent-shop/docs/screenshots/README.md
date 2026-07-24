# Scenario Screenshot Guide

No GUI screenshots have been captured automatically. This structure separates common project evidence from evidence for each deterministic execution scenario:

```text
docs/screenshots/
|-- common/
|-- scenario-01-default/
|-- scenario-02-all-a/
|-- scenario-03-balanced/
|-- scenario-04-refusal-stock/
`-- scenario-05-restriction-priority/
```

The `common` directory documents three project-wide screenshots. Each scenario directory contains its exact plan, expected results, 15-second capture command, screenshot checklist, and an automated `run-output.txt` produced by the scenario runner.

## Automated console evidence

From the project root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-scenarios.ps1
```

The script builds once, runs all scenarios with `mas.gui=false`, validates expected markers, waits for each process and port `7778`, and writes complete console logs to the matching scenario directories. It never kills Java processes.

## Manual GUI capture workflow

1. Run `mvn clean package` and confirm port `7778` is free.
2. Open the chosen scenario directory and copy its exact capture command.
3. The command adds a 15-second initial delay to every buyer, allowing time to prepare RMA and Sniffer.
4. In RMA, use the **Tools** menu to start/open the Sniffer and select `seller`, `1B`, `2B`, `3B`, and `4B`.
5. Capture the four specified PNG files while their required evidence is visible.
6. Close the JADE GUI normally before starting another scenario.
7. Mark a screenshot as captured in that scenario's README only after verifying it is readable and nonblank.

Do not generate blank or fake PNG files. Detailed filenames and expected content are documented inside each directory.
