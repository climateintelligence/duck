from pathlib import Path
from zipfile import ZipFile
import os

from pywps import Process
from pywps import LiteralInput, ComplexInput, ComplexOutput
from pywps import FORMATS, Format
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

import craimodels
from duck import clintai
import xarray as xr

import logging
LOGGER = logging.getLogger("PYWPS")

FORMAT_PNG = Format("image/png", extension=".png", encoding="base64")

MEDIA_ROLE = "http://www.opengis.net/spec/wps/2.0/def/process/description/media"

models_list = list(craimodels.info_models().keys())


class ClintAI(Process):
    def __init__(self):
        inputs = [
            LiteralInput('dataset_name', 'Dataset name', data_type='string',
                         abstract='Choose the type of dataset to be infilled.',
                         allowed_values=models_list,
                         default=models_list[0]),
            ComplexInput('file', 'Add your NetCDF file with missing values here',
                         abstract="Enter a URL pointing to a NetCDF file with missing values.",
                         min_occurs=1,
                         max_occurs=1,
                         default="https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc", # noqa
                         supported_formats=[FORMATS.NETCDF, FORMATS.ZIP]),
            LiteralInput('variable_name', 'Variable name', data_type='string',
                         abstract='Enter here the variable name to be infilled.',
                         default='tas_mean'),
        ]
        outputs = [
            ComplexOutput('output', 'Reconstructed dataset',
                          abstract='NetCDF output produced by CRAI.',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            ComplexOutput('plot', 'Preview of the first time step',
                          # abstract='Plot of original input file. First timestep.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
        ]

        super(ClintAI, self).__init__(
            self._handler,
            identifier="crai",
            title="CRAI",
            version="0.1.0",
            abstract="AI-enhanced climate service to infill missing values in climate datasets.",
            metadata=[
                Metadata(
                    title="CRAI Logo",
                    href="https://github.com/FREVA-CLINT/duck/raw/main/docs/source/_static/crai_logo.png",
                    role=MEDIA_ROLE),
                Metadata('CRAI', 'https://github.com/FREVA-CLINT/climatereconstructionAI'),
                Metadata('Clint Project', 'https://climateintelligence.eu/'),
                Metadata('HadCRUT on Wikipedia', 'https://en.wikipedia.org/wiki/HadCRUT'),
                Metadata('HadCRUT4', 'https://www.metoffice.gov.uk/hadobs/hadcrut4/'),
                Metadata('HadCRUT5', 'https://www.metoffice.gov.uk/hadobs/hadcrut5/'),
                Metadata('Near Surface Air Temperature',
                         'https://www.atlas.impact2c.eu/en/climate/temperature/?parent_id=22'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        dataset_name = request.inputs['dataset_name'][0].data
        file = request.inputs['file'][0].file
        variable_name = request.inputs['variable_name'][0].data

        response.update_status('Prepare dataset ...', 0)
        workdir = Path(self.workdir)

        zipfile = False
        if Path(file).suffix == ".zip":
            with ZipFile(file, 'r') as zip:
                print("extraction zip file", workdir)
                zip.extractall(workdir.as_posix())
                zipfile = True

        try:
            datasets = sorted(workdir.rglob('*.nc'), key=os.path.getmtime)
        except Exception:
            raise ProcessError("Could not extract netcdf file.")

        ndata = len(datasets)
        if ndata == 0:
            raise ProcessError("Could not find netcdf files.")

        istep = 100 / ndata
        i = 0
        for dataset in datasets:

            ds = xr.open_dataset(dataset)

            vars = list(ds.keys())
            if variable_name not in vars:
                raise ProcessError("Could not find variable {} in {}.".format(variable_name, dataset))

            try:
                clintai.run(
                    dataset,
                    dataset_name=dataset_name,
                    variable_name=variable_name,
                    outdir=workdir,
                    update_status=[response.update_status, i, istep])
            except Exception as e:
                raise ProcessError(str(e))

            i += 1

        if zipfile:
            outfile = ".".join(file.split(".")[:-1]) + "_infilled.zip"
            outfile = workdir / "outputs" / outfile
            infiles = sorted((workdir / "outputs").rglob('*_infilled.nc'), key=os.path.getmtime)

            with ZipFile(outfile, 'w') as zip:
                for infile in infiles:
                    zip.write(infile, arcname=infile.as_posix().split("/")[-1])
        else:
            outfile = workdir / "outputs" / str(datasets[0].stem+"_infilled.nc")

        response.outputs["output"].file = outfile
        response.outputs["plot"].file = workdir / "outputs" / str(datasets[0].stem+"_combined.1_0.png")

        response.update_status('done.', 100)
        return response
