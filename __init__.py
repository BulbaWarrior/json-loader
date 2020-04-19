"""
PyMOL plugin for loading JSON files


Arguments:

File name - path to the file to be loaded.

Object - the name of the object to be loaded.

State(>= 0) - the number of state to start loading files to, i.e if 3 is passed
and 4 files are chosen, they will be loaded to states 3, 4, 5, and 6.
If 0 is passed the file will be loaded to the first unoccupied state.
"""

import os
from pymol import cmd


def __init_plugin__(app=None):
    # older versions of PyMOL do not support Qt
    # and should use Tkinter instead
    try:
        from pymol.plugins import addmenuitemqt
        addmenuitemqt('JSON file loader', run_gui_qt)
    except ImportError:
        app.menuBar.addmenuitem(
            'Plugin', 'command',
            label='JSON file loader',
            command=lambda: run_gui_tkinter(app.root))

    cmd.extend(load_json)


def run_gui_tkinter(parent):
    import Tkinter as tk

    window = tk.Tk()
    window.title('JSON loader')
    window.minsize(630, 80)

    f_top = tk.Frame(window)
    f_center = tk.Frame(window)
    f_bottom = tk.Frame(window)

    f_top.pack(fill=tk.X, expand=1)
    f_center.pack(fill=tk.X, expand=1)
    f_bottom.pack(fill=tk.BOTH, expand=1)

    input_filename = tk.Entry(f_top, width=50)
    input_filename.pack(side=tk.LEFT, fill=tk.X, expand=1)

    label_state = tk.Label(f_center, text='State:')
    label_object = tk.Label(f_center, text='Object:')


    # for reasons unknown Tkinter variables
    # don't seem to work properly with pymol
    def switch(parent):
        parent.obj_check = not parent.obj_check
        if parent.obj_check:
            input_object.config(state=tk.NORMAL)
        else:
            input_object.config(state=tk.DISABLED)
    window.obj_check = True
    checkbox_object = tk.Checkbutton(f_center, text='as single object',
                                     command=lambda: switch(window))
    checkbox_object.select()




    def check(P): # a filter to only allow digits
        if str.isdigit(P) or P =='':
            return True
        else:
            return False

    vcmd = (window.register(check))
    input_state = tk.Entry(f_center, validate='all',
                           validatecommand=(vcmd, '%P'), width=10)


    input_object = tk.Entry(f_center, width=40)

    label_state.pack(side=tk.LEFT)
    input_state.pack(side=tk.LEFT, fill=tk.X, expand=1)
    label_object.pack(side=tk.LEFT)
    input_object.pack(side=tk.LEFT, fill=tk.X, expand=1)
    checkbox_object.pack(side=tk.LEFT, fill=tk.X)

    def set_text(entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    window.filenames = ()

    def browse_files():
        from tkFileDialog import askopenfilenames
        window.filenames = askopenfilenames(
            title='select files',
            filetypes=(('JSON fies', '*.json'), ('All files', '*.*')))
        if window.filenames:
            set_text(input_filename, str(window.filenames))
            set_text(input_state, '0')
            obj_name = os.path.basename(window.filenames[0]).rsplit('.', 1)[0]
            set_text(input_object, obj_name)
        window.lift()

    def load_from_gui_tk():


        if window.filenames and input_state.get():

            state = int(input_state.get())
            obj_name = ''
            if window.obj_check:
                obj_name = input_object.get()
                if not obj_name:
                    obj_name = os.path.basename(window.filenames[0]).rsplit('.',1)[0]
            for fn in window.filenames:
                load_json(fn, obj_name, state)
                if state > 0 and window.obj_check:
                    state += 1
            # if flag:
            #     # print(input_object.get())
            #     # obj_name = input_object.get()
            #     for fn in window.filenames:
            #         load_json(fn, 'molec', state)
            #         if state > 0:
            #             state += 1

            # else:
            #     for fn in window.filenames:
            #         load_json(fn, state=state)
                # print(fn)


        else:
            return

        window.destroy()

    button_browse = tk.Button(f_top, text='Browse', command=browse_files)
    button_browse.pack(side=tk.LEFT, fill=tk.X, expand=1)
    button_load = tk.Button(f_bottom, text='Load', command=load_from_gui_tk)
    # button_close = tk.Button(f_bottom, text='Close', command=window.destroy)
    button_load.pack(fill=tk.BOTH, expand=1)
    # button_close.pack(side=tk.LEFT)

    window.mainloop()


def run_gui_qt():
    from pymol.Qt import QtWidgets
    from pymol.Qt.utils import loadUi

    # create new Window
    dialog = QtWidgets.QDialog()

    uifile = os.path.join(os.path.dirname(__file__), 'form.ui')
    form = loadUi(uifile, dialog)

    def browse_file():
        form.filenames, extension_filter = QtWidgets.QFileDialog.getOpenFileNames(
            dialog, 'Open', filter='JSON file (*.json)')

        if form.filenames:
            form.input_filename.setText(str(form.filenames))
            form.input_state.setText('0')
            obj_name = os.path.basename(form.filenames[0]).rsplit('.', 1)[0]
            form.input_object.setText(obj_name)

    form.browse_button.clicked.connect(browse_file)
    form.close_button.clicked.connect(dialog.close)
    form.input_filename.setReadOnly(True)

    @form.load_button.clicked.connect
    def load_from_gui_qt():
        state = int(form.input_state.text())
        obj_name = form.input_object.text()

        for fn in form.filenames:
            load_json(fn, obj_name, state)
            if state:
                state += 1
        dialog.close()

    dialog.show()


def gen_model(mol):
    from chempy import models
    from chempy import Atom
    from chempy import Bond
    # print('generating model')
    model = models.Indexed()
    i = 1
    for at in mol['atoms']:
        atom = Atom()
        atom.name = at['name']
        atom.resi = at['residue']
        atom.resi_number = int(at['residue'])
        atom.segi = at['segment']
        atom.symbol = at['element']
        atom.coord = [float(at["x"]),
                      float(at["y"]),
                      float(at["z"])]
        model.add_atom(atom)
        # model.update_index()

    # model.update_index()
    for b in mol['bonds']:
        bond = Bond()
        bond.index = [int(b['atom1'])-1, int(b['atom2'])-1]
        model.add_bond(bond)
    return model


# creating a new command for PyMOL command line
# @cmd.extend
def load_json(file_name, object='', state=0):
    from json import load
    # print('loading ' + file_name)

    if state < -1:
        print('incorrect state')
        return

    with open(file_name, 'r') as fp:
        try:
            molecule = load(fp)
            model = gen_model(molecule)

        except ValueError:
            print('the file seems to be not of JSON type')

        except LookupError:
            print('the file is formatted incorrectly')

        except Exception as e:
            print(str(e.__class__) + ' while creating model')

        if object:
            object_name = object
        else:
            object_name = os.path.basename(file_name).rsplit('.', 1)[0]  # names may have dots

        cmd.load_model(model, object_name, state)
