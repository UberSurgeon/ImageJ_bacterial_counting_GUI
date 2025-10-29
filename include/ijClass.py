import imagej
import os
from scyjava import jimport
import json
import jpype
# import scyjava
# scyjava.config.add_options('-Xmx6g')

# ij = imagej.init("C:/Users/NotEW/Desktop/Fiji")
# print(ij.getVersion())
# print(ij.getApp().getInfo(True))

class ImageJ():
    def __init__(self, dir, mode):
        self.ij = imagej.init(dir, mode)
        # print(self.ij.getVersion())
        # print(self.ij.getApp().getInfo(True))
    
    def exit(self):
        print("Closing ImageJ...")
        self.ij.IJ.run('Quit')
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            
    def laskePesakeLuvut(self, img_list: list, setting: dict, imgDir: str, dataDir: str):
        
        print('AWIHEDAOWHDIAHU')
        ResultsTable = jimport('ij.measure.ResultsTable')
        OvalRoi = jimport('ij.gui.OvalRoi')
        ChannelSplitter = jimport('ij.plugin.ChannelSplitter')
        names = []
        names = []
        
        env = setting['env']
        addLightness = setting['preset'][env]['addlightness']
        setprominence = setting['preset'][env]['prominence']
        
        print(f'env = {env}, light = {addLightness}, prom = {setprominence}')
        # ep = 40
        ep = 80
        
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
            # roi = OvalRoi(ep/2, ep/2, (width-ep), (height-(ep+10)))
            roi = OvalRoi(ep/2 + 40, ep/2 + 45, (width-ep-70), (height-(ep+70)))
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
            # imp.close()
            
        # handle data
        self.ij.IJ.selectWindow('Results')
        rt = ResultsTable.getResultsTable()
        count = rt.size()

        results = []

        # Prepare lists for CSV
        filenames = []
        counts = []

        for i in range(count):
            cnt = int(rt.getValue("Count", i))
            img_name = img_list[i]  # same as ImageJ macro: "Filename"
            
            result = {
                'row': i + 1,
                'count': cnt,
                'img': img_name
            }
            results.append(result)
            
            filenames.append(img_name)
            counts.append(cnt)

        # Save as JSON (same as before)
        dst_json = os.path.join(dataDir, "data.json")
        with open(dst_json, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        # Save as CSV (same format as ImageJ macro)
        dst_csv = os.path.join(dataDir, "Kuvista_Lasketut_pesakeluvut.csv")
        with open(dst_csv, 'w', encoding='utf-8', newline='') as file:
            file.write("Filename,Count\n")
            for name, cnt in zip(filenames, counts):
                file.write(f"{name},{cnt}\n")

        # Close Results table
        self.ij.IJ.run("Close", "Results")

        return results
    
    def test(self, img_list: list, setting: dict, imgDir: str, dataDir: str):
        print('AWIHEDAOWHDIAHU')
        ResultsTable = jimport('ij.measure.ResultsTable')
        OvalRoi = jimport('ij.gui.OvalRoi')
        ChannelSplitter = jimport('ij.plugin.ChannelSplitter')
        names = []
        names = []
        
        env = setting['env']
        addLightness = setting['preset'][env]['addlightness']
        setprominence = setting['preset'][env]['prominence']
        
        print(f'env = {env}, light = {addLightness}, prom = {setprominence}')
        # ep = 40
        ep = 80
        
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
            print(height, width)
            self.ij.IJ.run(imp, "Subtract Background...", "rolling=100 light")
            self.ij.IJ.run(imp, "Enhance Contrast...", "saturated=0.9 normalize")
            imp.setDisplayRange(100, 200)  # no change visually
            # imp.updateAndDraw()
            # ij.IJ.run(imp, "Apply LUT", "")
            self.ij.IJ.run(imp, "Median...", "radius=1")
            self.ij.IJ.run(imp, "Add...", f"value={addLightness}")
            
            # roi = OvalRoi(ep/2, ep/2, (width-ep), (height-(ep+10)))
            roi = OvalRoi(ep/2, ep/2 + 5, (width-ep-10), (height-(ep+10)))
            imp.setRoi(roi)
            self.ij.IJ.setBackgroundColor(255, 255, 255)
            self.ij.IJ.run(imp, "Clear Outside", "")
            
            self.ij.IJ.run(imp, "Find Maxima...", f"prominence={setprominence} light output=Count")
            self.ij.IJ.run(imp, "Find Maxima...", f"prominence={setprominence} light output=[Point Selection]")
            imp = imp.flatten()
            
            dst = os.path.join(imgDir, f"{name}_point_selection.png")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            self.ij.IJ.saveAs(imp, 'png', dst)
            
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
            print(results)
            return results
        # self.ij.py.show(imp)
        # ResultsTable = jimport('ij.measure.ResultsTable')
        # OvalRoi = jimport('ij.gui.OvalRoi')
        # ChannelSplitter = jimport('ij.plugin.ChannelSplitter')
        # ep = 40
        # red, green, imp = ChannelSplitter.split(imp)
        # height = imp.getHeight()
        # width = imp.getWidth()
        # self.ij.IJ.run(imp, "Subtract Background...", "rolling=100 light")
        # self.ij.IJ.run(imp, "Enhance Contrast...", "saturated=0.9 normalize")
        # # imp.updateAndDraw()
        # # ij.IJ.run(imp, "Apply LUT", "")
        # self.ij.IJ.run(imp, "Median...", "radius=1")
        # self.ij.IJ.run(imp, "Add...", "value=90")
        # self.ij.ui().show(imp)
        # roi = OvalRoi(ep/2, ep/2, (width-ep), (height-(ep+10)))
        # imp.setRoi(roi)
        # self.ij.IJ.setBackgroundColor(255, 255, 255)
        # self.ij.IJ.run(imp, "Clear Outside", "")
        # self.ij.IJ.run(imp, "Find Maxima...", "prominence=65 light output=Count")
        # self.ij.IJ.run(imp, "Find Maxima...", "prominence=65 light output=[Point Selection]")
        # imp = imp.flatten()

        # self.ij.IJ.selectWindow('Results')
        # rt = ResultsTable.getResultsTable()
        # count = rt.size()

        # results = []

        # for i in range(count):
        #     x = rt.getValue("Count", i)
        #     result = {
        #         'row': i + 1,
        #         'count': int(x)
        #     }
        #     results.append(result)
        # print(results)

def main():
    setting = ''
    with open(r'C:\Users\NotEW\Documents\Code\roboai\gui\setting\setting.json', 'r') as file:
        setting = json.load(file)
            
    # init imageJ
    os.environ['JAVA_HOME'] = setting["JAVA_HOME"]
    # self.imageJ = ImageJ("C:/Users/NotEW/Desktop/Fiji", mode='interactive')
    imageJ = ImageJ(setting["fiji_dir"], mode='interactive')
    # laskePesakeLuvut(self, img_list: list, setting: dict, imgDir: str, dataDir: str)
    # os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
    # lol = ImageJ("C:/Users/NotEW/Desktop/Fiji", 'interactive')
    img_list = [r'C:\Users\NotEW\Documents\Code\roboai\gui\bac.png']
    # imageJ.test(img_list, setting, r'C:\Users\NotEW\Documents\Code\roboai\gui\waa', r'C:\Users\NotEW\Documents\Code\roboai\gui\waa')
    
    imageJ.laskePesakeLuvut(img_list, setting, r'C:\Users\NotEW\Documents\Code\roboai\gui\waa', r'C:\Users\NotEW\Documents\Code\roboai\gui\waa')
    uIn = input()
    imageJ.exit()
if __name__ == '__main__':
    main()
