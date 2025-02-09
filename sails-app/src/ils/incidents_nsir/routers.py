class tax1Router(object):
    """
    A router to control all database operations on models in
    the incidents_nsir application
    """

    def db_for_read(self, model, **hints):
        """
        Point all operations on incidents_nsir models to 'tax1'
        """
        if model._meta.app_label == 'incidents_nsir':
            return 'tax1'
        return None

    def db_for_write(self, model, **hints):
        """
        Point all operations on incidents_nsir models to 'tax1'
        """
        if model._meta.app_label == 'incidents_nsir':
            return 'tax1'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the 'incidents_nsir' app is involved.
        """
        if obj1._meta.app_label == 'incidents_nsir' or \
           obj2._meta.app_label == 'accounts':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the 'incidents_nsir' app only appears on the 'tax1' db
        """
        if db == 'tax1':
            return model._meta.app_label == 'incidents_nsir'
        elif model._meta.app_label == 'incidents_nsir':
            return False
        return None
