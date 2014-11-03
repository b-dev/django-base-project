from django import template

register = template.Library()

@register.tag(name="dashboard_navigation")
def reception_navigation(parser, token):
    return DashboardNavigationNode()
class DashboardNavigationNode(template.Node):
    def render(self, context):
        from website.nav import get_nodes
        user = context['user']
        try: type = user.type
        except: type = None
        context['nav_items'] = get_nodes(user, type)
        return ''
