_RUSTFMT = true

ui.set_theme('dark', {fontsize = 15, font = 'DejaVu Sans Mono'})
textadept.file_types.extensions.toml = 'toml'

keys['cpgup'] = {view.goto_buffer, view, -1, true}
keys['cpgdn'] = {view.goto_buffer, view, 1, true}
