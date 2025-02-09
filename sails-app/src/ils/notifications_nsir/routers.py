class notifications_nsirRouter(object):
    """
    A router to control all database operations on models in
    the notifications_nsir application
    """

    def db_for_read(self, model, **hints):
        """
        Point all operations on notifications_nsir models to 'tax1'
        """
        if model._meta.app_label == 'notifications_nsir':
            return 'tax1'
        return None

    def db_for_write(self, model, **hints):
        """
        Point all operations on notifications_nsir models to 'tax1'
        """
        if model._meta.app_label == 'notifications_nsir':
            return 'tax1'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the 'notifications_nsir' app is involved.
        """
        if obj1._meta.app_label == 'notifications_nsir' or \
           obj2._meta.app_label == 'notifications_nsir':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the 'notifications_nsir' app only appears on the 'tax1' db
        """
        if db == 'tax1':
            return model._meta.app_label == 'notifications_nsir'
        elif model._meta.app_label == 'notifications_nsir':
            return False
        return None
