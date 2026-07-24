package ir.ac.mas.shop.behaviour;

import ir.ac.mas.shop.agent.BuyerAgent;
import ir.ac.mas.shop.model.Product;
import ir.ac.mas.shop.protocol.ShopProtocol;
import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.util.UUID;

public final class BuyerPurchaseBehaviour extends Behaviour {
    private final BuyerAgent buyerAgent;
    private final Product requestedProduct;
    private final String sellerLocalName;
    private final long requestTimeMillis;
    private final String conversationId;
    private final String replyWith;

    private boolean requestSent;
    private boolean finished;
    private MessageTemplate responseTemplate;

    public BuyerPurchaseBehaviour(BuyerAgent buyerAgent, Product requestedProduct,
            long delayMillis, String sellerLocalName) {
        super(buyerAgent);
        this.buyerAgent = buyerAgent;
        this.requestedProduct = requestedProduct;
        this.sellerLocalName = sellerLocalName;
        this.requestTimeMillis = System.currentTimeMillis() + delayMillis;
        this.conversationId = buyerAgent.getLocalName() + "-purchase-" + UUID.randomUUID();
        this.replyWith = buyerAgent.getLocalName() + "-request-" + UUID.randomUUID();
    }

    @Override
    public void action() {
        if (!requestSent) {
            long remainingDelay = requestTimeMillis - System.currentTimeMillis();
            if (remainingDelay > 0) {
                block(remainingDelay);
                return;
            }
            sendRequest();
        }

        ACLMessage response = buyerAgent.receive(responseTemplate);
        if (response == null) {
            block();
            return;
        }

        handleResponse(response);
        buyerAgent.printPurchasedProducts();
        finished = true;
        buyerAgent.doDelete();
    }

    private void sendRequest() {
        ACLMessage request = new ACLMessage(ACLMessage.REQUEST);
        request.addReceiver(new AID(sellerLocalName, AID.ISLOCALNAME));
        request.setOntology(ShopProtocol.ONTOLOGY);
        request.setProtocol(ShopProtocol.PROTOCOL);
        request.setContent(requestedProduct.name());
        request.setConversationId(conversationId);
        request.setReplyWith(replyWith);

        responseTemplate = MessageTemplate.and(
                MessageTemplate.MatchConversationId(conversationId),
                MessageTemplate.MatchInReplyTo(replyWith));

        System.out.printf("[%s] Requesting product %s%n",
                buyerAgent.getLocalName(), requestedProduct);
        buyerAgent.send(request);
        requestSent = true;
    }

    private void handleResponse(ACLMessage response) {
        switch (response.getPerformative()) {
            case ACLMessage.INFORM -> {
                buyerAgent.recordPurchase(requestedProduct);
                System.out.printf("[%s] Purchase successful: %s%n",
                        buyerAgent.getLocalName(), requestedProduct);
            }
            case ACLMessage.REFUSE -> System.out.printf("[%s] Purchase refused: %s%n",
                    buyerAgent.getLocalName(), response.getContent());
            case ACLMessage.FAILURE -> System.out.printf("[%s] Purchase failed: %s%n",
                    buyerAgent.getLocalName(), response.getContent());
            default -> System.err.printf("[%s] Unexpected response %s: %s%n",
                    buyerAgent.getLocalName(),
                    ACLMessage.getPerformative(response.getPerformative()), response.getContent());
        }
    }

    @Override
    public boolean done() {
        return finished;
    }
}
