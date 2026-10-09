"""Smoke tests for the CRAI inference and NetCDF dependency stack."""

import craimodels
import numpy as np
import torch
import xarray as xr

from climatereconstructionai import config as cfg
from climatereconstructionai.model.net import CRAINet
from climatereconstructionai.utils.io import load_ckpt, load_model
from duck.clintai import write_clintai_cfg


def test_pretrained_model_cpu_inference(tmp_path):
    info = craimodels.info_models()["HadCRUT5"]
    config = write_clintai_cfg(
        tmp_path, craimodels.model_dir(), "smoke", "smoke.nc", "tas_mean",
        info["eval_parameters"],
    )
    cfg.set_evaluate_args(str(config))
    model = CRAINet(
        img_size=(36, 72), enc_dec_layers=cfg.encoding_layers[0],
        pool_layers=cfg.pooling_layers[0], in_channels=cfg.n_channel_steps,
        out_channels=cfg.out_channels, bounds=np.array([[-np.inf, np.inf]]),
    )
    checkpoint = load_ckpt(craimodels.model_dir() / cfg.model_names[0], "cpu")
    load_model(checkpoint, model)
    model.eval()
    values = torch.ones(1, 1, 1, 36, 72)
    mask = torch.ones_like(values)
    mask[..., 10:15, 20:25] = 0
    with torch.no_grad():
        result = model(values * mask, mask)
    assert result.shape == values.shape
    assert torch.isfinite(result).all()


def test_netcdf_roundtrip(tmp_path):
    dataset = xr.Dataset({
        "tas_mean": (("time", "latitude", "longitude"),
                     np.array([[[1.0, np.nan], [2.0, 3.0]]], dtype="float32")),
    })
    path = tmp_path / "smoke.nc"
    dataset.to_netcdf(path, engine="netcdf4")
    with xr.open_dataset(path, engine="netcdf4", chunks={"time": 1}) as restored:
        xr.testing.assert_equal(dataset, restored)
