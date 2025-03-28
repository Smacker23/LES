
# execfile(activate_this, dict(__file__=activate_this))


import os
import sys
import site
from django.core.wsgi import get_wsgi_application

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Users/pventura/Envs/grupo1_6/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/inetpub/wwwroot/DAUALG/grupo1_6')
sys.path.append('C:/inetpub/wwwroot/DAUALG/grupo1_6/dia_aberto')

os.environ['DJANGO_SETTINGS_MODULE'] = 'dia_aberto.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dia_aberto.settings")

application = get_wsgi_application()
