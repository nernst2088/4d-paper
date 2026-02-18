from src.core.i18n.translator import translator, _

# Test default language
print('Default language:', translator.current_language)
print('English:', _('Welcome to 4D-Paper API'))

# Test Chinese
print('\nSetting language to Chinese...')
translator.set_language('zh')
print('Chinese:', _('Welcome to 4D-Paper API'))
print('Chinese (Dynamic Paper ID):', _('Dynamic Paper ID'))

# Test French
print('\nSetting language to French...')
translator.set_language('fr')
print('French:', _('Welcome to 4D-Paper API'))
print('French (Version):', _('Version'))

# Test Spanish
print('\nSetting language to Spanish...')
translator.set_language('es')
print('Spanish:', _('Welcome to 4D-Paper API'))
print('Spanish (Research Purpose):', _('Research Purpose'))

print('\nTranslation test completed successfully!')
