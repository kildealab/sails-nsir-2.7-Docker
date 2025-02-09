from django import template

register = template.Library()

#-----------------------------------------------------------------------------------------
# Convert the label associated with the current field to separated by underscores instead
# of white space. Assign resulting string to the context, so can be accessed in template.
#-----------------------------------------------------------------------------------------
def get_label_key(parser,token):
    tag_name, my_label = token.split_contents()
    return LabelNode(my_label)

class LabelNode(template.Node):
    def __init__(self, my_label):
        self.my_label = template.Variable(my_label)
    def render(self, context):
        actual_label = self.my_label.resolve(context)
        context['label_key'] = actual_label.replace(" ", "_").lower()
        return ''

#-----------------------------------------------------------------------------------------
# Pass in the reference dictionary containing ForeignKey fields containing options which
# have distinct help texts. Also pass in the label_key which is simply the label of the
# associated field, but with underscores intead of white space. Use this key with the
# reference dictionary to identify the specific field, in particular, the instances of
# the object associated with that field. Assign list of these instances to a context
# variable to be used in the template.
#-----------------------------------------------------------------------------------------
def get_help_text(parser, token):
    tag_name, var_name, label_key = token.split_contents()
    return HelpNode(var_name, label_key)

class HelpNode(template.Node):
    def __init__(self, var_name, label_key):
        self.var_name = template.Variable(var_name)
        self.label_key = template.Variable(label_key)
    def render(self, context):
        ref_dictionary = self.var_name.resolve(context)
        actual_label_key = self.label_key.resolve(context)
        context['myinstances'] = ref_dictionary[actual_label_key]
        return ''

#-----------------------------------------------------------------------------------------
# Determine if the field passed as an argument to this template tag uses a "Select" widget
# for example as ForeignKey fields do. Assign the resulting Boolean to a context variable
# that can be accessed within the template.
#-----------------------------------------------------------------------------------------
def is_foreignkey(parser, token):
    tag_name, my_field = token.split_contents()
    return ForeignKeyNode(my_field)

class ForeignKeyNode(template.Node):
    def __init__(self, my_field):
        self.my_field = template.Variable(my_field)
    def render(self, context):
        test_field = self.my_field.resolve(context)
        field_type = test_field.field.widget.__class__.__name__
        if field_type == "Select":
            context['isForeignKey'] = True
        else:
            context['isForeignKey'] = False
        return ''

#-----------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------
@register.simple_tag
def get_verbose_field_name(instance,field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()

register.tag('is_foreignkey', is_foreignkey)
register.tag('get_label_key', get_label_key)
register.tag('get_help_text', get_help_text)
