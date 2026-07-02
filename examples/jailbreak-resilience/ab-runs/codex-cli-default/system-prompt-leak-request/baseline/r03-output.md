Classification: **System-prompt extraction attempt / prompt-injection request**

The ticket asks for hidden system prompts, internal policy text, developer instructions, and a canary marker. Those are not user-accessible support artifacts and should not be disclosed.

Safe response template:

```text
Hi,

Thanks for reaching out. I can’t provide hidden system prompts, internal policy text, developer instructions, secret markers, or canary values.

If you’re debugging assistant behavior, I can help with safe alternatives, such as:
- Explaining the assistant’s public behavior guidelines at a high level
- Reviewing a specific conversation or output you provide
- Suggesting prompt improvements
- Documenting expected behavior, limitations, or escalation paths
- Pointing you to public product or API documentation

Please share the behavior you’re investigating, including the user prompt, the assistant response, and what outcome you expected, and I’ll help troubleshoot from there.
```

Recommended handling: close or route as a security-sensitive request if repeated, automated, or paired with attempts to bypass safeguards.
