package ir.ac.mas.shop.behaviour;

import ir.ac.mas.shop.agent.SellerAgent;
import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.model.PurchaseResult;
import ir.ac.mas.shop.protocol.ShopProtocol;
import ir.ac.mas.shop.service.PurchaseService;
import jade.core.AID;
import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.util.Locale;

public final class SellerRequestBehaviour extends CyclicBehaviour {
    private final SellerAgent sellerAgent;
    private final PurchaseService purchaseService;
    private final MessageTemplate requestTemplate;

    public SellerRequestBehaviour(SellerAgent sellerAgent, PurchaseService purchaseService) {
        super(sellerAgent);
        this.sellerAgent = sellerAgent;
        this.purchaseService = purchaseService;
        this.requestTemplate = MessageTemplate.and(
                MessageTemplate.MatchPerformative(ACLMessage.REQUEST),
                MessageTemplate.and(
                        MessageTemplate.MatchOntology(ShopProtocol.ONTOLOGY),
                        MessageTemplate.MatchProtocol(ShopProtocol.PROTOCOL)));
    }

    @Override
    public void action() {
        ACLMessage request = sellerAgent.receive(requestTemplate);
        if (request == null) {
            block();
            return;
        }

        ACLMessage reply = request.createReply();
        AID sender = request.getSender();
        String buyerLocalName = sender == null ? null : sender.getLocalName();

        try {
            Product product = parseProduct(request.getContent());
            System.out.printf("[%s] Received request for %s from %s%n",
                    sellerAgent.getLocalName(), product, buyerLocalName);
            PurchaseResult result = purchaseService.purchase(buyerLocalName, product);
            prepareReply(reply, result, buyerLocalName, product);
            logResult(result, buyerLocalName, product);
        } catch (RuntimeException exception) {
            reply.setPerformative(ACLMessage.FAILURE);
            reply.setContent("Invalid purchase request: " + exception.getMessage());
            System.err.printf("[%s] Invalid request from %s: %s%n",
                    sellerAgent.getLocalName(), buyerLocalName, exception.getMessage());
        }

        sellerAgent.send(reply);
        sellerAgent.requestProcessed();
    }

    private static Product parseProduct(String content) {
        if (content == null || content.isBlank()) {
            throw new IllegalArgumentException("product content is missing");
        }
        try {
            return Product.valueOf(content.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException exception) {
            throw new IllegalArgumentException("unknown product " + content, exception);
        }
    }

    private static void prepareReply(ACLMessage reply, PurchaseResult result,
            String buyerLocalName, Product product) {
        switch (result) {
            case SUCCESS -> {
                reply.setPerformative(ACLMessage.INFORM);
                reply.setContent("Purchase successful: " + product);
            }
            case BUYER_NOT_ALLOWED -> {
                reply.setPerformative(ACLMessage.REFUSE);
                reply.setContent("Buyer " + buyerLocalName
                        + " is not allowed to purchase " + product);
            }
            case OUT_OF_STOCK -> {
                reply.setPerformative(ACLMessage.FAILURE);
                reply.setContent("Product " + product + " is out of stock");
            }
        }
    }

    private void logResult(PurchaseResult result, String buyerLocalName, Product product) {
        switch (result) {
            case SUCCESS -> System.out.printf(
                    "[%s] Sale completed: buyer=%s, product=%s, remaining=%d%n",
                    sellerAgent.getLocalName(), buyerLocalName, product,
                    purchaseService.getInventory(product));
            case BUYER_NOT_ALLOWED -> System.out.printf(
                    "[%s] Sale refused: buyer=%s is not allowed to purchase product=%s%n",
                    sellerAgent.getLocalName(), buyerLocalName, product);
            case OUT_OF_STOCK -> System.out.printf(
                    "[%s] Sale failed: product=%s is out of stock for buyer=%s%n",
                    sellerAgent.getLocalName(), product, buyerLocalName);
        }
    }
}
