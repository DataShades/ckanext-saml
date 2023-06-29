import json

import click

from ckanext.saml import config, helpers


@click.group()
def saml():
    pass


@saml.command()
def show_config():
    settings = (
        helpers._parse_file_settings()
        if config.get_folder_path()
        else helpers._parse_dynamic_settings()
    )

    click.secho(json.dumps(settings, indent=4), fg="yellow")


@saml.command()
def show_mapping():
    click.secho(json.dumps(helpers.saml_get_attribute_mapper(), indent=4), fg="yellow")


def get_commands():
    return [saml]
