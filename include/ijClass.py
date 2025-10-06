import imagej
import os
from scyjava import jimport
import json
# import scyjava
# scyjava.config.add_options('-Xmx6g')

# ij = imagej.init("C:/Users/NotEW/Desktop/Fiji")
# print(ij.getVersion())
# print(ij.getApp().getInfo(True))

class ImageJ():
    def __init__(self, dir, mode):
        self.ij = imagej.init(dir, mode)
        print(self.ij.getVersion())
        print(self.ij.getApp().getInfo(True))
    
    def exit(self):
        self.ij.IJ.run('Quit')
            
    def laskePesakeLuvut(self, img_list: list, setting: dict, imgDir: str, dataDir: str):
        ResultsTable = jimport('ij.measure.ResultsTable')
        OvalRoi = jimport('ij.gui.OvalRoi')
        ChannelSplitter = jimport('ij.plugin.ChannelSplitter')
        names = []
        names = []
        
        env = setting['env']
        addLightness = setting['preset'][env]['addlightness']
        setprominence = setting['preset'][env]['prominence']
        
        print(f'env = {env}, light = {addLightness}, prom = {setprominence}')
        # hard coded stuff
        # if preset['env'] == 'testtube':
        #     addLightness = 90
        # elif preset['env'] == 'bottle':
        #     addLightness = 105
        # elif preset['env'] == 'test tube in prototype':
        #     addLightness = 30
        # else:
        #     print("preset not avaliable")
        #     return None
        
        # if preset['env'] == 'bottle':
        #     setprominence = 90
        # else:
        #     setprominence = 65
        ep = 40
        
        for idx, imgPath in enumerate(img_list):
            imp = self.ij.IJ.openImage(imgPath)
            
            if not imp:
                print('somthing wrong with image')
                return
            
            name0 = imp.getTitle()
            print(idx, name0)
            dotIndex = str(name0).index('.')
            name = name0[:dotIndex]
            try:
                red, green, imp = ChannelSplitter.split(imp)
            except ValueError:
                print('Image don\'t have 3 channel')
            
            nameb = name0 + " (blue)"
            names.append(nameb)
            
            height = imp.getHeight()
            width = imp.getWidth()
            
            self.ij.IJ.run(imp, "Subtract Background...", "rolling=100 light")
            self.ij.IJ.run(imp, "Enhance Contrast...", "saturated=0.9 normalize")
            imp.setDisplayRange(100, 200)  # no change visually
            # imp.updateAndDraw()
            # ij.IJ.run(imp, "Apply LUT", "")
            self.ij.IJ.run(imp, "Median...", "radius=1")
            self.ij.IJ.run(imp, "Add...", f"value={addLightness}")
            
            # clear outer bg
            roi = OvalRoi(ep/2, ep/2, (width-ep), (height-(ep+10)))
            imp.setRoi(roi)
            self.ij.IJ.setBackgroundColor(255, 255, 255)
            self.ij.IJ.run(imp, "Clear Outside", "")
            
            # counting
            self.ij.IJ.run(imp, "Find Maxima...", f"prominence={setprominence} light output=Count")
            self.ij.IJ.run(imp, "Find Maxima...", f"prominence={setprominence} light output=[Point Selection]")
            imp = imp.flatten()
            
            dst = os.path.join(imgDir, f"{name}_point_selection.png")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            self.ij.IJ.saveAs(imp, 'png', dst)
            imp.close()
            
        # handle data
        self.ij.IJ.selectWindow('Results')
        rt = ResultsTable.getResultsTable()
        count = rt.size()

        results = []
        
        for i in range(count):
            x = rt.getValue("Count", i)
            result = {
                'row': i + 1,
                'count': int(x),
                'img': img_list[i]
            }
            results.append(result)

        # self.ij.IJ.run("Close", "Results")

        dst = os.path.join(dataDir, "data.json")
        with open(dst, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        
        self.ij.IJ.run("Close", "Results")
        return results

def main():
    os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
    lol = ImageJ("C:/Users/NotEW/Desktop/Fiji")
    img_list = []
    dst = os.path.join(os.path.dirname(__file__), 'temp', 'raw')
    for filename in os.listdir(dst):
        path = os.path.normpath(os.path.join(dst, filename))
        img_list.append(path)
        
    lol.setImgGrey8bit(img_list=img_list)
if __name__ == '__main__':
    main()
