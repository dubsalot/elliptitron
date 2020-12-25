const { app, BrowserWindow } = require('electron')

function createWindow () {
  const win = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      nodeIntegration: true
    }, 
    fullscreen: true
  })

  //win.loadFile('gauge/gauge.html')
  win.loadFile('proto/proto.html')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  BrowserWindow.setFullScreen(true);
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})