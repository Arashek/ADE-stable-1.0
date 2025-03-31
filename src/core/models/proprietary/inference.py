from typing import Dict, Any, Optional, List
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

class CodeCompletionInference:
    """Inference class for code completion models"""
    
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        device: str = "cuda",
        batch_size: int = 1
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.batch_size = batch_size
        
        # Move model to device
        self.model.to(device)
        self.model.eval()
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate code completion for the given prompt"""
        try:
            # Prepare input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048  # Adjust based on model context length
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    stopping_criteria=self._get_stopping_criteria(stop_sequences) if stop_sequences else None
                )
            
            # Decode and return
            completion = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            return completion
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate completion: {str(e)}")
    
    def _get_stopping_criteria(self, stop_sequences: List[str]):
        """Get stopping criteria for the given stop sequences"""
        from transformers import StoppingCriteria, StoppingCriteriaList
        
        class StopSequenceCriteria(StoppingCriteria):
            def __init__(self, tokenizer, stop_sequences):
                self.tokenizer = tokenizer
                self.stop_sequences = stop_sequences
                
            def __call__(self, input_ids, scores, **kwargs):
                # Decode the last few tokens
                last_tokens = self.tokenizer.decode(input_ids[0][-50:])
                
                # Check if any stop sequence is present
                for sequence in self.stop_sequences:
                    if sequence in last_tokens:
                        return True
                return False
        
        return StoppingCriteriaList([
            StopSequenceCriteria(self.tokenizer, stop_sequences)
        ])
        
    async def generate_batch(self, prompts: List[str]) -> List[str]:
        """Generate completions for a batch of prompts"""
        # Tokenize inputs
        inputs = self.tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.config.max_new_tokens
        ).to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repetition_penalty=self.config.repetition_penalty,
                length_penalty=self.config.length_penalty,
                early_stopping=self.config.early_stopping,
                do_sample=self.config.do_sample,
                num_return_sequences=self.config.num_return_sequences,
                use_cache=self.config.use_cache,
                pad_token_id=self.config.pad_token_id or self.tokenizer.pad_token_id,
                eos_token_id=self.config.eos_token_id or self.tokenizer.eos_token_id,
                bos_token_id=self.config.bos_token_id or self.tokenizer.bos_token_id
            )
            
        # Decode and return
        completions = []
        for i in range(len(prompts)):
            completion = self.tokenizer.decode(
                outputs[i][len(inputs["input_ids"][i]):],
                skip_special_tokens=True
            )
            completions.append(completion)
            
        return completions 