# LLM Hosting Options: Self-host, Cloud-host, or OpenAI API (Or equivalent)

Since our plan is to use some sort of large language model to analyze our files, we need to decide how to host and access the models. There are three ways to approach this and this document will compare them so we can all agree on a decision.

1. Self-hosting an LLM server (on our own hardware)
2. Cloud-hosted model (AWS, Azure, GCP, or similar)
3. Using a hosted API (OpenAI or similar)

## 1) Self-hosting an LLM server

The self hosted option means we would have to set up and maintain our own infrastructure to run the model inference. There are many open-source models available that can be used but hardware restrictions may be an issue.

https://ollama.com/
Ollama provides an easy way to run LLMs locally. We can choose which models to download and run on our own hardware.

The system specs for Olamma are:
- Minimum 8GB RAM, 16GB+ recommended
- Disk space depends on model size (tens to hundreds GB)
- No GPU required for small models, but a discrete GPU (NVIDIA/AMD) helps with larger models.

Pros
- Full control over data and model
- Lower cost
- No vendor lock-in for model hosting

Cons
- Resource intensive on our hardware
- Scaling complexity
- Less access to the latest models
- Security responsibilities are fully on us

## 2) Cloud-hosted model deployment (managed on cloud provider)

For cloud hosting options, we can use services like AWS, Azure, or GCP to deploy a model and use it for processing.


### Google Cloud Platform (GCP) https://cloud.google.com/products/ai?hl=en

Google Cloud would allow us to deploy an Ollama instance or use their Vertex AI platform to host models.

It's possible to expose an endpoint and then call it from our application.

They claim they offer a free tier with $300 in credits for 90 days. This should be more than enough for us to get started and test things out. If we need more credits, I am sure we can just make an account with another user email in our group.


### Microsoft Azure https://azure.microsoft.com/en-ca

Provides $100 in credits annually with no credit card required. 

Azure Machine Learning service can be used to deploy and manage models. We can bring our own model or use pre-trained models from Azure's model catalog. From there, we can expose an endpoint and call it from our application.

### Oracle Cloud https://www.oracle.com/ca-en/cloud/free/

Oracles free tier includes $300 in credits for 30 days and always-free services, which can be used to host models and APIs. 

They also have an always-free tier that supposedly includes a 4-core, 24GB machine with a 200GB disk. This should be enough to get us started with hosting a model.

Like the previous providers, we can expose an endpoint for our application to call.

Pros
- Lower operational burden than self-hosting
- Way easier to scale
- We would have access to other AI services that might be useful

Cons
- Data leaves our local environment (may be a privacy).
- Free tiers can only last so long

## 3) Using a hosted API (OpenAI or other model APIs)

Use a third-party API (OpenAI, Anthropic, etc.) and send prompts over HTTPS. The provider hosts and maintains models and exposed APIs.

This is by far the easiest solution, but privacy and cost could be a big issue. 

I couldn't find a lot of information on free tiers for their API, but it seems like OpenAI offers $5 for new users. This converts to roughly 2,500,000 tokens. 

Below shows some OpenAI models with their costs:

| Model         | Input Tokens (per 1K) | Output Tokens (per 1K) | Total Cost per 1K Tokens |
| ------------- | --------------------- | ---------------------- | ------------------------ |
| GPT-3.5 Turbo | $0.0005               | $0.0015                | $0.002                   |
| GPT-4         | $0.030                | $0.060                 | $0.090                   |
| GPT-4o Mini   | $0.015                | $0.060                 | $0.075                   |

If we assume the total tokens per file ≈ 3,500, then we will be able to process about 714 files with the free $5 credit using GPT-3.5 Turbo. That's around $0.007 per file.

This is VERY slim and doesn't seem like a viable solution. We would most likely burn through credits very quickly if we had a lot of files to process.

Pros
- Minimal operational work
- Simple integration- HTTP-based API
- Could be useful for a prototype or just testing initially

Cons
- Data is sent to the provider and we have no control
- Expensive and lacking free tier
- Less model customization

# Conclusion

After comparing all the models and checking out their free plans, I believe the best option is to go with a cloud-hosted model deployment.

Many providers offer decent free tiers, and I think we would be able to rotate through them if we need more credits. This would allow us to avoid costs while still having a scalable and also relatively powerful model for free.

Using Oracle is temping because I believe their $300 free credits allow you to host GPU instances, which we would pretty much need for LLMs.

Let me know what you think and if you have any other suggestions in your PR review.
