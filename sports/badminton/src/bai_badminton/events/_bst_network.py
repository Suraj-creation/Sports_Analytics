"""Inference-only BST-CG-AP architecture, adapted from Jing-Yuan Chang's MIT code.

Source commit c93acfa736ed784ba7bea4ec9d360001dea9b728:
https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer
See bst_LICENSE.txt. Retains checkpoint parameter names and forward operations.
Training/model-summary code and unused architectures are omitted. Positional
initialization is omitted because the adapter MUST strictly load every parameter
from the pinned checkpoint before inference. This is not an untrained fallback.
"""

# ruff: noqa: N801, N803, N806
from __future__ import annotations

import torch
from torch import Tensor, nn


class MLP(nn.Module):
    """Same as MLP_Block in TemPose paper."""

    def __init__(self, in_dim, out_dim, hd_dim, drop_p=0.0) -> None:
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, hd_dim), nn.GELU(), nn.Dropout(drop_p, inplace=True), nn.Linear(hd_dim, out_dim)
        )

    def forward(self, x: Tensor):
        return self.mlp(x)


class MLP_Head(nn.Module):
    """Same as MLP_Head in TemPose."""

    def __init__(self, in_dim, out_dim, hd_dim, drop_p=0.0) -> None:
        super().__init__()
        self.layer_norm = nn.LayerNorm(in_dim)
        self.mlp = MLP(in_dim, out_dim, hd_dim, drop_p)

    def forward(self, x: Tensor):
        x = self.layer_norm(x)
        x = self.mlp(x)
        return x


class FeedForward(nn.Module):
    """Same as FeedForward in TemPose."""

    def __init__(self, in_dim, out_dim, hd_dim, drop_p=0.0) -> None:
        super().__init__()
        self.mlp = MLP(in_dim, out_dim, hd_dim, drop_p)
        self.dropout = nn.Dropout(drop_p, inplace=True)

    def forward(self, x: Tensor):
        x = self.mlp(x)
        x = self.dropout(x)
        return x


class MultiHeadAttention(nn.Module):
    """Same as Attention in TemPose."""

    def __init__(self, d_model, d_head, n_head, drop_p) -> None:
        super().__init__()
        d_cat = d_head * n_head
        self.h = n_head
        self.to_qkv = nn.Linear(d_model, d_cat * 3, bias=False)
        self.scale = d_head ** (-0.5)
        self.attend = nn.Sequential(nn.Softmax(dim=-1), nn.Dropout(drop_p))
        self.tail = (
            nn.Sequential(nn.Linear(d_cat, d_model), nn.Dropout(drop_p, inplace=True))
            if n_head != 1 or d_cat != d_model
            else nn.Identity()
        )

    def forward(self, x: Tensor, mask: Tensor = None):
        bn, t, _ = x.shape
        qkv: Tensor = self.to_qkv(x)
        qkv = qkv.view(bn, t, self.h, -1).chunk(3, dim=-1)
        q, k, v = map(lambda ts: ts.transpose(1, 2), qkv)
        dots: Tensor = q.contiguous() @ k.transpose(-1, -2).contiguous() * self.scale
        if mask is not None:
            mask = mask.view(bn, 1, 1, t)
            dots = dots.masked_fill(mask == 0.0, -torch.inf)
        coef = self.attend(dots)
        attension: Tensor = coef @ v.contiguous()
        out = attension.transpose(1, 2).reshape(bn, t, -1)
        out = self.tail(out)
        return out


class TransformerLayer(nn.Module):
    def __init__(self, d_model, d_head, n_head, hd_mlp, drop_p) -> None:
        super().__init__()
        self.layer_norm1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, d_head, n_head, drop_p)
        self.layer_norm2 = nn.LayerNorm(d_model)
        self.ff = FeedForward(d_model, d_model, hd_mlp, drop_p)

    def forward(self, x: Tensor, mask=None):
        z = self.layer_norm1(x)
        x = self.attn(z, mask) + x
        z = self.layer_norm2(x)
        x = self.ff(z) + x
        return x


class TransformerEncoder(nn.Module):
    """Same as Transformer in TemPose."""

    def __init__(self, d_model, d_head, n_head, depth, hd_mlp, drop_p) -> None:
        super().__init__()
        self.layers = nn.ModuleList([TransformerLayer(d_model, d_head, n_head, hd_mlp, drop_p) for _ in range(depth)])

    def forward(self, x: Tensor, mask=None):
        for layer in self.layers:
            x = layer(x, mask)
        return x


