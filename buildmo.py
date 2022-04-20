import os

po_dir = os.path.join("data", "po", "zh_CN", "LC_MESSAGES")
po_path = os.path.join(po_dir, "erArk.po")
mo_path = os.path.join(po_dir, "erArk.mo")
if os.path.exists(po_path):
    os.remove(po_path)
os.system('find ./ -name "*.py" >POTFILES && xgettext -n --files-from=POTFILES -o ' + po_path)
os.remove("POTFILES")
os.system("msgfmt " + po_path + " -o " + mo_path)
