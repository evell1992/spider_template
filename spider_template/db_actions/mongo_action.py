from spider_template.settings import MONGO_URI, MONGO_DB, MONGO_TEMPLATE, MONGO_ORDATA, MONGO_DUPEFILTER, MONGO_FAILED
import pymongo


class MongoAction(object):
    """
    mongo api
    """
    uri = ""
    db_name = ""
    doc_name = {}

    def __init__(self):
        self.client = pymongo.MongoClient(self.uri)
        self.tdb = self.client[self.db_name]
        if isinstance(self.doc_name, dict):
            for k, v in self.doc_name.items():
                setattr(self, k, self.tdb[v])
        else:
            raise Exception("doc_name settings {} is disable.".format(self.doc_name))

    def find(self, table_name, *args, **kwargs):
        return getattr(self, table_name).find(*args, **kwargs)

    def find_one(self, table_name, filter, *args, **kwargs):
        return getattr(self, table_name).find_one(filter, *args, **kwargs)

    def update(self, table_name, spec, document, upsert=False, manipulate=False, multi=False, check_keys=True,
               **kwargs):
        return getattr(self, table_name).update(spec, document, upsert, manipulate, multi, check_keys, **kwargs)

    def update_one(self, table_name, filter, update, upsert=False, bypass_document_validation=False, collation=None,
                   array_filters=None, session=None):
        return getattr(self, table_name).update_one(filter, update, upsert, bypass_document_validation,
                                                    collation, array_filters, session)

    def insert(self, table_name, doc_or_docs, manipulate=True, check_keys=True, continue_on_error=False, **kwargs):
        getattr(self, table_name).insert(doc_or_docs, manipulate, check_keys, continue_on_error, **kwargs)

    def insert_one(self, table_name, document, bypass_document_validation=False, session=None):
        getattr(self, table_name).insert_one(document, bypass_document_validation, session)

    def count(self, table_name, filters=None):
        return getattr(self, table_name).count(filters)

    def save(self, table_name, document):
        getattr(self, table_name).save(document)

    def close(self):
        self.client.close()


class TemplateInfo(MongoAction):
    uri = MONGO_URI
    db_name = MONGO_DB
    doc_name = {
        'template': MONGO_TEMPLATE,
    }


class DupeFilter(MongoAction):
    uri = MONGO_URI
    db_name = MONGO_DB
    doc_name = {
        'dupefilter': MONGO_DUPEFILTER,
    }
