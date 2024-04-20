#_____________________________________________________________________________________________________
""" 
    - defines views inside the `home` app.
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

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


#______________________________________________views___________________________________________________

def index(request: HttpRequest) -> HttpResponse:
	return render(request, "home/index.html")
