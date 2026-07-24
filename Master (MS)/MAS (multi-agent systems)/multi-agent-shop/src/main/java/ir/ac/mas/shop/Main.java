package ir.ac.mas.shop;

import ir.ac.mas.shop.agent.BuyerAgent;
import ir.ac.mas.shop.agent.SellerAgent;
import ir.ac.mas.shop.config.BuyerPlan;
import ir.ac.mas.shop.config.ScenarioConfiguration;
import ir.ac.mas.shop.protocol.ShopProtocol;
import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.wrapper.AgentContainer;
import jade.wrapper.AgentController;
import jade.wrapper.StaleProxyException;

public final class Main {
    private static final String LOCAL_HOST = "127.0.0.1";
    private static final String LOCAL_PORT = "7778";
    private static final String GUI_PROPERTY = "mas.gui";

    private Main() {
    }

    public static void main(String[] args) {
        ScenarioConfiguration scenario = ScenarioConfiguration.fromSystemProperties();
        boolean guiEnabled = readGuiEnabled();
        printScenario(scenario, guiEnabled);

        Profile profile = new ProfileImpl();
        profile.setParameter(Profile.MAIN, Boolean.TRUE.toString());
        profile.setParameter(Profile.GUI, Boolean.toString(guiEnabled));
        profile.setParameter(Profile.LOCAL_HOST, LOCAL_HOST);
        profile.setParameter(Profile.LOCAL_PORT, LOCAL_PORT);

        Runtime runtime = Runtime.instance();
        runtime.setCloseVM(true);
        AgentContainer mainContainer = runtime.createMainContainer(profile);

        System.out.printf("[main] JADE main container started at %s:%s with GUI %s%n",
                LOCAL_HOST, LOCAL_PORT, guiEnabled ? "enabled" : "disabled");

        if (!startAgent(mainContainer, ShopProtocol.SELLER_LOCAL_NAME,
                SellerAgent.class.getName(), new Object[]{!guiEnabled})) {
            System.err.println("[main] Buyers were not started because the seller failed to start");
            stopContainerAfterStartupFailure(mainContainer);
            return;
        }

        for (BuyerPlan plan : scenario.buyerPlans()) {
            if (!startBuyer(mainContainer, plan)) {
                System.err.println("[main] Platform is shutting down after a buyer startup failure");
                stopContainerAfterStartupFailure(mainContainer);
                return;
            }
        }
    }

    private static boolean startBuyer(AgentContainer container, BuyerPlan plan) {
        Object[] arguments = {
            plan.product().name(), plan.delayMillis(), ShopProtocol.SELLER_LOCAL_NAME
        };
        return startAgent(container, plan.buyerLocalName(), BuyerAgent.class.getName(), arguments);
    }

    private static boolean readGuiEnabled() {
        String value = System.getProperty(GUI_PROPERTY);
        if (value == null || value.equalsIgnoreCase("true")) {
            return true;
        }
        if (value.equalsIgnoreCase("false")) {
            return false;
        }
        System.err.printf("[main] Invalid %s value '%s'; GUI remains enabled.%n",
                GUI_PROPERTY, value);
        return true;
    }

    private static void printScenario(ScenarioConfiguration scenario, boolean guiEnabled) {
        System.out.printf("[main] Selected scenario: %s%n", scenario.name());
        System.out.printf("[main] Initial screenshot delay: %d ms%n",
                scenario.initialBuyerDelayMillis());
        System.out.printf("[main] GUI enabled: %s%n", guiEnabled);
        for (BuyerPlan plan : scenario.buyerPlans()) {
            System.out.printf("[main] %s -> product=%s, effective delay=%d ms%n",
                    plan.buyerLocalName(), plan.product(), plan.delayMillis());
        }
    }

    private static boolean startAgent(AgentContainer container, String localName,
            String className, Object[] arguments) {
        try {
            AgentController controller = container.createNewAgent(localName, className, arguments);
            controller.start();
            return true;
        } catch (StaleProxyException exception) {
            System.err.printf("[main] Failed to create or start agent %s: %s%n",
                    localName, exception.getMessage());
            exception.printStackTrace(System.err);
            return false;
        }
    }

    private static void stopContainerAfterStartupFailure(AgentContainer container) {
        try {
            container.kill();
        } catch (StaleProxyException exception) {
            System.err.printf("[main] Failed to stop the JADE container: %s%n",
                    exception.getMessage());
            exception.printStackTrace(System.err);
        }
    }
}
