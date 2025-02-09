class accountsRouter(object):
    """
    A router to control all database operations on models in
    the accounts application
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read accounts models go to 'default'
        """
        
        if model._meta.app_label == 'accounts':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write accounts models go to 'default'
        """
        
        if model._meta.app_label == 'accounts':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the accounts app is involved.
        """
        if obj1._meta.app_label == 'accounts' or \
           obj2._meta.app_label == 'accounts':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the accounts app only appears on the 'default' db
        """
        if db == 'default':
            return model._meta.app_label == 'accounts'
        elif model._meta.app_label == 'accounts':
            return False
        return None
