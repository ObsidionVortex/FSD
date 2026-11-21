# Python 3.14 compatibility patch for Django 4.2 BaseContext.__copy__
try:
    from django.template import context as _d_context

    def _py314_basecontext_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _d_context.BaseContext.__copy__ = _py314_basecontext_copy
except Exception:
    pass
