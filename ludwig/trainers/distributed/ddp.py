from typing import Any

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.optim import Optimizer

from ludwig.trainers.distributed.base import DistributedStrategy


class DDPStrategy(DistributedStrategy):
    def wrap_model(self, model: nn.Module) -> nn.Module:
        return DDP(model, device_ids=[self.rank()])

    def wrap_optimizer(self, optimizer: Optimizer) -> Optimizer:
        return optimizer

    def size(self) -> int:
        return dist.get_world_size()

    def rank(self) -> int:
        return dist.get_rank()

    def barrier(self):
        return dist.barrier()

    def allreduce(self, t: torch.Tensor) -> torch.Tensor:
        return dist.all_reduce(t)

    def broadcast(self, t: torch.Tensor) -> torch.Tensor:
        return dist.broadcast(t)

    def sync_model(self, model: nn.Module):
        # TODO(travis): open question if this is needed to ensure all workers using same weights
        pass

    def sync_optimizer(self, optimizer: Optimizer):
        # TODO(travis): open question if this is needed to ensure all workers using same optimizer state
        pass

    def broadcast_object(self, v: Any) -> Any:
        return dist.broadcast_object_list([v])[0]
