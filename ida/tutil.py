from idaapi import *
import idc
import putil

ADD_TYPE = putil.enum(KEEP = False, ENSURE_UNIQUE = True, REPLACE = 2)

def exists(name):
  return idc.get_struc_id (name) != BADADDR

def _add_type (name, decl, attr, pre, post, mode):
  if exists(name):
    if mode == ADD_TYPE.ENSURE_UNIQUE:
      raise RuntimeError ("struct %s already exists" % (name))
    elif mode == ADD_TYPE.REPLACE:
      print ("## replaced existing", name)
    elif mode == ADD_TYPE.KEEP:
      print ("## kept existing", name)
      return name
  if decl != '':
    decl = '{' + decl + '}'
  idc_parse_types ("{pre}\nstruct {attr} {name} {decl};\n{post}"
                   .format(pre=pre, name=name, attr=attr, decl=decl, post=post), 0)
  idc.import_type (-1, name)
  print ("## declared", name)
  return name

def add_packed_type (name, decl, mode = ADD_TYPE.KEEP):
  return _add_type (name,
                    decl,
                    '',
                    '#pragma pack (push, 1)',
                    '#pragma pack (pop, 1)',
                    mode)

def add_unpacked_type (name, decl, mode = ADD_TYPE.KEEP, alignment = None):
  return _add_type (name,
                    decl,
                    '' if not alignment else '__declspec(align({})) '.format(alignment),
                    '',
                    '',
                    mode)

def maybe_make_dummy_type (name):
  return _add_type (name,
                    '',
                    '',
                    '',
                    '',
                    ADD_TYPE.KEEP)

def maybe_make_dummy_type_with_known_size (name, size):
  return _add_type (name,
                    'char dummy[{}];'.format(size),
                    '',
                    '',
                    '',
                    ADD_TYPE.KEEP)

def create_template_and_make_name (template, parameters, unique = False):
  template.create_types (parameters, unique)
  return template.make_name (parameters)
def maybe_make_templated_type (name, parameters):
  return create_template_and_make_name(template_description.template(name), parameters, False)
def make_templated_type (name, parameters):
  return create_template_and_make_name(template_description.template(name), parameters, True)

class template_description (object):
  def __init__ (self, name, parameters):
    object.__init__ (self)
    self.name = name
    self.parameters = parameters
  def parameter_count (self):
    return len (self.parameters)
  def parameter_name (self, index):
    return self.parameters[index]

  def make_name (self, parameter_names, name_override = ""):
    assert len (parameter_names) == self.parameter_count()
    name = ""
    if name_override == "":
      name = self.name
    else:
      name = name_override
    for parameter in parameter_names:
      name += "$" + parameter.replace (" const*", "_cptr").replace (" *", "_ptr").replace ("*", "_ptr").replace (" ", "_")
    return name

  @classmethod
  def templates(cls):
    return [subcls.__name__ for subcls in cls.__subclasses__()]
  @classmethod
  def template(cls, name):
    for subcls in cls.__subclasses__():
      if subcls.__name__ == name:
        return subcls()
    return None

def integral_for_bytes (bytes):
  known = {1: '__int8', 2: '__int16', 4: '__int32', 8: '__int64', 16: '__int128'}
  return known[bytes]

## todo: better abstraction? do them as plain blobs for now...
## class Function:
##   def __init__ (self, name = None, ret = None, args = None):
##     self.name = name
##     self.ret = ret
##     self.args = args
##   def as_field (self, fallback_name = None):
##     name = self.name or fallback_name
##     if not name:
##       raise Exception ('function.as_field without name and fallback name')
##     if not self.ret and not self.args:
##       return '_UNKNOWN* %s' % (name)
##     elif self.ret and self.args:
##       return '%s (__fastcall* %s) (%s)' % (ret, name, args)
##     else:
##       raise Exception ('function.as_field with either ret but not args or the other way around')
##
## def make_vtable (type, functions):
##   funs = ''
##   i = 0
##   for fun in functions:
##     funs += fun.as_field ('fun_%s;' % (i))
##     i += 1
##   add_packed_type ('vtable$%s' % (type), funs)
