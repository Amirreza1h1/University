package ir.ac.mas.shop.agent;

import ir.ac.mas.shop.behaviour.BuyerPurchaseBehaviour;
import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.protocol.ShopProtocol;
import jade.core.Agent;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class BuyerAgent extends Agent {
    private final List<Product> purchasedProducts = new ArrayList<>();

    @Override
    protected void setup() {
        try {
            BuyerConfiguration configuration = readConfiguration(getArguments());
            System.out.printf("[%s] Buyer started: product=%s, delay=%d ms, seller=%s%n",
                    getLocalName(), configuration.product(), configuration.delayMillis(),
                    configuration.sellerLocalName());
            addBehaviour(new BuyerPurchaseBehaviour(this, configuration.product(),
                    configuration.delayMillis(), configuration.sellerLocalName()));
        } catch (IllegalArgumentException exception) {
            System.err.printf("[%s] Invalid startup arguments: %s%n",
                    getLocalName(), exception.getMessage());
            doDelete();
        }
    }

    public void recordPurchase(Product product) {
        purchasedProducts.add(product);
    }

    public void printPurchasedProducts() {
        System.out.printf("[%s] Purchased products: %s%n", getLocalName(), purchasedProducts);
    }

    private static BuyerConfiguration readConfiguration(Object[] arguments) {
        if (arguments == null || arguments.length < 2 || arguments.length > 3) {
            throw new IllegalArgumentException(
                    "expected product, delay milliseconds, and optional seller local name");
        }

        Product product;
        try {
            product = Product.valueOf(String.valueOf(arguments[0]).trim().toUpperCase(Locale.ROOT));
        } catch (RuntimeException exception) {
            throw new IllegalArgumentException("product must be A or B", exception);
        }

        long delayMillis;
        try {
            delayMillis = arguments[1] instanceof Number number
                    ? number.longValue()
                    : Long.parseLong(String.valueOf(arguments[1]));
        } catch (RuntimeException exception) {
            throw new IllegalArgumentException("delay must be a whole number", exception);
        }
        if (delayMillis < 0) {
            throw new IllegalArgumentException("delay must not be negative");
        }

        String sellerLocalName = arguments.length == 3
                ? String.valueOf(arguments[2]).trim()
                : ShopProtocol.SELLER_LOCAL_NAME;
        if (sellerLocalName.isBlank()) {
            throw new IllegalArgumentException("seller local name must not be blank");
        }

        return new BuyerConfiguration(product, delayMillis, sellerLocalName);
    }

    @Override
    protected void takeDown() {
        System.out.printf("[%s] Buyer stopped%n", getLocalName());
    }

    private record BuyerConfiguration(Product product, long delayMillis, String sellerLocalName) {
    }
}
