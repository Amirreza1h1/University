package ir.ac.mas.shop.config;

import ir.ac.mas.shop.model.Product;
import org.junit.jupiter.api.Test;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class ScenarioConfigurationTest {
    @Test
    void missingScenarioPropertySelectsDefault() {
        ScenarioConfiguration configuration =
                ScenarioConfiguration.fromProperties(null, null);

        assertEquals("default", configuration.name());
        assertEquals(0L, configuration.initialBuyerDelayMillis());
    }

    @Test
    void everySupportedScenarioHasFourUniqueBuyerNames() {
        Set<String> expectedNames = Set.of("1B", "2B", "3B", "4B");

        for (String scenarioName : ScenarioConfiguration.supportedScenarioNames()) {
            ScenarioConfiguration configuration =
                    ScenarioConfiguration.fromProperties(scenarioName, null);
            List<String> names = configuration.buyerPlans().stream()
                    .map(BuyerPlan::buyerLocalName)
                    .toList();

            assertEquals(4, names.size(), scenarioName);
            assertEquals(expectedNames, new HashSet<>(names), scenarioName);
        }
    }

    @Test
    void scenarioDelaysAreDeterministicAndIncludeInitialDelay() {
        ScenarioConfiguration configuration =
                ScenarioConfiguration.fromProperties("balanced", "15000");

        assertEquals(15_000L, configuration.initialBuyerDelayMillis());
        assertEquals(List.of(15_500L, 16_000L, 16_500L, 17_000L),
                configuration.buyerPlans().stream().map(BuyerPlan::delayMillis).toList());
    }

    @Test
    void negativeInitialDelayFallsBackToZero() {
        ScenarioConfiguration configuration =
                ScenarioConfiguration.fromProperties("all-a", "-1");

        assertEquals(0L, configuration.initialBuyerDelayMillis());
        assertEquals(List.of(500L, 1_000L, 1_500L, 2_000L),
                configuration.buyerPlans().stream().map(BuyerPlan::delayMillis).toList());
    }

    @Test
    void unknownScenarioFallsBackToDefault() {
        ScenarioConfiguration unknown =
                ScenarioConfiguration.fromProperties("not-a-scenario", null);
        ScenarioConfiguration expected =
                ScenarioConfiguration.fromProperties("default", null);

        assertEquals("default", unknown.name());
        assertEquals(expected.buyerPlans(), unknown.buyerPlans());
    }

    @Test
    void restrictionPriorityOrders4BBefore3B() {
        ScenarioConfiguration configuration =
                ScenarioConfiguration.fromProperties("restriction-priority", null);

        assertEquals(List.of("1B", "2B", "4B", "3B"),
                configuration.buyerPlans().stream().map(BuyerPlan::buyerLocalName).toList());
    }

    @Test
    void everyScenarioContainsOnlyValidProducts() {
        for (String scenarioName : ScenarioConfiguration.supportedScenarioNames()) {
            ScenarioConfiguration configuration =
                    ScenarioConfiguration.fromProperties(scenarioName, null);
            for (BuyerPlan plan : configuration.buyerPlans()) {
                assertNotNull(plan.product(), scenarioName + ": " + plan.buyerLocalName());
                assertEquals(Product.valueOf(plan.product().name()), plan.product());
            }
        }
    }
}
