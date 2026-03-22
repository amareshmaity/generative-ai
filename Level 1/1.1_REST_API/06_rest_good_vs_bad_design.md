# 06. Good REST Design vs Bad REST Design

## Why this matters

Many APIs work, but are still poorly designed.

A badly designed API may function technically, but it becomes:

* hard to understand
* hard to maintain
* hard to scale
* annoying for frontend or backend consumers

This file helps you build REST judgment, not just REST definitions.

## Example 1: route naming

Bad:

* `/getAllUsers`
* `/createNewUser`
* `/deleteUserById/7`

Better:

* `GET /users`
* `POST /users`
* `DELETE /users/7`

Why better:

* resource is clear
* action comes from method
* route naming is cleaner

## Example 2: singular vs plural

In most REST APIs, plural nouns are clearer for collections.

Better:

* `/users`
* `/orders`
* `/documents`

Less consistent:

* `/user`
* `/order`
* `/document`

Plural naming is not a law, but consistency matters a lot.

## Example 3: deep nesting

Too deep:

* `/companies/1/departments/3/teams/7/employees/9/tasks/4`

Problem:

* hard to read
* hard to maintain
* often signals design problems

Better:

* `/tasks/4`
* `/employees/9/tasks`

## Example 4: unclear response shape

Bad:

```json
{
  "data": "ok"
}
```

Why bad:

The response is too vague.

Better:

```json
{
  "message": "User created successfully",
  "user_id": 14
}
```

## Example 5: inconsistent style

Bad:

* `GET /users`
* `POST /create-document`
* `GET /orderList`

Problem:

No common design pattern.

Better:

* `GET /users`
* `POST /documents`
* `GET /orders`

## Example 6: mixing transport and business confusion

Bad design often exposes implementation confusion directly in the route.

Bad:

* `/run-prompt-chain`
* `/execute-llm-process`

These may reflect internal implementation, not external resource design.

Better:

* `/conversations`
* `/messages`
* `/summaries`

## Signs of good REST design

Good REST APIs usually feel:

* easy to guess
* easy to explain
* consistent across resources
* stable over time

## One useful question

When designing a route, ask:

If a new developer sees this for the first time, will they understand what this endpoint does without extra explanation?

If the answer is no, redesign it.

## What to remember

Good REST design is about clarity and consistency more than cleverness.

