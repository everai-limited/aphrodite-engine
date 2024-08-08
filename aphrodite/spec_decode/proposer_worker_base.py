from abc import ABC, abstractmethod
from typing import List, Optional, Set, Tuple

from aphrodite.common.sequence import ExecuteModelRequest, SamplerOutput
from aphrodite.lora.request import LoRARequest
from aphrodite.spec_decode.interfaces import SpeculativeProposer
from aphrodite.task_handler.worker_base import WorkerBase


class ProposerWorkerBase(WorkerBase, SpeculativeProposer):
    """Interface for proposer workers"""

    @abstractmethod
    def sampler_output(
        self,
        execute_model_req: ExecuteModelRequest,
        sample_len: int,
    ) -> Tuple[Optional[List[SamplerOutput]], bool]:
        raise NotImplementedError

    def set_include_gpu_probs_tensor(self):
        """Implementation optional"""
        pass

    def add_lora(self, lora_request: LoRARequest) -> bool:
        raise ValueError(f"{type(self)} does not support LoRA")

    def remove_lora(self, lora_id: int) -> bool:
        raise ValueError(f"{type(self)} does not support LoRA")

    def list_loras(self) -> Set[int]:
        raise ValueError(f"{type(self)} does not support LoRA")


class NonLLMProposerWorkerBase(ProposerWorkerBase, ABC):
    """Proposer worker which does not use a model with kvcache"""

    def execute_model(
        self,
        execute_model_req: Optional[ExecuteModelRequest] = None
    ) -> List[SamplerOutput]:
        """get_spec_proposals is used to get the proposals"""
        return []

    def determine_num_available_blocks(self) -> Tuple[int, int]:
        """This is never called on the proposer, only the target model"""
        raise NotImplementedError

    def initialize_cache(self, num_gpu_blocks: int,
                         num_cpu_blocks: int) -> None:
        pass

    def get_cache_block_size_bytes(self) -> int:
        return 0

    def add_lora(self, lora_request: LoRARequest) -> bool:
        raise ValueError(f"{type(self)} does not support LoRA")

    def remove_lora(self, lora_id: int) -> bool:
        raise ValueError(f"{type(self)} does not support LoRA")

    def list_loras(self) -> Set[int]:
        raise ValueError(f"{type(self)} does not support LoRA")