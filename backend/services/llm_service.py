import os
import time
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from prometheus_client import Counter, Histogram
import logging

# Initialize metrics
LLM_REQUESTS = Counter('llm_requests_total', 'Total number of LLM requests', ['model'])
LLM_LATENCY = Histogram('llm_latency_seconds', 'LLM request latency in seconds', ['model'])
LLM_TOKENS = Counter('llm_tokens_total', 'Total number of tokens processed', ['model'])

class LLMService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize Llama 2 and Mistral models."""
        try:
            # Initialize Llama 2
            llama2_model_name = "meta-llama/Llama-2-7b-chat-hf"
            self.models['llama2'] = AutoModelForCausalLM.from_pretrained(
                llama2_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.tokenizers['llama2'] = AutoTokenizer.from_pretrained(llama2_model_name)
            
            # Initialize Mistral
            mistral_model_name = "mistralai/Mistral-7B-v0.1"
            self.models['mistral'] = AutoModelForCausalLM.from_pretrained(
                mistral_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.tokenizers['mistral'] = AutoTokenizer.from_pretrained(mistral_model_name)
            
            self.logger.info("Successfully initialized LLM models")
        except Exception as e:
            self.logger.error(f"Error initializing LLM models: {str(e)}")
            raise

    async def generate_completion(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0
    ) -> Dict[str, Any]:
        """Generate text completion using the specified model."""
        if model not in self.models:
            raise ValueError(f"Model {model} not found")

        start_time = time.time()
        LLM_REQUESTS.labels(model=model).inc()

        try:
            # Prepare input
            tokenizer = self.tokenizers[model]
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)

            # Generate completion
            with torch.no_grad():
                outputs = self.models[model].generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            # Decode output
            completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
            completion = completion[len(prompt):]  # Remove prompt from completion

            # Calculate metrics
            latency = time.time() - start_time
            prompt_tokens = len(tokenizer.encode(prompt))
            completion_tokens = len(tokenizer.encode(completion))
            total_tokens = prompt_tokens + completion_tokens

            # Record metrics
            LLM_LATENCY.labels(model=model).observe(latency)
            LLM_TOKENS.labels(model=model).inc(total_tokens)

            return {
                "text": completion,
                "model": model,
                "usage": {
                    "promptTokens": prompt_tokens,
                    "completionTokens": completion_tokens,
                    "totalTokens": total_tokens
                },
                "latency": latency * 1000  # Convert to milliseconds
            }

        except Exception as e:
            self.logger.error(f"Error generating completion with {model}: {str(e)}")
            raise

    async def stream_completion(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9
    ):
        """Stream text completion using the specified model."""
        if model not in self.models:
            raise ValueError(f"Model {model} not found")

        start_time = time.time()
        LLM_REQUESTS.labels(model=model).inc()

        try:
            # Prepare input
            tokenizer = self.tokenizers[model]
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)

            # Generate completion with streaming
            with torch.no_grad():
                streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)
                generation_kwargs = {
                    **inputs,
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": True,
                    "pad_token_id": tokenizer.eos_token_id,
                    "streamer": streamer
                }
                
                # Start generation in a separate thread
                thread = Thread(target=self.models[model].generate, kwargs=generation_kwargs)
                thread.start()

                # Yield tokens as they are generated
                for token in streamer:
                    yield token

            # Calculate and record metrics
            latency = time.time() - start_time
            LLM_LATENCY.labels(model=model).observe(latency)

        except Exception as e:
            self.logger.error(f"Error streaming completion with {model}: {str(e)}")
            raise

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about the specified model."""
        if model not in self.models:
            raise ValueError(f"Model {model} not found")

        return {
            "name": model,
            "type": "causal",
            "contextLength": self.models[model].config.max_position_embeddings,
            "parameters": sum(p.numel() for p in self.models[model].parameters()),
            "device": str(self.device)
        }

# Create singleton instance
llm_service = LLMService() 