package ir.ac.mas.shop.service;

import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.model.PurchaseResult;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public final class PurchaseService {
    private static final int INITIAL_QUANTITY = 2;
    private static final String RESTRICTED_BUYER = "3B";

    private final Map<Product, Integer> inventory = new EnumMap<>(Product.class);
    private final List<String> successfulBuyers = new ArrayList<>();

    public PurchaseService() {
        inventory.put(Product.A, INITIAL_QUANTITY);
        inventory.put(Product.B, INITIAL_QUANTITY);
    }

    public PurchaseResult purchase(String buyerLocalName, Product product) {
        validateBuyerLocalName(buyerLocalName);
        Objects.requireNonNull(product, "product must not be null");

        if (RESTRICTED_BUYER.equals(buyerLocalName) && product == Product.B) {
            return PurchaseResult.BUYER_NOT_ALLOWED;
        }

        int availableQuantity = inventory.get(product);
        if (availableQuantity == 0) {
            return PurchaseResult.OUT_OF_STOCK;
        }

        inventory.put(product, availableQuantity - 1);
        successfulBuyers.add(buyerLocalName);
        return PurchaseResult.SUCCESS;
    }

    public Map<Product, Integer> getInventory() {
        return Map.copyOf(inventory);
    }

    public int getInventory(Product product) {
        Objects.requireNonNull(product, "product must not be null");
        return inventory.get(product);
    }

    public List<String> getSuccessfulBuyers() {
        return List.copyOf(successfulBuyers);
    }

    private static void validateBuyerLocalName(String buyerLocalName) {
        Objects.requireNonNull(buyerLocalName, "buyerLocalName must not be null");
        if (buyerLocalName.isBlank()) {
            throw new IllegalArgumentException("buyerLocalName must not be blank");
        }
    }
}
