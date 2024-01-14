import os, sys
PWD = os.getenv('\STARTUP')

PROJ_MISSING_MSG = """Set an enviroment variable:\n
`DJANGO_PROJECT=STARTUP`\n
or call:\n
`init_django(STARTUP)`
"""

def init_django(STARTUP=None):
    os.chdir("STARTUP")
    STARTUP = STARTUP or os.environ.get('DJANGO_PROJECT') or None
    if PWD == None:
        raise Exception(PROJ_MISSING_MSG)
    sys.path.insert(0, os.getenv('PWD'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'STARTUP.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    import django
    django.setup()
