package ir.ac.mas.shop.service;

import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.model.PurchaseResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PurchaseServiceTest {
    private PurchaseService purchaseService;

    @BeforeEach
    void setUp() {
        purchaseService = new PurchaseService();
    }

    @Test
    void initialInventoryContainsTwoUnitsOfEachProduct() {
        assertEquals(Map.of(Product.A, 2, Product.B, 2), purchaseService.getInventory());
    }

    @Test
    void successfulPurchaseOfProductA() {
        assertEquals(PurchaseResult.SUCCESS, purchaseService.purchase("1B", Product.A));
    }

    @Test
    void successfulPurchaseOfProductB() {
        assertEquals(PurchaseResult.SUCCESS, purchaseService.purchase("1B", Product.B));
    }

    @Test
    void successfulPurchaseDecrementsOnlyRequestedProduct() {
        purchaseService.purchase("1B", Product.A);

        assertEquals(1, purchaseService.getInventory(Product.A));
        assertEquals(2, purchaseService.getInventory(Product.B));
    }

    @Test
    void buyer3BRequestingProductBIsNotAllowed() {
        assertEquals(PurchaseResult.BUYER_NOT_ALLOWED,
                purchaseService.purchase("3B", Product.B));
    }

    @Test
    void refusedRequestDoesNotChangeInventory() {
        Map<Product, Integer> inventoryBeforeRequest = purchaseService.getInventory();

        purchaseService.purchase("3B", Product.B);

        assertEquals(inventoryBeforeRequest, purchaseService.getInventory());
    }

    @Test
    void outOfStockRequestReturnsOutOfStock() {
        purchaseService.purchase("1B", Product.A);
        purchaseService.purchase("2B", Product.A);

        assertEquals(PurchaseResult.OUT_OF_STOCK,
                purchaseService.purchase("4B", Product.A));
    }

    @Test
    void outOfStockRequestDoesNotChangeInventory() {
        purchaseService.purchase("1B", Product.A);
        purchaseService.purchase("2B", Product.A);

        purchaseService.purchase("4B", Product.A);

        assertEquals(0, purchaseService.getInventory(Product.A));
        assertEquals(2, purchaseService.getInventory(Product.B));
    }

    @Test
    void failedAndRefusedBuyersAreNotRecorded() {
        purchaseService.purchase("1B", Product.A);
        purchaseService.purchase("2B", Product.A);
        purchaseService.purchase("3B", Product.B);
        purchaseService.purchase("4B", Product.A);

        assertFalse(purchaseService.getSuccessfulBuyers().contains("3B"));
        assertFalse(purchaseService.getSuccessfulBuyers().contains("4B"));
    }

    @Test
    void successfulBuyersAreRecorded() {
        purchaseService.purchase("1B", Product.A);
        purchaseService.purchase("2B", Product.B);

        assertEquals(List.of("1B", "2B"), purchaseService.getSuccessfulBuyers());
    }

    @Test
    void inventoryNeverBecomesNegative() {
        purchaseService.purchase("1B", Product.B);
        purchaseService.purchase("2B", Product.B);
        purchaseService.purchase("4B", Product.B);
        purchaseService.purchase("5B", Product.B);

        assertEquals(0, purchaseService.getInventory(Product.B));
        assertTrue(purchaseService.getInventory().values().stream().allMatch(quantity -> quantity >= 0));
    }

    @Test
    void returnedCollectionsCannotMutateInternalState() {
        purchaseService.purchase("1B", Product.A);
        Map<Product, Integer> inventoryView = purchaseService.getInventory();
        List<String> successfulBuyerView = purchaseService.getSuccessfulBuyers();

        assertThrows(UnsupportedOperationException.class,
                () -> inventoryView.put(Product.A, 100));
        assertThrows(UnsupportedOperationException.class,
                () -> successfulBuyerView.add("fake-buyer"));
        assertEquals(1, purchaseService.getInventory(Product.A));
        assertEquals(List.of("1B"), purchaseService.getSuccessfulBuyers());
    }

    @Test
    void invalidInputsAreRejected() {
        assertThrows(NullPointerException.class,
                () -> purchaseService.purchase(null, Product.A));
        assertThrows(IllegalArgumentException.class,
                () -> purchaseService.purchase("   ", Product.A));
        assertThrows(NullPointerException.class,
                () -> purchaseService.purchase("1B", null));
        assertThrows(NullPointerException.class,
                () -> purchaseService.getInventory(null));
    }
}
