"""The LM Format Enforcer logits processor."""
import math
from typing import List, Optional, Union

import torch
from lmformatenforcer import (CharacterLevelParser, FormatEnforcerAnalyzer,
                              TokenEnforcer, TokenEnforcerTokenizerData)
from lmformatenforcer.integrations.transformers import (
    build_token_enforcer_tokenizer_data)
from transformers import PreTrainedTokenizerBase

import aphrodite


class aphroditeLogitsProcessor:

    def __init__(self, token_enforcer: TokenEnforcer, analyze):
        self.token_enforcer = token_enforcer
        self.analyzer = FormatEnforcerAnalyzer(
            token_enforcer) if analyze else None
        self.mask: Optional[torch.Tensor] = None

    def __call__(self, input_ids: List[int],
                 scores: torch.Tensor) -> torch.Tensor:
        token_sequence = input_ids
        if self.analyzer:
            self.analyzer.report_raw_logits(token_sequence, scores.tolist())
        allowed_tokens = self.token_enforcer.get_allowed_tokens(token_sequence)
        if self.mask is not None:
            self.mask.fill_(-math.inf)
        else:
            # We create it here because full_like() also copies the device
            # and dtype
            self.mask = torch.full_like(scores, -math.inf)
        self.mask[allowed_tokens] = 0
        scores = scores + self.mask
        return scores


def build_aphrodite_token_enforcer_tokenizer_data(
    tokenizer: Union[aphrodite.LLM, PreTrainedTokenizerBase]
) -> TokenEnforcerTokenizerData:
    # There are many classes that can be passed here, this logic should work
    # on all of them.
    if hasattr(tokenizer, 'get_tokenizer'):
        tokenizer = tokenizer.get_tokenizer()
    if hasattr(tokenizer, 'tokenizer'):
        tokenizer = tokenizer.tokenizer
    return build_token_enforcer_tokenizer_data(tokenizer)


def build_aphrodite_logits_processor(
        llm: Union[aphrodite.LLM, PreTrainedTokenizerBase,
                   TokenEnforcerTokenizerData],
        character_level_parser: CharacterLevelParser,
        analyze: bool = False) -> aphroditeLogitsProcessor:
    """Build the logits processor function that aphrodite will use to filter
    the tokens generated by the model. The result can be passed in the
    logits_processor list that is sent to the call or generate() method of
    models."""
    if not isinstance(llm, TokenEnforcerTokenizerData):
        llm = build_aphrodite_token_enforcer_tokenizer_data(llm)
    token_enforcer = TokenEnforcer(llm, character_level_parser)
    return aphroditeLogitsProcessor(token_enforcer, analyze)


__all__ = [
    'build_aphrodite_logits_processor',
    'build_aphrodite_token_enforcer_tokenizer_data'
]
