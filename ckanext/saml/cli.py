import click

from ckanext.saml.model.saml2_user import (
    setupdb, dropdb
    )


def get_commnads():
    return [
    saml
    ]

@click.group()
def saml():
    pass

@saml.command('init-db')
def init_db():
    """Initialize table"""
    setupdb()
    click.secho('Done', fg='green')

@saml.command('drop-db')
def drop_db():
    """Drops table"""
    dropdb()
    click.secho('Done', fg='green')