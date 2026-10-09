from jinja2 import Template
import shutil

import craimodels
from climatereconstructionai import evaluate
import logging

LOGGER = logging.getLogger("PYWPS")

info_models = craimodels.info_models()
dataset_names = list(info_models.keys())


def write_clintai_cfg(
    base_dir, model_dir, eval_name, data_name, data_type, eval_parameters
):
    cfg_templ = """
    --data-root-dir {{ base_dir }}
    --log-dir {{ base_dir }}
    --mask-dir {{ base_dir }}/outputs
    --model-dir {{ model_dir }}
    --evaluation-dirs {{ base_dir }}/outputs
    --eval-names {{ eval_name }}
    --data-names {{ data_name }}
    --data-types {{ data_type }}
    --maxmem 5000
    --device cpu
    --plot-results 0
    {{ eval_parameters }}
    """
    cfg = Template(cfg_templ).render(
        base_dir=base_dir,
        model_dir=model_dir,
        eval_name=eval_name,
        data_name=data_name,
        data_type=data_type,
        eval_parameters=eval_parameters,
    )
    out = base_dir / "clintai.cfg"
    with open(out, "w") as fp:
        fp.write(cfg)
    return out


def run(dataset, dataset_name, variable_name, outdir, update_status):
    # data_type = info_models[dataset_name]["variable-name"]
    (outdir / "masks").mkdir(exist_ok=True)
    (outdir / "outputs").mkdir(exist_ok=True)
    input_dir = outdir / "test"
    input_dir.mkdir(exist_ok=True)
    shutil.move(dataset.as_posix(), input_dir.as_posix())
    # print(f"dataset={dataset}")
    cfg_file = write_clintai_cfg(
        base_dir=outdir,
        model_dir=craimodels.model_dir(),
        eval_name=dataset.stem,
        data_name=dataset.name,
        data_type=variable_name,
        eval_parameters=info_models[dataset_name]["eval_parameters"],
    )
    # print(f"written cfg {cfg_file}")
    try:
        evaluate(arg_file=cfg_file.as_posix(), prog_func=update_status)

    except Exception as e:
        raise Exception(e)

    except SystemExit:
        raise Exception("CRAI exited with an error.")
