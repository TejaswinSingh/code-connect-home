#_____________________________________________________________________________________________________
""" 
    - defines urls inside the `home` app.
"""

__author__ = "Tejaswin Singh, "
__copyright__ = "Copyright 2024, Code Connect Home"
__credits__ = ["Tejaswin Singh", "", ]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Tejaswin Singh"
__email__ = "tejaswin.cs08@gmail.com"
__status__ = "Development"

#______________________________________________imports_________________________________________________


from django.urls import path
from . import views


#______________________________________________urls____________________________________________________

app_name = "home"

urlpatterns = [
	path("", views.index, name="index"),
]
