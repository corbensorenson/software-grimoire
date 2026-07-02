You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A function `price_for(plan, seats, coupon=None)` applies tiered seat pricing, rejects negative seats, supports annual coupons, and rounds currency to cents. The implementation has branches for free, team, and enterprise plans, but no tests for boundary seats or invalid coupons.

USER REQUEST:
Write tests for this function.
