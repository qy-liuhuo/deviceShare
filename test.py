keyNames = """
cmd:alt
alt_l:cmd
""".strip().split("\n")
keyNames = {i.split(":")[0]: i.split(":")[1] for i in keyNames}
print(keyNames)