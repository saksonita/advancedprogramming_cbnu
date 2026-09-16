# Project Brief

## Goal
Build a Web UI assistant for the owner of a small café.
The owner types questions in natural language; the assistant uses **tools** to get facts and take actions.

## Users
One café owner. Not technical. Wants short, correct answers.

## What the assistant can do
- Show the menu and prices
- Check stock for an item
- Calculate prices, discounts, and totals
- Record a sale (updates stock and revenue)
- Report today's sales
- Simple chat UI in the browser

## Out of scope
- databases, real payments, real external APIs, multiple users

## Success criteria
- Never guesses numbers: all prices, stock, and totals come from tools.
- Can answer questions that need 2–3 tools in a row.
- Recovers from tool errors (e.g. wrong item name) instead of crashing.
- Asks for confirmation before changing data (record_sale).
