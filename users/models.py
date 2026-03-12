from django.contrib.auth.models import User

def is_admin_or_editor(self):
    return self.groups.filter(name__in=['root', 'editor']).exists()

User.add_to_class('is_admin_or_editor', is_admin_or_editor)