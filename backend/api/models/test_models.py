from django.db import models
from pyorient.ogm.property import Integer

from api.models.orientdb_engine import Node, Relationship, graph


class Company(models.Model):
    name = models.CharField(max_length=500)
    email = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # def __get_company_information__(self):
    #     return '%s %s' % (self.name, self.email).filter(is_active=True, is_deleted=False)
    #
    # company_information = property(__get_company_information__)


class OUsers(Node):
    element_plural = 'ousers'
    postgresql_id = Integer(nullable=False, unique=True)


class OCompany(Node):
    element_plural = 'ocompany'
    postgresql_id = Integer(nullable=False, unique=True)


class OFriends(Relationship):
    label = 'ofriends'
    from_postgresql_ouser_id = Integer(nullable=False, unique=True)
    to_postgresql_ouser_id = Integer(nullable=False, unique=True)


class OWorksAt(Relationship):
    label = 'oworksat'
    from_postgresql_ouser_id = Integer(nullable=False, unique=True)
    to_postgresql_ocompany_id = Integer(nullable=False, unique=True)


# graph.create_all(Node.registry)
# graph.create_all(Relationship.registry)
