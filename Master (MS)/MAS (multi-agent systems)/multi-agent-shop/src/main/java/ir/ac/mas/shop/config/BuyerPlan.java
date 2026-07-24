package ir.ac.mas.shop.config;

import ir.ac.mas.shop.model.Product;

import java.util.Objects;

public record BuyerPlan(String buyerLocalName, Product product, long delayMillis) {
    public BuyerPlan {
        Objects.requireNonNull(buyerLocalName, "buyerLocalName must not be null");
        Objects.requireNonNull(product, "product must not be null");
        if (buyerLocalName.isBlank()) {
            throw new IllegalArgumentException("buyerLocalName must not be blank");
        }
        if (delayMillis < 0) {
            throw new IllegalArgumentException("delayMillis must not be negative");
        }
    }
}
