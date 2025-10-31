# IJgui

IJgui is a graphical python based GUI app for **ImageJ/Fiji**, to used **Object Detection** and OCR-assisted workflows using **Ollama** and models such as `minicpm-v`.
It’s an application built to process raw microscope or lab photos — automatically cropping, reading sample labels with GPU acceleration, and using Fiji scripts to count and analyze bacterial colonies efficiently.

---

## Notable Technologies and Libraries

* **[Java 21 (LTS)](https://www.oracle.com/java/technologies/javase/jdk21-archive-downloads.html)** — stable runtime for modern features like pattern matching and virtual threads.
* **[Apache Maven 3.9.9](https://maven.apache.org/)** — dependency management and build tool.
* **[Ollama](https://ollama.ai)** — local model execution environment for running LLMs offline.
* **Model: [minicpm-v:latest](https://ollama.ai/library/minicpm-v)** — compact multimodal model used for embedded AI analysis.
* **[Fiji](https://imagej.net/software/fiji/)** — ImageJ distribution for image processing workflows.
* **Optional: [CUDA 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)** — GPU acceleration.
* Infastucture: **[tkinter](https://docs.python.org/3/library/tkinter.html)** (used for the GUI).
* **[PyInstaller](https://pypi.org/project/pyinstaller/)** — used to bundle Python applications into standalone executables.
* **[YOLOv7](https://github.com/WongKinYiu/yolov7)** — deep learning model for object detection, used here for detecting and cropping bacterial colonies dishes. 
* **[pyimagej](https://pypi.org/project/pyimagej/)** — Python interface to ImageJ for running Fiji scripts directly in Python.
* **[scyjava](https://pypi.org/project/scyjava/)** and *[JPype](https://pypi.org/project/jpype1/)** — Java-Python interoperability libraries used to bridge ImageJ and Python environments.

---

## Installation Guide (Windows)

### 1. Install Java

Download and install **Java 21**:
[https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe](https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe)

---

### 2. Install Maven

Install **Maven 3.9.9**:
[https://dlcdn.apache.org/maven/mvnd/1.0.3/maven-mvnd-1.0.3-windows-amd64.zip](https://dlcdn.apache.org/maven/mvnd/1.0.3/maven-mvnd-1.0.3-windows-amd64.zip)

Extract the ZIP file to a location such as:

```
C:\ProgramData\chocolatey\lib\maven\
```

Then add `maven\bin` to your **PATH** environment variable.

---

### 3. Install and Run Ollama

#### Step 3.1 — Download Ollama

Go to [https://ollama.ai](https://ollama.ai) and download the Windows installer.

#### Step 3.2 — Install the Model

Once Ollama is installed

1. Click the **Start** button in the bottom-left corner of your screen  
   (the Windows logo made of four small white squares).

2. Type **PowerShell** in the search bar.

3. You should see an icon labeled **Windows PowerShell**

4. **Right-click** on “Windows PowerShell” and choose  
**Run as administrator.**

5. Click inside the blue PowerShell window.

6. Copy and paste the following command:

```
ollama pull minicpm-v:latest
```

7. Press **Enter** on your keyboard.

This may take a few minutes depending on your internet speed. 


#### Step 3.3 — Start Ollama

Run Ollama as a background service:

Copy and paste the following command:

```
ollama run minicpm-v:latest
```

Keep this running while you use IJgui. The first startup will download the model and may take several minutes.

---

### 4. (Optional) Install CUDA

For GPU acceleration, install **CUDA 11.8**:
[https://developer.nvidia.com/cuda-11-8-0-download-archive](https://developer.nvidia.com/cuda-11-8-0-download-archive)

---

### 5. Install Fiji

Download Fiji (ImageJ distribution):
[https://imagej.net/software/fiji/downloads](https://imagej.net/software/fiji/downloads)

---

### 6. Install IJgui

Download the latest release of **IJgui** from:
[Releases](https://github.com/UberSurgeon/ImageJ_bacterial_counting_GUI/releases)

Extract the files and locate `IJgui.exe` in the root folder.

---

### 7. Run IJgui

1. Launch **IJgui.exe**.
2. In the pre-launch window:

   * Click **“Change JAVA_HOME”** and select your Java directory.
     If you installed the recommended Java, it should be:

     ```
     C:/Program Files/Java/jdk-21
     ```
   * Click **“Change fiji_dir”** and select your Fiji installation directory (e.g., `C:/.../Fiji`).
3. Check the console output below for:

   * GPU availability
   * Ollama detection
   * Python environment checks
   * Maven and Java validation

Example output:

```
Checking Maven:
--> Maven executable = C:\ProgramData\chocolatey\lib\maven\apache-maven-3.9.9\bin\mvn.CMD
$ mvn -v
Apache Maven 3.9.9
Java version: 24.0.1
```

If Maven is found, click **“Yes”** to proceed.
The first run may take time to initialize dependencies.
If errors occur, open `app.log` and troubleshoot from there.
