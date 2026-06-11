const { Tray, Menu } = require('electron')
const path = require('path')
const fs = require('fs')

let tray = null

function createTray(win) {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.ico')
  const fallback = path.join(__dirname, '..', 'public', 'icon.svg')
  const icon = fs.existsSync(iconPath) ? iconPath : fallback

  try {
    tray = new Tray(icon)
  } catch {
    return
  }

  const menu = Menu.buildFromTemplate([
    {
      label: 'Abrir Contador de Água',
      click: () => { win.show(); win.focus() },
    },
    { type: 'separator' },
    {
      label: 'Sair',
      click: () => {
        const { app } = require('electron')
        app.isQuitting = true
        app.quit()
      },
    },
  ])

  tray.setToolTip('Contador de Água')
  tray.setContextMenu(menu)
  tray.on('click', () => { win.show(); win.focus() })
}

module.exports = { createTray }
