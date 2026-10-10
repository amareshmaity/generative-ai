# 08. Interview and Revision

## Quick revision sheet

### What is an API?

A communication interface between software systems.

### What is REST?

An architectural style for designing web APIs around resources, HTTP methods, statelessness, and consistency.

### What is a REST API?

A web API that follows REST principles.

### What is a resource?

The object or entity the API manages, such as users, documents, or orders.

### What is an endpoint?

Usually the combination of method, route, and behavior.

## Most important concepts to revise

* API vs REST API
* resource-based design
* route naming
* statelessness
* HTTP methods
* request and response structure
* good design vs bad design

## Interview questions

* What is the difference between API and REST API?
* What does stateless mean in REST?
* Why are resources usually represented as nouns?
* Difference between route and endpoint
* Why is `GET /deleteUser/5` bad REST design?
* Why is REST useful in GenAI applications?

## Strong answer pattern

When answering in interviews:

1. define the concept simply
2. explain why it exists
3. give one example
4. relate it to real systems

## Example interview answer

Question:

What is REST API?

Good answer:

"REST API is a web API designed around resources using standard HTTP methods like GET, POST, PUT, and DELETE. It follows principles such as stateless communication and consistent resource-based URLs. For example, `GET /documents/5` means fetching document 5. REST is useful because it makes systems predictable and easy to integrate."

## Self-check

You understand REST well if you can:

* explain it without memorized jargon
* design resources for a new app idea
* choose good route names
* choose correct methods
* identify bad API design quickly
* explain how REST fits a GenAI backend

## Final note

Do not rush to frameworks before this part becomes clear.

If REST concepts become strong, later topics like FastAPI, authentication, and GenAI backend development become much easier.

