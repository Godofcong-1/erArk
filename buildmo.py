import os

po_dir = os.path.join("data", "po", "en_US", "LC_MESSAGES")
po_path = os.path.join(po_dir, "erArk.po")
mo_path = os.path.join(po_dir, "erArk.mo")
os.system("msgfmt " + po_path + " -o " + mo_path)
