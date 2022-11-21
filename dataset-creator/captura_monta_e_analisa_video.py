import os

# Calls all other necessary files to do a full work of capturing, processing images and generate 3d skeleton with metrics
# The first two lines are only necessary when running video capture
# os.system("python capture-images.py -p1 -g1")
# os.system("python make-videos.py -p1 -g1")
os.system("python request-2d-skeletons.py -p1 -g1")
os.system("python request-3d-skeletons.py -p1 -g1")
os.system("python export-video-3d-medicoes-erros-no-3d.py -p1 -g1")
