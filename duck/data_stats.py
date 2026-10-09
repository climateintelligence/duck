import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import yaml
import pathlib
import io
import base64


def get_stats(data):
    return {
        "min": float(np.nanmin(data)),
        "max": float(np.nanmax(data)),
        "mean": float(np.nanmean(data)),
        "std": float(np.nanstd(data)),
    }


class DataStats(object):
    def __init__(self, output_dir):
        if isinstance(output_dir, pathlib.Path):
            self.output_dir = output_dir
        else:
            self.output_dir = pathlib.Path(output_dir)
        self.info = None
        self.histogram = None

    def gen_data_stats(self, filename, var, nbins=100):
        ds = xr.open_dataset(filename)

        vstats = get_stats(ds[var].values)
        bins = np.linspace(vstats["min"], vstats["max"], num=nbins + 1)

        ntime, nlon, nlat = ds[var].shape
        mratio = np.zeros(ntime)
        hist = np.zeros((ntime, nbins))
        for i in range(ntime):
            a = ds[var].values[i]
            idx = ~np.isnan(a)
            mratio[i] = idx.sum()
            a = np.histogram(a[idx], bins=bins)[0]
            hist[i] = a / max(a)

        mratio = 1 - mratio / (nlon * nlat)

        # TODO: It would be great to store the distribution graph in a database
        if True:
            plt.close()
            plt.imshow(
                hist,
                aspect="auto",
                origin="lower",
                extent=[vstats["min"], vstats["max"], 0, ntime],
                cmap="gist_ncar",
            )
            ax = plt.gca()
            ax.grid(color="gray", linestyle="-.", linewidth=1)
            plt.xlabel(var)
            plt.ylabel("Timesteps")
            # outfile = self.output_dir / "histogram.png"
            # print(f"histogram: {outfile}")
            # plt.savefig(outfile.as_posix(), dpi=50)
            # store as base64
            # Save the plot to a BytesIO object
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            # Encode the BytesIO object as base64
            base64_encoded_plot = base64.b64encode(buffer.read()).decode("utf-8")
            # print(f"{base64_encoded_plot}")
            self.histogram = base64_encoded_plot
            # close plot
            plt.close()

        # The following information should be stored in a database
        attrs = {}
        orig_attrs = dict(ds.attrs)
        for key in orig_attrs:
            value = orig_attrs[key]
            if isinstance(value, str):
                attrs[key] = value

        self.info = {}
        self.info["Attrs"] = attrs
        self.info["Dims"] = dict(ds.dims)
        self.info["Vars"] = list(dict(ds.variables).keys())
        self.info["Vstats"] = vstats
        self.info["Mstats"] = get_stats(mratio)
        # print(self.info)

    def write_json(self):
        outfile = self.output_dir / "info.txt"
        with open(outfile.as_posix(), "w") as f:
            yaml.dump(self.info, f)
        return outfile
