# Multi-Agent Shop

A small university Multi-Agent Systems project built with Java 17, Maven, and JADE 4.6.0. The application starts its own JADE main container and GUI, one seller, and four buyers.

## Required software

- Java Development Kit (JDK) 17
- Apache Maven
- Visual Studio Code with the Microsoft Extension Pack for Java (recommended)
- JADE 4.6.0 at `lib/jade.jar`

Verify Java 17:

```powershell
java -version
javac -version
```

Verify Maven:

```powershell
mvn -version
```

## Build and test

Build the project:

```powershell
mvn clean package
```

Run the tests:

```powershell
mvn clean test
```

## Run the application

Before starting the application, make sure no standalone JADE window is using port `7778`.

From PowerShell after compilation:

```powershell
mvn clean package
java "-Djava.net.preferIPv4Stack=true" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

From Command Prompt after compilation:

```cmd
mvn clean package
java -Djava.net.preferIPv4Stack=true -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

With no additional properties, this runs the original `default` scenario with the JADE GUI enabled.

## Deterministic scenarios

Select a scenario with the `mas.scenario` JVM property. Supported names are:

| Scenario | Buyer plan in processing order | Expected final inventory | Successful buyers |
|---|---|---|---|
| `default` | `1B:B`, `2B:B`, `3B:B`, `4B:B` | `{A=2, B=0}` | `[1B, 2B]` |
| `all-a` | `1B:A`, `2B:A`, `3B:A`, `4B:A` | `{A=0, B=2}` | `[1B, 2B]` |
| `balanced` | `1B:A`, `2B:B`, `3B:A`, `4B:B` | `{A=0, B=0}` | `[1B, 2B, 3B, 4B]` |
| `refusal-stock` | `1B:A`, `2B:A`, `3B:B`, `4B:B` | `{A=0, B=1}` | `[1B, 2B, 4B]` |
| `restriction-priority` | `1B:B`, `2B:B`, `4B:B`, `3B:B` | `{A=2, B=0}` | `[1B, 2B]` |

An absent property selects `default`. An unknown name prints the supported values and safely falls back to `default`.

Example normal GUI execution:

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=balanced" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

### Optional properties

- `mas.initialBuyerDelayMs`: non-negative delay added to every buyer's base delay; default `0`. Invalid or negative values print a warning and use zero.
- `mas.gui`: `true` by default. Set to `false` for console validation; the same agents and ACL messages run without RMA, then JADE shuts down naturally.

Non-GUI example:

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.gui=false" "-Dmas.scenario=all-a" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

### Screenshot capture commands

These commands add a 15-second preparation delay:

```powershell
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=default" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=all-a" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=balanced" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=refusal-stock" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
java "-Djava.net.preferIPv4Stack=true" "-Dmas.scenario=restriction-priority" "-Dmas.initialBuyerDelayMs=15000" -cp "target\classes;lib\jade.jar" ir.ac.mas.shop.Main
```

### Run all scenarios automatically

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-scenarios.ps1
```

The script builds once, runs all five scenarios sequentially with no screenshot delay and no GUI, validates each exit code/result, and saves logs under `docs/screenshots/scenario-*`.

The Maven Exec Plugin is also configured with the main class. If system-scoped JADE dependencies are included correctly in the local Maven environment, run:

```powershell
mvn "-Djava.net.preferIPv4Stack=true" exec:java
```

The IPv4 system property is required on this machine. Both the direct Java commands and the Maven command above provide it explicitly.

## Standalone JADE platform

The following known-working command starts the JADE GUI on `127.0.0.1:7778` and prefers IPv4:

```powershell
java "-Djava.net.preferIPv4Stack=true" -cp ".\lib\jade.jar" jade.Boot -gui -local-host 127.0.0.1 -local-port 7778
```

Close the standalone JADE window before starting the project because both launchers use port `7778`.

## JADE Sniffer

For message-flow screenshots, open the **Sniffer Agent** from the RMA window's **Tools** menu. Add `seller`, `1B`, `2B`, `3B`, and `4B` to the sniffed agents before running or while requests are active.
