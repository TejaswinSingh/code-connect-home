#_____________________________________________________________________________________________________
""" 
    - configures the models showed under the Home section on the admin-site.
"""

__author__ = "Tejaswin Singh, "
__copyright__ = "Copyright 2024, Code Connect Home"
__credits__ = ["Tejaswin Singh", "", ]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Tejaswin Singh"
__email__ = "tejaswin.cs08@gmail.com"
__status__ = "Development"

#_____________________________________________________________________________________________________


from django.contrib import admin

from home.models import SendInviteTask, Task

admin.site.register(Task)
admin.site.register(SendInviteTask)