class TCN(nn.Module):
    """Same as TCN in TemPose. There is a bit different from the original TCN."""

    def __init__(self, in_channel, channels: list[int], kernel_size=5, drop_p=0.3) -> None:
        """`kernel_size` should be an odd number, so the output sequence length can remain the same as input."""
        super().__init__()
        layers = []
        for i in range(len(channels)):
            in_ch = in_channel if i == 0 else channels[i - 1]
            out_ch = channels[i]
            dilation = i * 2 + 1
            padding = (kernel_size - 1) * dilation // 2
            layers += [
                nn.Conv1d(in_ch, out_ch, kernel_size, padding=padding, dilation=dilation),
                nn.BatchNorm1d(out_ch),
                nn.GELU(),
                nn.Dropout(drop_p, inplace=True),
            ]
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor):
        return self.net(x)


class MultiHeadCrossAttention(nn.Module):
    def __init__(self, d_model, d_head, n_head, drop_p) -> None:
        super().__init__()
        d_cat = d_head * n_head
        self.h = n_head
        self.to_q = nn.Linear(d_model, d_cat, bias=False)
        self.to_kv = nn.Linear(d_model, d_cat * 2, bias=False)
        self.scale = d_head ** (-0.5)
        self.attend = nn.Sequential(nn.Softmax(dim=-1), nn.Dropout(drop_p))
        self.tail = (
            nn.Sequential(nn.Linear(d_cat, d_model), nn.Dropout(drop_p, inplace=True))
            if n_head != 1 or d_cat != d_model
            else nn.Identity()
        )

    def forward(self, x1: Tensor, x2: Tensor, mask: Tensor = None):
        q: Tensor = self.to_q(x1)
        kv: Tensor = self.to_kv(x2)
        b, t, _ = q.shape
        q = q.view(b, t, self.h, -1).transpose(1, 2)
        kv = kv.view(b, t, self.h, -1).chunk(2, dim=-1)
        k, v = map(lambda ts: ts.transpose(1, 2), kv)
        dots: Tensor = q.contiguous() @ k.transpose(-1, -2).contiguous() * self.scale
        if mask is not None:
            mask = mask.view(b, 1, 1, t)
            dots = dots.masked_fill(mask == 0.0, -torch.inf)
        coef = self.attend(dots)
        attension: Tensor = coef @ v.contiguous()
        out = attension.transpose(1, 2).reshape(b, t, -1)
        out = self.tail(out)
        return out


class CrossTransformerLayer(nn.Module):
    def __init__(self, d_model, d_head, n_head, hd_mlp, drop_p) -> None:
        super().__init__()
        self.layer_norm1_x1 = nn.LayerNorm(d_model)
        self.layer_norm1_x2 = nn.LayerNorm(d_model)
        self.cross_attn = MultiHeadCrossAttention(d_model, d_head, n_head, drop_p)
        self.layer_norm2 = nn.LayerNorm(d_model)
        self.ff = FeedForward(d_model, d_model, hd_mlp, drop_p)

    def forward(self, x1: Tensor, x2: Tensor, mask=None):
        x1 = self.layer_norm1_x1(x1)
        x2 = self.layer_norm1_x2(x2)
        x = self.cross_attn(x1, x2, mask)
        z = self.layer_norm2(x)
        x = self.ff(z) + x
        return x


