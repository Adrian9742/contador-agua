const { BrowserWindow, app } = require('electron')
const path = require('path')
const fs = require('fs')

const isDev = process.env.NODE_ENV === 'development'

function createWindow() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.ico')

  const win = new BrowserWindow({
    width: 460,
    height: 870,
    minWidth: 460,
    minHeight: 700,
    resizable: false,
    maximizable: false,
    title: 'Contador de Água',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    backgroundColor: '#0d1424',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    win.loadURL('http://localhost:3000')
    win.webContents.openDevTools({ mode: 'detach' })
  } else {
    win.loadFile(path.join(__dirname, '..', 'out', 'index.html'))
  }

  win.on('close', (e) => {
    if (!app.isQuitting) {
      e.preventDefault()
      win.hide()
    }
  })

  return win
}

module.exports = { createWindow }
