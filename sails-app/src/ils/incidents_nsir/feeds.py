class DictModelAdaptor():
    """Forget what this was included for, no longer appears to be used.
    """
    def __init__(self,model):
        self.model = model

    def getitem(self,key):
        return self.model.objects.get(key=key)

    def __setitem__(self,key,item):
        pair = self.model()
        pair.key = key
        pair.value = item
        pair.save()
