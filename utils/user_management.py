import click
from passlib.hash import sha256_crypt
import redis

@click.group()
@click.option('--host', default="localhost") #"'172.22.54.5')
@click.option('--port', default='6379')
@click.pass_context
def cli(ctx, host, port):
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['port'] = port


@cli.command()
@click.pass_context
@click.argument('username')
def delete_user(ctx, username):
    host = ctx.obj.get('host')
    port = ctx.obj.get('port')
    rdb = redis.StrictRedis(host=host, port=port)
    user_exists = rdb.hexists('users', username)
    if not user_exists:
        click.echo('User "{}" does not exist, so cannot be deleted'.format(username))
        exit(1)
    # else
    rdb.hdel('users', username)
    click.echo('User "{}" successfully deleted'.format(username))


@cli.command()
@click.pass_context
def create_user(ctx):
    import getpass
    host = ctx.obj.get('host')
    port = ctx.obj.get('port')
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    repeat_password = getpass.getpass("Repeat password: ")
    if password == repeat_password:
        encrypted_password = sha256_crypt.hash(password)
        rdb = redis.StrictRedis(host=host, port=port)
        user_exists = rdb.hexists('users', username)
        if user_exists:
            click.echo('User "{}" already exists'.format(username))
            exit(1)
        # hash set = 'users', key1 = username, key2 = 'password', value2 = password
        rdb.hmset('users', {username: encrypted_password})
        click.echo('User "{}" successfully created'.format(username))
    else:
        print("Passwords don't match!")
    exit(0)

if __name__ == '__main__':
    cli(obj={})

# todo: reset password
# todo: create users from file
