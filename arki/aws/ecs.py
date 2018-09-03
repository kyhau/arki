import boto3
import click
import json
import logging
import sys
from arki.configs import create_ini_template, read_configs
from arki import init_logging


DEFAULT_CONFIGS = {
    "aws.profile": {"required": True},
}


def list_task_definitions(family_name):
    client = boto3.client("ecs")
    if family_name is None:
        resp = client.list_task_definitions(status="ACTIVE", sort="DESC")
    else:
        resp = client.list_task_definitions(familyPrefix=family_name, status="ACTIVE", sort="DESC")

    print("Task Definition ARNs:")
    print("---------------------")
    cnt = 0
    for arn in resp["taskDefinitionArns"]:
        print(f"{cnt}: {arn}")
        cnt += 1


def task_definition(arn):
    client = boto3.client("ecs")
    resp = client.describe_task_definition(taskDefinition=arn)
    print(json.dumps(resp["taskDefinition"], sort_keys=True, indent=2))


@click.command()
@click.argument("ini_file", required=False)
@click.option("--init", "-i", is_flag=True, help="Set up new configuration")
@click.option("--family", "-f", required=False, help="Filtered by family name (ake task definition name")
@click.option("--detail", "-d", required=False, help="ARN of the task definition to show more details")
def main(ini_file, init, family, detail):
    """
    ECS

    Use --init to create a `ini_file` with the default template to start.
    """

    try:
        init_logging()

        if init:
            create_ini_template(
                ini_file=ini_file,
                module=__file__,
                config_dict=DEFAULT_CONFIGS,
                allow_overriding_default=True
            )

        else:
            if ini_file:
                settings = read_configs(ini_file=ini_file, config_dict=DEFAULT_CONFIGS)
                boto3.setup_default_session(profile_name=settings["aws.profile"])

            if detail:
                task_definition(arn=detail)
            else:
                list_task_definitions(family_name=family)

    except Exception as e:
        logging.error(e)
        sys.exit(1)

    sys.exit(0)