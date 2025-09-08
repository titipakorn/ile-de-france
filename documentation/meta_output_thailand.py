import os, datetime, json
import subprocess as sp

def configure(context):
    context.config("output_path")
    context.config("output_prefix", "thailand_")

    for option in ("sampling_rate", "hts", "random_seed"):
        context.config(option)

def get_version():
    version_path = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.realpath("{}/../version.txt".format(version_path))

    with open(version_path) as f:
        return f.read().strip()

def get_commit():
    root_path = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.realpath("{}/..".format(root_path))

    try:
        return sp.check_output(["git", "rev-parse", "HEAD"], cwd = root_path).strip().decode("utf-8")
    except sp.CalledProcessError:
        return "unknown"

def execute(context):
    # Write meta information for Thailand pipeline
    information = dict(
        sampling_rate = context.config("sampling_rate"),
        hts = context.config("hts"),
        random_seed = context.config("random_seed"),
        version = get_version(),
        commit = get_commit(),
        created = datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    output_path = context.config("output_path")
    output_prefix = context.config("output_prefix")

    with open("%s/%smeta.json" % (output_path, output_prefix), "w+") as f:
        json.dump(information, f, indent = 2)

    return information
