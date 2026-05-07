from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('webdriver_manager')

# Collect data files (if any)
datas = collect_data_files('webdriver_manager')

# For chromedriver, we need to bundle it
# But since it's downloaded at runtime, we can pre-download it during build
# For now, assume it's handled by the code