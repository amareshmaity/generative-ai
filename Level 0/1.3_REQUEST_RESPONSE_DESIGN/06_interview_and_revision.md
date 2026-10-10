# 06. Interview and Revision

## Quick revision sheet

### What is request design?

It is the design of how clients send data to the server using URL, headers, parameters, and body.

### What is response design?

It is the design of how the server returns success or failure information in a clear and predictable way.

### Why does this matter?

Because APIs are easier to use, validate, test, and maintain when the request and response contract is clear.

## Most important things to revise

* path params vs query params vs body
* required vs optional fields
* clear field naming
* consistent response shape
* useful error responses
* request and response design in GenAI systems

## Interview questions

* Why is request and response design important in APIs?
* When should you use path params, query params, and request body?
* What makes a response design good?
* Why are vague error messages harmful?
* What fields are common in GenAI request payloads?
* How would you design a response for a document summarization API?

## Strong answer pattern

When answering:

1. define the idea simply
2. explain why it matters
3. give one clean example
4. relate it to backend or GenAI systems

## Example interview answer

Question:

Why does request and response design matter?

Good answer:

"Request and response design matters because an API is a contract between client and server. If request fields are unclear or response formats are inconsistent, integration becomes difficult and bugs increase. Good design uses clear field names, predictable structures, and useful error messages. This is especially important in GenAI systems where inputs like prompts, document ids, and generation settings need strong validation."

## Final note

If you can design routes correctly but cannot design requests and responses clearly, your API design is still incomplete.
