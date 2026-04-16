"""Pure-PyTorch replacements for torch_scatter functions.

Based on https://github.com/rerun-io/examples-monorepo/blob/main/packages/dpvo/dpvo/scatter_utils.py
Extended with scatter_max and scatter_mean for DROID-SLAM compatibility.
"""

import torch
from typing import Optional, Tuple


def _expand_index(index: torch.Tensor, src: torch.Tensor, dim: int) -> torch.Tensor:
    view = [1] * src.dim()
    view[dim] = index.shape[0]
    return index.view(*view).expand_as(src)


def scatter_sum(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    out: Optional[torch.Tensor] = None,
    dim_size: Optional[int] = None,
    fill_value: float = 0,
) -> torch.Tensor:
    index = index.long()
    if dim_size is None:
        dim_size = int(index.max().item()) + 1 if index.numel() > 0 else 0

    out_shape = list(src.shape)
    out_shape[dim] = dim_size
    out = src.new_zeros(out_shape) if out is None else out
    if dim_size == 0 or index.numel() == 0:
        return out

    out.scatter_add_(dim, _expand_index(index, src, dim), src)
    return out


def scatter_max(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    out: Optional[torch.Tensor] = None,
    dim_size: Optional[int] = None,
    fill_value: float = float("-inf"),
) -> Tuple[torch.Tensor, torch.Tensor]:
    index = index.long()
    if dim_size is None:
        dim_size = int(index.max().item()) + 1 if index.numel() > 0 else 0

    out_shape = list(src.shape)
    out_shape[dim] = dim_size
    out = torch.full(out_shape, fill_value, dtype=src.dtype, device=src.device)
    if dim_size == 0 or index.numel() == 0:
        return out, torch.full(out_shape, -1, dtype=torch.long, device=src.device)

    expanded_index = _expand_index(index, src, dim)
    out.scatter_reduce_(dim, expanded_index, src, reduce="amax", include_self=True)
    # Placeholder argmax indices — callers only use [0] (values)
    arg_out = torch.full(out_shape, -1, dtype=torch.long, device=src.device)
    return out, arg_out


def scatter_mean(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    out: Optional[torch.Tensor] = None,
    dim_size: Optional[int] = None,
    fill_value: float = 0,
) -> torch.Tensor:
    index = index.long()
    if dim_size is None:
        dim_size = int(index.max().item()) + 1 if index.numel() > 0 else 0

    sums = scatter_sum(src, index, dim=dim, dim_size=dim_size)
    ones = src.new_ones(src.shape)
    counts = scatter_sum(ones, index, dim=dim, dim_size=dim_size)
    return sums / counts.clamp_min(1)


def scatter_softmax(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    dim_size: Optional[int] = None,
) -> torch.Tensor:
    index = index.long()
    if dim_size is None:
        dim_size = int(index.max().item()) + 1 if index.numel() > 0 else 0
    if dim_size == 0 or index.numel() == 0:
        return torch.zeros_like(src)

    expanded_index = _expand_index(index, src, dim)
    max_shape = list(src.shape)
    max_shape[dim] = dim_size
    max_per_group = torch.full(
        max_shape, -torch.inf, dtype=src.dtype, device=src.device
    )
    max_per_group.scatter_reduce_(
        dim, expanded_index, src, reduce="amax", include_self=True
    )
    gathered_max = max_per_group.gather(dim, expanded_index)

    exp = torch.exp(src - gathered_max)
    denom = scatter_sum(exp, index, dim=dim, dim_size=dim_size)
    return exp / denom.gather(dim, expanded_index).clamp_min(
        torch.finfo(src.dtype).tiny
    )
