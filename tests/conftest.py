import os

# Run Qt without a display, so UI tests don't open windows and work in CI.
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