class BST_CG_AP(nn.Module):
    """BST_CleanGate_AimPlayer
    - PPF: Pose Position Fusion
    - Adding Clean Gate and Cosine Simularity
    """

    def __init__(
        self,
        in_dim,
        seq_len,
        n_class=35,
        n_people=2,
        d_model=100,
        d_head=128,
        n_head=6,
        depth_tem=2,
        depth_inter=1,
        drop_p=0.3,
        mlp_d_scale=4,
        tcn_kernel_size=5,
    ):
        super().__init__()
        if n_people > 2:
            raise NotImplementedError
        self.mlp_positions = MLP(2, out_dim=in_dim, hd_dim=256, drop_p=drop_p)
        self.tcn_pose = TCN(in_dim, [d_model, d_model], tcn_kernel_size, drop_p)
        self.tcn_shuttle = TCN(2, [d_model // 2, d_model], tcn_kernel_size, drop_p)
        self.learned_token_tem = nn.Parameter(torch.randn(1, d_model))
        self.embedding_tem = nn.Parameter(torch.empty(1, 1 + seq_len, d_model))
        self.pre_dropout = nn.Dropout(drop_p, inplace=True)
        self.encoder_tem = TransformerEncoder(d_model, d_head, n_head, depth_tem, d_model * mlp_d_scale, drop_p)
        self.embedding_cross = nn.Parameter(torch.empty(1, seq_len, d_model))
        self.cross_trans = CrossTransformerLayer(d_model, d_head, n_head, d_model * mlp_d_scale, drop_p)
        self.learned_token_inter = nn.Parameter(torch.randn(1, d_model))
        self.embedding_inter = nn.Parameter(torch.empty(1, 1 + seq_len, d_model))
        self.encoder_inter = TransformerEncoder(d_model, d_head, n_head, depth_inter, d_model * mlp_d_scale, drop_p)
        self.cos_sim = nn.CosineSimilarity()
        self.mlp_clean = MLP(d_model, d_model, d_model, drop_p)
        self.mlp_head = MLP_Head(d_model * 3, n_class, d_model * mlp_d_scale, drop_p)
        self.d_model = d_model

    def forward(self, JnB: Tensor, shuttle: Tensor, pos: Tensor, video_len: Tensor):
        b, t, n, in_dim = JnB.shape
        JnB = JnB.permute(0, 2, 3, 1).reshape(b * n, in_dim, t)
        pos = self.mlp_positions(pos)
        pos_impact = pos.permute(0, 2, 3, 1).reshape(b * n, in_dim, t)
        JnB = JnB * pos_impact + JnB
        JnB = self.tcn_pose(JnB)
        JnB = JnB.view(b, n, -1, t).transpose(-2, -1)
        shuttle = shuttle.transpose(1, 2).contiguous()
        shuttle = self.tcn_shuttle(shuttle)
        shuttle = shuttle.unsqueeze(1).transpose(-2, -1)
        x = torch.cat((JnB, shuttle), dim=1)
        _, n, _, d = x.shape
        class_token_tem = self.learned_token_tem.view(1, 1, -1).expand(b * n, -1, -1)
        x = x.view(b * n, t, d)
        x = torch.cat((class_token_tem, x), dim=1) + self.embedding_tem
        range_t = torch.arange(0, 1 + t, device=x.device).unsqueeze(0).expand(b, -1)
        video_len = video_len.unsqueeze(-1)
        mask = range_t < 1 + video_len
        mask_n = mask.repeat_interleave(n, dim=0)
        x: Tensor = self.pre_dropout(x)
        x = self.encoder_tem(x, mask_n)
        x = x.view(b, n, 1 + t, d)
        p1, p2, shuttle = map(lambda ts: ts.squeeze(1), x.chunk(3, dim=1))
        p1_cls, p2_cls, shuttle_cls = (p1[:, 0].contiguous(), p2[:, 0].contiguous(), shuttle[:, 0].contiguous())
        p1 = p1[:, 1:].contiguous() + self.embedding_cross
        p2 = p2[:, 1:].contiguous() + self.embedding_cross
        shuttle = shuttle[:, 1:].contiguous() + self.embedding_cross
        cross_mask = mask[:, 1:].contiguous()
        p1_shuttle = self.cross_trans(p1, shuttle, cross_mask)
        p2_shuttle = self.cross_trans(p2, shuttle, cross_mask)
        class_token_inter = self.learned_token_inter.view(1, 1, -1).expand(b, -1, -1)
        p1_shuttle = torch.cat((class_token_inter, p1_shuttle), dim=1) + self.embedding_inter
        p2_shuttle = torch.cat((class_token_inter, p2_shuttle), dim=1) + self.embedding_inter
        p1_shuttle: Tensor = self.encoder_inter(p1_shuttle, mask)
        p2_shuttle: Tensor = self.encoder_inter(p2_shuttle, mask)
        p1_shuttle_cls = p1_shuttle[:, 0, :].contiguous()
        p2_shuttle_cls = p2_shuttle[:, 0, :].contiguous()
        p1_shuttle_sim = self.cos_sim(p1_shuttle_cls, shuttle_cls)
        p2_shuttle_sim = self.cos_sim(p2_shuttle_cls, shuttle_cls)
        alpha: Tensor = (p1_shuttle_sim - p2_shuttle_sim + 2) / 4
        alpha = alpha.unsqueeze(1)
        p1_conclusion = p1_cls + p1_shuttle_cls
        p2_conclusion = p2_cls + p2_shuttle_cls
        p1_conclusion = alpha * p1_conclusion
        p2_conclusion = (1 - alpha) * p2_conclusion
        info_need_clean = torch.minimum(p1_shuttle_cls, p2_shuttle_cls)
        dirt = self.mlp_clean(info_need_clean)
        shuttle_cls = shuttle_cls - dirt
        x = torch.cat((p1_conclusion, p2_conclusion, shuttle_cls), dim=1)
        x = self.mlp_head(x)
        return x
