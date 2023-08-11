from rest_framework import routers


class UserRouter(routers.SimpleRouter):
    routes = [
        routers.Route(
            url=r'^{prefix}/register$',
            mapping={'post': 'create'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        routers.Route(
            url=r'^{prefix}/profile$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Detail'}
        ),
    ]


