import json

import click

from ckanext.saml import helpers


@click.group()
def saml():
    pass


@saml.command()
def show_config():
    click.secho(json.dumps(helpers._parse_settings(), indent=4), fg="green")


@saml.command()
def show_mapping():
    click.secho(json.dumps(helpers.saml_get_attribute_mapper(), indent=4), fg="green")


def get_commands():
    return [saml]
