package ir.ac.mas.shop.agent;

import ir.ac.mas.shop.behaviour.SellerRequestBehaviour;
import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.protocol.ShopProtocol;
import ir.ac.mas.shop.service.PurchaseService;
import jade.core.Agent;
import jade.core.behaviours.WakerBehaviour;
import jade.wrapper.ContainerController;
import jade.wrapper.StaleProxyException;

public final class SellerAgent extends Agent {
    private static final long NON_GUI_SHUTDOWN_DELAY_MILLIS = 500L;

    private final PurchaseService purchaseService = new PurchaseService();
    private int processedRequests;
    private boolean finalReportPrinted;
    private boolean shutDownPlatformAfterCompletion;

    @Override
    protected void setup() {
        Object[] arguments = getArguments();
        shutDownPlatformAfterCompletion = arguments != null
                && arguments.length > 0
                && Boolean.TRUE.equals(arguments[0]);
        System.out.printf("[%s] Seller started with inventory %s%n",
                getLocalName(), formattedInventory());
        addBehaviour(new SellerRequestBehaviour(this, purchaseService));
    }

    public void requestProcessed() {
        processedRequests++;
        if (processedRequests == ShopProtocol.EXPECTED_REQUEST_COUNT && !finalReportPrinted) {
            printFinalReport();
            finishSellerLifecycle();
        }
    }

    private void finishSellerLifecycle() {
        if (!shutDownPlatformAfterCompletion) {
            doDelete();
            return;
        }
        addBehaviour(new WakerBehaviour(this, NON_GUI_SHUTDOWN_DELAY_MILLIS) {
            @Override
            protected void onWake() {
                System.out.printf("[%s] Non-GUI validation complete; shutting down JADE%n",
                        getLocalName());
                // JADE must not tear down its container from the agent scheduler thread itself.
                ContainerController container = getContainerController();
                Thread shutdownThread = new Thread(() -> {
                    try {
                        container.kill();
                    } catch (StaleProxyException exception) {
                        System.err.printf("[%s] Failed to stop the JADE container: %s%n",
                                getLocalName(), exception.getMessage());
                        exception.printStackTrace(System.err);
                    }
                }, "jade-platform-shutdown");
                shutdownThread.start();
            }
        });
    }

    private void printFinalReport() {
        finalReportPrinted = true;
        System.out.printf("[%s] Final inventory: %s%n", getLocalName(), formattedInventory());
        System.out.printf("[%s] Successful buyers: %s%n",
                getLocalName(), purchaseService.getSuccessfulBuyers());
        System.out.printf("[%s] Processed requests: %d%n", getLocalName(), processedRequests);
    }

    private String formattedInventory() {
        return "{A=" + purchaseService.getInventory(Product.A)
                + ", B=" + purchaseService.getInventory(Product.B) + "}";
    }

    @Override
    protected void takeDown() {
        System.out.printf("[%s] Seller stopped%n", getLocalName());
    }
}
