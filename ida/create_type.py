import gutil
import tutil
import ida_kernwin
import idc

def main():
  chosen_template = gutil.choose_one ('Template class', tutil.template_description.templates())
  if not chosen_template:
    return
  template = tutil.template_description.template (chosen_template)

  name_pref = chosen_template + '$'

  parameters = []
  for parameter in range (0, template.parameter_count()):
    ch_struct = ida_kernwin.choose_struct('Choose ' + name_pref + template.parameter_name (parameter))
    if not ch_struct:
      p = AskStr ("", template.parameter_name (parameter))
      if not p:
        return
      param = p
    else:
      param = idc.get_struc_name(ch_struct.id)
    parameters.append (param)
    name_pref += '$' + param

  template.create_types (parameters)
main()
