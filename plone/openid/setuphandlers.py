from plone.openid.upgrades import update_bbb_attributes


def importVarious(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone_openid-default.txt') is None:
        return

    update_bbb_attributes(context)
