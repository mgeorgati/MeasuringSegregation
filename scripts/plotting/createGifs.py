from pathlib import Path
import imageio,os
def createGIFs(src_path, export_path, fileName):
    """_summary_

    Args:
        src_path (_str_): Directory where png files are stored
        export_path (_type_): Directory where the exported gif is saved
        fileName (_type_): File name of gif
    """    
    
    filePaths=[]
    for file in os.listdir(src_path):
        if file.endswith('.png'):
            filePath = Path(src_path + "/" + file)
            filePaths.append(filePath)
    print(filePaths)
    images = []
    for i in filePaths:
        images.append(imageio.imread(i))
    imageio.mimsave(export_path + '/{}.gif'.format(fileName), images, fps=24, duration=1)
        
