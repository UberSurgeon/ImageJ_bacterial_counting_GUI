#%%
import imagej
import os
import scyjava as sj
from scyjava import jimport

os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
ij = imagej.init("C:/Users/NotEW/Desktop/Fiji", mode='interactive')
print(ij.getVersion())
print(ij.getApp().getInfo(True))

# %%
imp = ij.IJ.openImage(r'C:\Users\NotEW\Documents\Code\roboai\gui\bac.png')

# imp = ij.py.to_imageplus(dataset)
# ij.py.show(dataset, cmap='grey')
ij.py.show(imp)

#%%
ResultsTable = jimport('ij.measure.ResultsTable')
OvalRoi = jimport('ij.gui.OvalRoi')
ChannelSplitter = jimport('ij.plugin.ChannelSplitter')
ep = 40
red, green, imp = ChannelSplitter.split(imp)
height = imp.getHeight()
width = imp.getWidth()
ij.IJ.run(imp, "Subtract Background...", "rolling=100 light")
ij.IJ.run(imp, "Enhance Contrast...", "saturated=0.9 normalize")
# imp.updateAndDraw()
# ij.IJ.run(imp, "Apply LUT", "")
ij.IJ.run(imp, "Median...", "radius=1")
ij.IJ.run(imp, "Add...", "value=90")
ij.ui().show(imp)
roi = OvalRoi(ep/2, ep/2, (width-ep), (height-(ep+10)))
imp.setRoi(roi)
ij.IJ.setBackgroundColor(255, 255, 255)
ij.IJ.run(imp, "Clear Outside", "")
ij.IJ.run(imp, "Find Maxima...", "prominence=65 light output=Count")
ij.IJ.run(imp, "Find Maxima...", "prominence=65 light output=[Point Selection]")
imp = imp.flatten()

ij.IJ.selectWindow('Results')
rt = ResultsTable.getResultsTable()
count = rt.size()

results = []

for i in range(count):
    x = rt.getValue("Count", i)
    result = {
        'row': i + 1,
        'count': int(x)
    }
    results.append(result)
print(results)

# %%
