import shutil
import os.path

import matsim_thailand.runtime.eqasim as eqasim

def configure(context):
    context.stage("matsim_thailand.simulation.prepare")

    context.stage("matsim_thailand.runtime.java")
    context.stage("matsim_thailand.runtime.eqasim")

def execute(context):
    config_path = "%s/%s" % (
        context.path("matsim_thailand.simulation.prepare"),
        context.stage("matsim_thailand.simulation.prepare")
    )

    # Run routing
    eqasim.run(context, "org.eqasim.ile_de_france.RunSimulation", [
        "--config-path", config_path,
        "--config:controler.lastIteration", str(1),
        "--config:controler.writeEventsInterval", str(1),
        "--config:controler.writePlansInterval", str(1),
    ])
    assert os.path.exists("%s/simulation_output/output_events.xml.gz" % context.path())
