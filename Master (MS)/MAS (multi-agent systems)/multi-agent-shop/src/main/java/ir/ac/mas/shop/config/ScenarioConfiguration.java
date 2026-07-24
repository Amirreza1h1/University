package ir.ac.mas.shop.config;

import ir.ac.mas.shop.model.Product;

import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;

public record ScenarioConfiguration(
        String name,
        long initialBuyerDelayMillis,
        List<BuyerPlan> buyerPlans) {

    public static final String SCENARIO_PROPERTY = "mas.scenario";
    public static final String INITIAL_DELAY_PROPERTY = "mas.initialBuyerDelayMs";

    private static final String DEFAULT_SCENARIO = "default";
    private static final long LARGEST_BASE_DELAY_MILLIS = 2_000L;
    private static final List<String> SUPPORTED_SCENARIOS = List.of(
            DEFAULT_SCENARIO,
            "all-a",
            "balanced",
            "refusal-stock",
            "restriction-priority");

    public ScenarioConfiguration {
        Objects.requireNonNull(name, "name must not be null");
        Objects.requireNonNull(buyerPlans, "buyerPlans must not be null");
        buyerPlans = List.copyOf(buyerPlans);
        if (initialBuyerDelayMillis < 0) {
            throw new IllegalArgumentException("initialBuyerDelayMillis must not be negative");
        }
        if (buyerPlans.size() != 4) {
            throw new IllegalArgumentException("a scenario must contain exactly four buyers");
        }
        Set<String> buyerNames = new HashSet<>();
        for (BuyerPlan plan : buyerPlans) {
            if (!buyerNames.add(plan.buyerLocalName())) {
                throw new IllegalArgumentException(
                        "buyer names must be unique: " + plan.buyerLocalName());
            }
        }
    }

    public static ScenarioConfiguration fromSystemProperties() {
        return fromProperties(
                System.getProperty(SCENARIO_PROPERTY),
                System.getProperty(INITIAL_DELAY_PROPERTY));
    }

    public static ScenarioConfiguration fromProperties(
            String scenarioProperty, String initialDelayProperty) {
        String selectedScenario = selectScenarioName(scenarioProperty);
        long initialDelayMillis = parseInitialDelay(initialDelayProperty);
        List<BuyerPlan> effectivePlans = basePlans(selectedScenario).stream()
                .map(plan -> new BuyerPlan(
                        plan.buyerLocalName(),
                        plan.product(),
                        plan.delayMillis() + initialDelayMillis))
                .toList();
        return new ScenarioConfiguration(selectedScenario, initialDelayMillis, effectivePlans);
    }

    public static List<String> supportedScenarioNames() {
        return SUPPORTED_SCENARIOS;
    }

    private static String selectScenarioName(String scenarioProperty) {
        if (scenarioProperty == null) {
            return DEFAULT_SCENARIO;
        }
        String normalized = scenarioProperty.trim().toLowerCase(Locale.ROOT);
        if (SUPPORTED_SCENARIOS.contains(normalized)) {
            return normalized;
        }
        System.err.printf(
                "[main] Unknown scenario '%s'. Supported values: %s. Falling back to default.%n",
                scenarioProperty, SUPPORTED_SCENARIOS);
        return DEFAULT_SCENARIO;
    }

    private static long parseInitialDelay(String initialDelayProperty) {
        if (initialDelayProperty == null) {
            return 0L;
        }
        try {
            long parsed = Long.parseLong(initialDelayProperty.trim());
            if (parsed < 0 || parsed > Long.MAX_VALUE - LARGEST_BASE_DELAY_MILLIS) {
                throw new IllegalArgumentException("delay is outside the supported range");
            }
            return parsed;
        } catch (RuntimeException exception) {
            System.err.printf(
                    "[main] Invalid %s value '%s'; using 0 ms.%n",
                    INITIAL_DELAY_PROPERTY, initialDelayProperty);
            return 0L;
        }
    }

    private static List<BuyerPlan> basePlans(String scenarioName) {
        return switch (scenarioName) {
            case "all-a" -> List.of(
                    plan("1B", Product.A, 500L),
                    plan("2B", Product.A, 1_000L),
                    plan("3B", Product.A, 1_500L),
                    plan("4B", Product.A, 2_000L));
            case "balanced" -> List.of(
                    plan("1B", Product.A, 500L),
                    plan("2B", Product.B, 1_000L),
                    plan("3B", Product.A, 1_500L),
                    plan("4B", Product.B, 2_000L));
            case "refusal-stock" -> List.of(
                    plan("1B", Product.A, 500L),
                    plan("2B", Product.A, 1_000L),
                    plan("3B", Product.B, 1_500L),
                    plan("4B", Product.B, 2_000L));
            case "restriction-priority" -> List.of(
                    plan("1B", Product.B, 500L),
                    plan("2B", Product.B, 1_000L),
                    plan("4B", Product.B, 1_500L),
                    plan("3B", Product.B, 2_000L));
            default -> List.of(
                    plan("1B", Product.B, 500L),
                    plan("2B", Product.B, 1_000L),
                    plan("3B", Product.B, 1_500L),
                    plan("4B", Product.B, 2_000L));
        };
    }

    private static BuyerPlan plan(String buyerLocalName, Product product, long delayMillis) {
        return new BuyerPlan(buyerLocalName, product, delayMillis);
    }
}
